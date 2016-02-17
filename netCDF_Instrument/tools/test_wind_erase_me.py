'''
Created on Feb 10, 2016

@author: chogg
'''
from NetCDF_Utils import nc
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def get_second_coordinate(x1, y1, xorigin, yorigin, angle):
    
    newx = (x1 - xorigin)* np.cos(angle * np.pi / 180)
    newy = (y1 - yorigin)* np.sin(angle * np.pi / 180)
    return (newx,newy)

def wind_plot(file_name):
#     time = nc.get_variable_data(file_name, 'time')
#     wind_speed = nc.get_variable_data(file_name, 'wind_speed')
#     wind_direction = nc.get_variable_data(file_name, 'wind_direction')

    df = pd.read_csv(file_name, header=None)
    time = df[2]
    wind_direction = df[6]
    wind_speed = df[8]
    print('len', len(time))
    
    for x in range(0,len(time[0:50])):
        point1 = [x,0]
#         wind_speed[x] = 3
        point2 = [x,wind_speed[x]]
        
        diff = point2[1]
        
        #directly proportional to the x limits, need a couple of data sets to get magic number
        xscale = 300 #((len(time) + (2*np.max(wind_speed)))) /10
         
        
        #degrees from north clockwise (north is zero, east is 90)
        direction = 360 - wind_direction[x] + 90
        if direction >= 360:
            direction -= 360
            
        #calculate 2nd point based on direction
        point2[1] = get_second_coordinate(point2[1],point1[1],direction)
        if direction <= 90:
            pointpoint2[1] = get_second_coordinate(point2[1],point1[1],direction)
            point2[0] = point2[0] + ((diff - point2[1]) * xscale)
          
        elif direction > 90 and direction <= 180:
            point2[1] = get_second_coordinate(point2[1],point1[1],direction)
            point2[0] = point2[0] - ((diff - point2[1]) * xscale)
            
        elif direction > 180 and direction <= 270:
            direction2 = 180 - (direction - 180)
            point2[1] = get_second_coordinate(point2[1],point1[1],direction2) 
            point2[0] = point2[0] - ((diff + point2[1]) * xscale)
          
        else: 
            direction2 = 180 - (direction - 180)
            point2[1] = get_second_coordinate(point2[1],point1[1],direction2) 
            point2[0] = point2[0] + ((diff + point2[1]) * xscale)
         
        print(x,': ', wind_direction[x],wind_speed[x], point1[0],point2[0],point1[1],point2[1])
        plt.plot([point1[0],point2[0]],[point1[1],point2[1]], color='blue', alpha=.25)
   
    
#     plt.ylim([-5,5])
    plt.show()
    
if __name__ == '__main__':
    wind_plot('wind_data.csv')
        
    