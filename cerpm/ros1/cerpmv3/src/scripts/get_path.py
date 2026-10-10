#!/usr/bin/env python3

import numpy as np 
import pandas as pd 
from cerpm_data.msg import cerpm_receiver
import os 
from scipy.interpolate import interp1d, CubicSpline
import matplotlib.pyplot as plt 
import plotly.express as px 
import pymap3d as p3d
import math 
import time
import subprocess 

subprocess.call(['python3','/home/parth/catkin_ws/src/cerpmv3/src/scripts/get_cerpms.py'])

cerpm_df = pd.read_csv('/home/parth/catkin_ws/src/cerpmv3/src/scripts/saved_cerps.csv', index_col=False)
gps_points_df = pd.read_csv('/home/parth/Desktop/old_bethel1.csv',names=['lat', 'lon', 'alt', 'yaw', 'speed']) #might need to flip for older version

def seperate(df):

    """
    Takes in the dataframe and seperates into right and left df
    also appends the points to right and left lists 

    input -> dataframe for all cerpms 
    output -> tuple[right_df, left_df, rightpts, leftpts]

    """
    rightpts_coords = []
    leftpts_coords = []

    right_df = df[df["id"] % 2 != 0]
    left_df = df[df["id"] % 2 == 0]

    left_df = left_df.sort_values("lat", ascending=True) # sort by latitude

    for i, row in right_df.iterrows():

        rightpts_coords.append(
            [row["lat"], row["lon"], row["alt"]]
            )
        
    for i, row in left_df.iterrows():

        leftpts_coords.append(
            [row["lat"], row["lon"], row["alt"]]
            )

    return right_df, left_df, rightpts_coords, leftpts_coords
        
right_df, left_df, rightpts_coords, leftpts_coords = seperate(cerpm_df)

print("SEPERATED INTO LEFT AND RIGHT POINTS")

def interpolate_lane(df, NUM_POINTS : int = 20, type = "linear"):
    
    df = df.sort_values("lat", ascending=False)  # Put in order by latitude
    x, y, z = df["lat"], df["lon"], df["alt"]
    # Linear length on the line
    distance = np.sqrt(
        np.ediff1d(x, to_begin=0) ** 2
        + np.ediff1d(y, to_begin=0) ** 2
    )
    distance = np.cumsum(distance)
    distance /= distance[-1]  # normalize interpolator input to [0,1]
    # Create interpolators
    fx = interp1d(distance, x, kind=type)  # Latitude cubic spline interpolator
    fy = interp1d(distance, y, kind=type)  # Longitude cubic spline interpolator
    fz = interp1d(distance, z, kind=type)  # Altitude cubic spline interpolator
    # Interpolate
    i = np.linspace(0, 1, NUM_POINTS)
    interpolated_points = list(zip(fx(i), fy(i), fz(i)))
        
    return interpolated_points

# # change this to cubic when more than 3 cerpms

right_interp = interpolate_lane(right_df, 100, 'cubic')
right_inter_df = pd.DataFrame( { "lat" : [i[0] for i in right_interp], "lon": [i[1] for i in right_interp], "alt" : [i[2] for i in right_interp]} )

left_interp = interpolate_lane(left_df, 100, 'cubic')
left_inter_df = pd.DataFrame( { "lat" : [i[0] for i in left_interp], "lon": [i[1] for i in left_interp], "alt" : [i[2] for i in left_interp]} )

cent_interp_df = pd.DataFrame( { "lat" : [(rows1["lat"] + rows2["lat"])/2.0 for (idx1,rows1), (idx2,rows2) in zip(left_inter_df.iterrows(), right_inter_df.iterrows())], 
                                "lon" : [(rows1["lon"] + rows2["lon"])/2.0 for (idx1,rows1), (idx2,rows2) in zip(left_inter_df.iterrows(), right_inter_df.iterrows())], 
                                "alt" : [(rows1["alt"] + rows2["alt"])/2.0 for (idx1,rows1), (idx2,rows2) in zip(left_inter_df.iterrows(), right_inter_df.iterrows())]} )

right_inter_df = right_inter_df.iloc[::-1]
cent_interp_df = cent_interp_df.iloc[::-1]
left_inter_df = left_inter_df.iloc[::-1]

print("INTERPOLATED, AND GOT THE CENTER WAYPOINTS")

heading_calc = []

right_inter_df.to_csv('right_interpolated.csv',header=False)
left_inter_df.to_csv('left_interpolated.csv',header=False)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in km
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat/2) * np.sin(dlat/2) + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2) * np.sin(dlon/2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    distance = R * c * 1000
    return distance

def find_nearest_heading(df,lat, lon):
    min_distance = 0.3
    nearest_heading = None
    for idx, row in df.iterrows():
        distance = haversine(lat, lon, row['lat'], row['lon'])
        if distance < min_distance:
            # print(row['lat'],row['lon'])
            min_distance = distance
            nearest_heading = row['yaw']
    return nearest_heading

cent_interp_df['heading'] = cent_interp_df.apply(lambda row: find_nearest_heading(gps_points_df,row['lat'], row['lon']), axis=1)

print("GOT HEADING FOR THE CENTER WAYPOINTS")

# save the center_interpolated_dataframe with heading into a csv 
cent_interp_df.to_csv('cerpm_waypoints_v10.csv', header=False)

print('SAVED CSV WITH CENTER WAYPOINTS AND HEADING')
time.sleep(1)

print("OPENING WAYPOINTS PATH TO BE FOLLOWED IN A NEW WINDOW.......")
# time.sleep(1)

fig = px.scatter_mapbox(cent_interp_df, lat="lat", lon="lon", 
                        zoom=16, mapbox_style="open-street-map",
                        width=900,height=900)

fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig.show()