from logging.config import listen
import signal
import itertools

# Exit program on CTRL+C
signal.signal(signal.SIGINT, lambda sig, frame: exit())

import rospy
from cv_bridge import CvBridge

# ROS messages
from piksi_rtk_msgs.msg import BaselineHeading, PosLlh
from sensor_msgs.msg import NavSatFix, Image, CompressedImage, CameraInfo
from geometry_msgs.msg import PoseWithCovarianceStamped

import pymap3d as pm
import pandas as pd
import numpy as np
from scipy.spatial.transform import Rotation
from scipy.interpolate import interp1d
import cv2

# Custom topic listener class
from src.listener import Listener


def transform_geo_to_xyz(objpt_coords, origin_coords, tf_mtx, r_mtx):
    n, e, d = pm.geodetic2ned(*objpt_coords, *origin_coords)

    # Rotate axes to align with vehicle heading (z is forward, x is right, y is down)
    ned = np.array([[n], [e], [d]])
    # Switch coordinate axes
    xyz = np.matmul(tf_mtx, ned)
    # Rotate coordinate frame
    xyz = np.matmul(r_mtx, xyz)

    x, y, z = (float(dim) for dim in xyz)

    # Translate target point to new origin at camera
    x -= x0
    y -= y0
    z -= z0

    return [x, y, z]


def pairwise(iterable):
    "s -> (s0, s1), (s1, s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def interpolate_lane(df):
    NUM_POINTS = 500
    df = df.sort_values("Y", ascending=False)  # Put in order by latitude
    x, y, z = df["Y"], df["X"], df["Z"]
    # Linear length on the line
    distance = np.sqrt(np.ediff1d(x, to_begin=0) ** 2 + np.ediff1d(y, to_begin=0) ** 2)
    distance = np.cumsum(distance)
    distance /= distance[-1]  # normalize interpolator input to [0,1]
    # Create interpolators
    fx = interp1d(distance, x, kind="cubic")  # Latitude cubic spline interpolator
    fy = interp1d(distance, y, kind="cubic")  # Longitude cubic spline interpolator
    fz = interp1d(distance, z, kind="cubic")  # Altitude cubic spline interpolator
    # Interpolate
    i = np.linspace(0, 1, NUM_POINTS)
    lat, lon, alt = fx(i), fy(i), fz(i)
    interpolated_points = list(zip(fx(i), fy(i), fz(i)))
    return interpolated_points


def loop():
    # Initialize message variables for first comparison
    leftcam_info_msg = None
    leftcam_msg = None
    baseline_heading_msg = None
    navsatfix_best_fix_msg = None
    zedpose_msg = None
    posllh_msg = None
    while True:
        # Wait until at least one topic is updated
        while (
            (leftcam_info.msg == leftcam_info_msg)
            and (leftcam.msg == leftcam_msg)
            and (baseline_heading.msg == baseline_heading_msg)
            and (navsatfix_best_fix.msg == navsatfix_best_fix_msg)
            and (zedpose.msg == zedpose_msg)
            and (posllh.msg == posllh_msg)
        ):
            continue
        # Copy messages to variables (prevents mixing message fields)
        leftcam_info_msg = leftcam_info.msg
        leftcam_msg = leftcam.msg
        baseline_heading_msg = baseline_heading.msg
        navsatfix_best_fix_msg = navsatfix_best_fix.msg
        zedpose_msg = zedpose.msg
        posllh_msg = posllh.msg

        # Base station coordinates
        sensor_lat = navsatfix_best_fix_msg.latitude
        sensor_lng = navsatfix_best_fix_msg.longitude
        sensor_alt = navsatfix_best_fix_msg.altitude
        basestation_coords = [sensor_lat, sensor_lng, sensor_alt]

        # Build rotation matrix from heading to NED
        heading = baseline_heading_msg.heading / 1000
        heading_adjustment = 4  # degrees to the right
        heading += heading_adjustment
        # TODO: why negative heading?
        yaw_rotation = Rotation.from_euler("y", -heading, degrees=True)
        # Or, expressed in separate equations:
        # x = -n*sin(heading) + e*cos(heading)
        # y = d
        # z = n*cos(heading) + e*sin(heading)

        # Manual pitch adjustment
        pitch = -2.7  # degrees up
        pitch_rotation = Rotation.from_euler("x", pitch, degrees=True)

        # Manual roll adjustment
        roll = 0  # degrees clockwise
        roll_rotation = Rotation.from_euler("z", -roll, degrees=True)

        # Rotation from ZED pose
        x = zedpose_msg.pose.pose.orientation.x
        y = zedpose_msg.pose.pose.orientation.y
        z = zedpose_msg.pose.pose.orientation.z
        w = zedpose_msg.pose.pose.orientation.w
        q = Rotation.from_quat([x, y, z, w])

        # Intrinsic camera parameters
        camera_matrix = np.reshape(leftcam_info_msg.K, (3, 3))
        distortion_coeffs = np.array(leftcam_info_msg.D)

        # rotation_mtx = (yaw_rotation * q).as_matrix()
        # rotation_mtx = (yaw_rotation * pitch_rotation * q).as_matrix()
        rotation_mtx = (roll_rotation * pitch_rotation * yaw_rotation).as_matrix()

        # Transformation matrix from to NED coordinates to OpenCV coordinates
        transformation_mtx = np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]])
        # Or, expressed in separate equations:
        # x = e
        # y = d
        # z = n

        # Populate list of left lane object points
        leftpts = [
            transform_geo_to_xyz(
                leftpt_coords, basestation_coords, transformation_mtx, rotation_mtx
            )
            for leftpt_coords in leftpts_coords
        ]
        leftpts = list(filter(lambda pt: (pt[2] > 0), leftpts))
        # Populate list of right lane object points
        rightpts = [
            transform_geo_to_xyz(
                rightpt_coords, basestation_coords, transformation_mtx, rotation_mtx
            )
            for rightpt_coords in rightpts_coords
        ]
        rightpts = list(filter(lambda pt: (pt[2] > 0), rightpts))

        # Calculate object point distances
        leftdistances = [np.linalg.norm(objpt) for objpt in leftpts]
        rightdistances = [np.linalg.norm(objpt) for objpt in rightpts]

        # Remove left points beyond distance threshold
        leftpts_to_remove = [
            i
            for i, distance in enumerate(leftdistances)
            if distance > DISTANCE_THRESHOLD
        ]
        leftpts = [
            leftpt for i, leftpt in enumerate(leftpts) if i not in leftpts_to_remove
        ]
        leftdistances = [
            leftdistance
            for i, leftdistance in enumerate(leftdistances)
            if i not in leftpts_to_remove
        ]
        # Remove right points beyond distance threshold
        rightpts_to_remove = [
            i
            for i, distance in enumerate(rightdistances)
            if distance > DISTANCE_THRESHOLD
        ]
        rightpts = [
            rightpt for i, rightpt in enumerate(rightpts) if i not in rightpts_to_remove
        ]

        rightdistances = [
            rightdistance
            for i, rightdistance in enumerate(rightdistances)
            if i not in rightpts_to_remove
        ]

        # Read image
        img = cvbridge.imgmsg_to_cv2(leftcam_msg)
        # img = cvbridge.compressed_imgmsg_to_cv2(leftcam_msg)

        mask = np.zeros_like(img)
        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)

        # Draw right lane line
        if len(rightpts) > 0:
            # Calculate image points using already transformed object points
            proj, _ = cv2.projectPoints(
                np.array(rightpts), rvec, tvec, camera_matrix, distortion_coeffs
            )
            rightimgpts = [(round(imgpt[0][0]), round(imgpt[0][1])) for imgpt in proj]
            rightimgpts_arr = np.array(rightimgpts, dtype=np.int32)
            img = cv2.polylines(
                img, [rightimgpts_arr], isClosed=False, color=(0, 255, 0), thickness=3
            )
            mask = cv2.polylines(
                mask, [rightimgpts_arr], isClosed=False, color=255, thickness=3
            )
        # Draw left lane line
        if len(leftpts) > 0:
            # Calculate image points using already transformed object points
            proj, _ = cv2.projectPoints(
                np.array(leftpts), rvec, tvec, camera_matrix, distortion_coeffs
            )
            leftimgpts = [(round(imgpt[0][0]), round(imgpt[0][1])) for imgpt in proj]
            leftimgpts_arr = np.array(leftimgpts, dtype=np.int32)
            img = cv2.polylines(
                img, [leftimgpts_arr], isClosed=False, color=(0, 0, 255), thickness=3
            )
            mask = cv2.polylines(
                mask, [leftimgpts_arr], isClosed=False, color=255, thickness=3
            )
        # Shade driveable region
        if len(leftpts) > 0 and len(rightpts) > 0:
            pts = np.array(leftimgpts + [e for e in reversed(rightimgpts)])
            mask = cv2.fillConvexPoly(mask, pts, color=255)
            roi = img.copy()
            roi[mask.nonzero()] = [255, 0, 0]  # blue
            alpha = 0.25  # 25% opacity
            img = cv2.addWeighted(img, 1, roi, alpha, 0)

        fix_binary = bin(posllh_msg.flags)[-3:]
        fix_decimal = int(fix_binary, 2)
        fix_mode = FIX_MODES[fix_decimal]
        message = "MODE: " + fix_mode
        img = cv2.putText(
            img,
            message,
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 0),
            2,
        )

        message = "H_ACC: " + str(posllh_msg.h_accuracy / 10) + " cm"
        img = cv2.putText(
            img,
            message,
            (20, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 0),
            2,
        )
        message = "V_ACC: " + str(posllh_msg.v_accuracy / 10) + " cm"
        img = cv2.putText(
            img,
            message,
            (20, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 0),
            2,
        )

        # Show image
        cv2.imshow("img", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    # Initialize anonymous ROS node
    rospy.init_node("custom", anonymous=True)

    # Initialize topic listeners
    listeners = []
    # Left camera information listener
    leftcam_info = Listener("/zed2i/zed_node/left/camera_info", CameraInfo)
    listeners.append(leftcam_info)
    # Left camera image listener
    """leftcam = Listener(
        "/zed2i/zed_node/left_raw/image_raw_color/compressed", CompressedImage
    )"""
    leftcam = Listener("/zed2i/zed_node/left/image_rect_color", Image)
    listeners.append(leftcam)
    # Vehicle heading listener
    baseline_heading = Listener("/piksi/baseline_heading", BaselineHeading)
    listeners.append(baseline_heading)
    # NavSatFix listener
    navsatfix_best_fix = Listener(
        "/piksi_multi_base_station/navsatfix_best_fix", NavSatFix
    )
    listeners.append(navsatfix_best_fix)
    # Zed Pose
    zedpose = Listener(
        "/zed2i/zed_node/pose_with_covariance", PoseWithCovarianceStamped
    )
    listeners.append(zedpose)
    # Pos LLH
    posllh = Listener("/piksi_multi_base_station/pos_llh", PosLlh)
    listeners.append(posllh)

    # Wait for every listener to receive a message
    for listener in listeners:
        print(f"Waiting for listener: {listener.topic}")
        while not listener.ready:
            continue
        print(f"Ready.")

    # Read left lane line coordinates
    leftpts_coords = []
    left_df = pd.read_csv("left.csv")
    leftpts_coords = interpolate_lane(left_df)
    # Read right lane line coordinates
    rightpts_coords = []
    right_df = pd.read_csv("right.csv")
    rightpts_coords = interpolate_lane(right_df)

    # Translation from GNSS base station to camera
    x0 = 0  # meters right
    y0 = 0.7  # meters down
    z0 = 1.8  # meters forward

    # Translation of Trimble Catalyst pole
    y0 -= 2.05  # meters

    # Empty rotation and translation vectors
    # Transformation is handled manually so these aren't useful
    rvec = tvec = np.array([0.0, 0.0, 0.0])

    # Start CV Bridge
    cvbridge = CvBridge()

    # Size of projected point
    PTSIZE = 50

    # Distance beyond which to not draw lane lines
    DISTANCE_THRESHOLD = 250  # meters

    # FIX MODES
    FIX_MODES = [
        "Invalid",
        "SPP",
        "DGNSS",
        "Float RTK",
        "Fixed RTK",
        "Dead Reckoning",
        "SBAS Position",
    ]

    # Loop
    print("Beginning loop...")
    loop()
