'''
Created on Feb 11, 2016

@author: chogg
'''
import numpy as np
import matplotlib.image as image
from matplotlib.image import BboxImage
from matplotlib.transforms import Bbox

# def plot_wind_data(ax, so, time_nums):
#     print('this is the length of time for wind',len(so.wind_time))
#     #i need to go home _-_
#     for x in range(0,len(time_nums)):
#             point1 = [time_nums[x],0]
#     #         wind_speed[x] = 3
#             point2 = [time_nums[x],so.wind_speed[x]]
#             
#             diff = point2[1]
#             
#             #directly proportional to the x limits, need a couple of data sets to get magic number
#             xscale = 300 #((len(time) + (2*np.max(wind_speed)))) /10
#              
#             
#             #degrees from north clockwise (north is zero, east is 90)
#             direction = 360 - so.wind_direction[x] + 90
#             if direction >= 360:
#                 direction -= 360
#                 
#             #calculate 2nd point based on direction
#             point2[1] = get_second_coordinate(point2[1],point1[1],direction)
#             if direction <= 90:
#                 point2[1] = get_second_coordinate(point2[1],point1[1],direction)
#                 point2[0] = point2[0] + ((diff - point2[1]) * xscale)
#               
#             elif direction > 90 and direction <= 180:
#                 point2[1] = get_second_coordinate(point2[1],point1[1],direction)
#                 point2[0] = point2[0] - ((diff - point2[1]) * xscale)
#                 
#             elif direction > 180 and direction <= 270:
#                 direction2 = 180 - (direction - 180)
#                 point2[1] = get_second_coordinate(point2[1],point1[1],direction2) 
#                 point2[0] = point2[0] - ((diff + point2[1]) * xscale)
#               
#             else: 
#                 direction2 = 180 - (direction - 180)
#                 point2[1] = get_second_coordinate(point2[1],point1[1],direction2) 
#                 point2[0] = point2[0] + ((diff + point2[1]) * xscale)
#              
# #             print(x,': ', wind_direction[x],wind_speed[x], point1[0],point2[0],point1[1],point2[1])
#             ax.plot([point1[0],point2[0]],[point1[1],point2[1]], color='blue', alpha=.25)
            
def plot_wind_data2(ax, so, time_nums):

    so.wind_speed = np.array(so.wind_speed)
    wind_speed_max = np.nanmax(so.wind_speed)
    print('max speed', wind_speed_max, len(so.wind_speed))
    
    logo = image.imread('north.png', None)
    bbox2 = Bbox.from_bounds(210, 330, 30, 40)
#     trans_bbox2 = bbox2.transformed(ax.transData)
    bbox_image2 = BboxImage(bbox2)
    bbox_image2.set_data(logo)
    ax.add_image(bbox_image2)
    
#     for x in range(0,len(time_nums),100):
    U = so.u
    V = so.v
    
           
#          if x == max_index:
    Q = ax.quiver(time_nums, -.15, U, V, headlength=0, 
              headwidth=0, headaxislength=0, alpha=1, color='#045a8d', width=.0015, scale=wind_speed_max*5)
    ax.quiverkey(Q, 0.44, 0.84, wind_speed_max * .6,labelpos='N',label = '                                    0 mph                      %.2f mph' % wind_speed_max,
#                    fontproperties={'weight': 'bold'}
       )
#             else:
#                 ax.quiver(time_nums[x], -.15, 0,1, headlength=0, 
#                           headwidth=0, headaxislength=0, alpha=.3, color='#045a8d', width=.0030)
            
def get_second_coordinate(y1, yorigin, angle):
    
    newy = (y1 - yorigin) * np.sin(angle * np.pi / 180)
    return newy