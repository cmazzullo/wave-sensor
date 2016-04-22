'''
Created on Apr 21, 2016

@author: chogg
'''
import numpy as np
import matplotlib.pyplot as plt
import pressure_to_depth as p2d

T = np.arange(.1,20,.1)
H = np.linspace(1, 20, len(T))

T,H = np.meshgrid(T,H)
Z = p2d.echart_omega_to_wavenumber(np.pi*2/T, H)
# 
# print(Z)
# 
#         
#         
CS = plt.contour(H,T,Z)
plt.clabel(CS, inline=1, fontsize=10)
plt.xlabel('Water Depth in Meters')
plt.ylabel('Period in seconds')
plt.show()