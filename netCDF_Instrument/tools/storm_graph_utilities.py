'''
Created on Feb 11, 2016

@author: chogg
'''
import numpy as np

def plot_wind_data(ax, so, time_nums):
    print('this is the length of time for wind',len(so.wind_time))
    #i need to go home _-_
    for x in range(0,len(time_nums)):
            point1 = [time_nums[x],0]
    #         wind_speed[x] = 3
            point2 = [time_nums[x],so.wind_speed[x]]
            
            diff = point2[1]
            
            #directly proportional to the x limits, need a couple of data sets to get magic number
            xscale = 300 #((len(time) + (2*np.max(wind_speed)))) /10
             
            
            #degrees from north clockwise (north is zero, east is 90)
            direction = 360 - so.wind_direction[x] + 90
            if direction >= 360:
                direction -= 360
                
            #calculate 2nd point based on direction
            point2[1] = get_second_coordinate(point2[1],point1[1],direction)
            if direction <= 90:
                point2[1] = get_second_coordinate(point2[1],point1[1],direction)
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
             
#             print(x,': ', wind_direction[x],wind_speed[x], point1[0],point2[0],point1[1],point2[1])
            ax.plot([point1[0],point2[0]],[point1[1],point2[1]], color='blue', alpha=.25)
            
def plot_wind_data2(ax, so, time_nums):
    
    
    ax.plot(time_nums,np.repeat(.885, len(time_nums)),color='#969696',alpha=.5)
    ax.plot(time_nums,np.repeat(.885, len(time_nums)),color='#969696',alpha=.5)
    ax.plot(time_nums,np.repeat(-.885, len(time_nums)),color='#969696',alpha=.5)
    
    wind_speed_max = np.max(so.wind_speed)
    
    stringText = ax.text(-.05, .95,"%.2f mph wind\n blowing north" % wind_speed_max,  \
                    bbox={'facecolor':'white', 'alpha':1, 'pad':5}, \
                    va='center', ha='center', transform=ax.transAxes)
    stringText.set_size(9)
#     stringText2 = ax.text(-.05, 0.5,"0 mph wind",  \
#                     bbox={'facecolor':'white', 'alpha':1, 'pad':5}, \
#                     va='center', ha='center', transform=ax.transAxes)
#     stringText2.set_size(9)
    stringText3 = ax.text(-.05, .05,"%.2f mph wind\n blowing south" % wind_speed_max,  \
                    bbox={'facecolor':'white', 'alpha':1, 'pad':5}, \
                    va='center', ha='center', transform=ax.transAxes)
    stringText3.set_size(9)
    
#     so.wind_direction = np.linspace(0,359,len(so.wind_direction))
    for x in range(0,len(time_nums)):
            U = np.sin(so.wind_direction[x] * np.pi/180)
            V = np.cos(so.wind_direction[x] * np.pi/180)
            
            scale_fraction = float(so.wind_speed[x]) / wind_speed_max 
            scale_factor = (10.0 / scale_fraction)
           
            
            if x == 461:
                Q = ax.quiver(time_nums[x], 0, U, V, headlength=0, 
                          headwidth=0, headaxislength=0, alpha=1, color='red', width=.0015, scale=scale_factor )
#                 ax.quiverkey(Q, 0.4, 0.92, 2, r'$2 \frac{m}{s}$', labelpos='N',
#                    fontproperties={'weight': 'bold'})
#                 ax.quiverkey(Q, 0.4, 0.92, 2, 'Wind Speed', labelpos='N',
#                     fontproperties={'weight': 'bold'})
            else:
                ax.quiver(time_nums[x], 0, U, V, headlength=0, 
                          headwidth=0, headaxislength=0, alpha=.3, color='#045a8d', width=.0015, scale=scale_factor )
            
def get_second_coordinate(y1, yorigin, angle):
    
    newy = (y1 - yorigin)* np.sin(angle * np.pi / 180)
    return newy