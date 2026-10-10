import numpy as np
import pandas as pd 
import plotly.express as px 
import matplotlib.pyplot as plt
import pymap3d as p3d 
import argparse

parser = argparse.ArgumentParser(description='Resample points based on the Tx seperation')
parser.add_argument('-d', '--sep', default=40)

args = parser.parse_args()

gps_points = pd.read_csv('/home/parth/Desktop/egcr1.csv',names=['lat', 'lon', 'alt', 'yaw', 'speed'])

lat0 = gps_points['lat'][0]
lon0 = gps_points['lon'][0]
alt0 = gps_points['alt'][0]

distance = 3.38/2.0 # meters

resampled_right = []
resampled_left = []
heading = []

sep_dist = float(args.sep) * 0.3048

print(sep_dist)

for index, row in gps_points.iterrows():

    x_local, y_local, z_local = p3d.geodetic2ned(row['lat'], row['lon'], row['alt'], lat0, lon0, alt0)
    
    offset_x = distance * np.cos(row['yaw'])
    offset_y = distance * np.sin(row['yaw'])
    
    projected_left_x = x_local + offset_y
    projected_left_y = y_local - offset_x
    
    projected_right_x = x_local - offset_y
    projected_right_y = y_local + offset_x
    
    yaw = row['yaw']
    
    if index == 0:
        x_ini_r = projected_right_x
        y_ini_r = projected_right_y
        
        right_lat, right_lon, right_alt = p3d.ned2geodetic(x_ini_r, y_ini_r, z_local, lat0, lon0, alt0)
        
        x_ini_l = projected_left_x
        y_ini_l = projected_left_y
        
        left_lat, left_lon, left_alt = p3d.ned2geodetic(y_ini_r, y_ini_l, z_local, lat0, lon0, alt0)
        
        resampled_right.append([right_lat, right_lon, right_alt])
        resampled_left.append([left_lat, left_lon, left_alt])
        heading.append([yaw])
    
    if np.sqrt( ( projected_right_x - x_ini_r )**2 + ( projected_right_y - y_ini_r )**2 ) >= sep_dist:
        
        right_lat, right_lon, right_alt = p3d.ned2geodetic(projected_right_x, projected_right_y, z_local, lat0, lon0, alt0)
        resampled_right.append([right_lat, right_lon, right_alt])
        
        left_lat, left_lon, left_alt = p3d.ned2geodetic(projected_left_x, projected_left_y, z_local, lat0, lon0, alt0)
        resampled_left.append([left_lat, left_lon, left_alt])
        
        heading.append([yaw])
        
        x_ini_r = projected_right_x
        y_ini_r = projected_right_y
        
        x_ini_l = projected_left_x
        y_ini_l = projected_left_y

right_resampled = np.array(resampled_right)
left_resampled = np.array(resampled_left)
heading_resampled = np.array(heading)

right_resampled_df = pd.DataFrame(right_resampled, columns=['right_lat', 'right_lon','right_alt'])
left_resampled_df = pd.DataFrame(left_resampled, columns=['left_lat', 'left_lon','left_alt'])
heading_resampled_df = pd.DataFrame(heading_resampled, columns=['heading'])

resampled_df = pd.concat([left_resampled_df,right_resampled_df,heading_resampled_df], axis=1)

resampled_df['right_id'] = 1
resampled_df['left_id'] = 2

ct_r = 101 # set to 1 default
ct_l = 100 # set to 2 default

for i,rows in resampled_df.iterrows():
    
    resampled_df['right_id'].loc[i] = ct_r
    resampled_df['left_id'].loc[i] = ct_l 
    
    ct_l += 2
    ct_r += 2
    
resampled_df.to_csv(f'/home/parth/catkin_ws/src/cerpmv3/src/scripts/resampled_pts_egcr{int(args.sep)}.csv', columns=['left_lat', 'left_lon','left_alt','right_lat', 'right_lon','right_alt','heading','right_id','left_id'])
