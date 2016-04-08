import numpy as np
import pandas as pd
import netCDF4
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import os
from datetime import datetime
import pytz
import random

class constituent(object):
    
    def __init__(self, name, freq_in_hours, amp, phase):
        self.name = name
        self.freq = (2*np.pi) / freq_in_hours
        self.amplitude = amp
        self.phase = phase
        
    def get_calculation(self, t):
        return self.amplitude * np.sin(self.freq*t + self.phase)
        
    def get_description(self):
        return self.name


def tidal_answer(constituents, series_length, time_delta, add_noise = False, noise_level = 1):
    
    water_level = []
    interval = 3600000 * time_delta
    time_data = [(x * interval) + 1404647999870 for x in range(0,series_length)]
    for x in range(0,series_length):
        wl_point = 0
        
        next_point = x * time_delta
        
        for p in constituents:
            wl_point += p.get_calculation(next_point)
        
        if(add_noise):
                rand_inverse = random.randint(0,1)
                
                if rand_inverse == 0:
                    rand_inverse = -1
                
                rand_int = float( random.randint(0,noise_level * 100.0)/100.0 * rand_inverse )
#                 print rand_int
                
                wl_point += rand_int
         
        water_level.append(wl_point)
            
    print(len(water_level), len(time_data))
    return (water_level, time_data)


def create_test_data(consituent_data):
    
    for x in constituent_data:
        depth_data, time_data = tidal_answer(x['data'],x['series_length'], x['t_delta'], x['noise'], x['noise_level'])
        
     #   print(time_series.length, x['series_length'])
        
        epoch_start = datetime(year=1970,month=1,day=1,tzinfo=pytz.utc)    
        nc = netCDF4.Dataset(os.path.join(x['name']),'w',format="NETCDF4_CLASSIC")
        time_dimen = nc.createDimension("time",x['series_length'])
        depth = nc.createVariable("depth","f8",("time",))
        time = nc.createVariable("time","f8",("time"))
        time.setncattr('units', "milliseconds since " + epoch_start.strftime("%Y-%m-%d %H:%M:%S"))
#         timeArray = [x for x in time_series.index]
       
        depth[:] = depth_data
      
        time[:] = time_data
#         plt.plot(time_series.index,time_series.values)
#         plt.show()
        nc.close()

def M2S2N2_plot():
    M2 = [.9549,.9681,.9716,.9659,.9646]
    S2 = [.8036,.8584,.9684,.9651,1.000]
    N2 = [.9301,.9467,.9669,1.0112,.9646]
    
    fig = plt.figure(figsize=(16,7))
    ax = fig.add_subplot(111)
    ax.set_axis_bgcolor('#f7f7f7')
        
    
    ax.set_ylabel('Height in Feet')
    xlabel = ax.set_xlabel("Time Series Length in Days")
    ax.set_xticklabels(["","30","60","120","240","480"])
    
    p1, = plt.plot(np.arange(len(M2)),M2, \
                 alpha=0.70, linewidth="4.0", linestyle="-", color = "red")
    
    plt.plot(np.arange(len(M2)),M2, ".",\
                 alpha=0.70, linewidth="4.0",  color = 'red', ms=15)
    
    p2, = plt.plot(np.arange(len(S2)),S2, \
                 alpha=0.70, linewidth="4.0", linestyle="-", color = "blue")
    plt.plot(np.arange(len(S2)),S2, ".",\
                 alpha=0.70, linewidth="4.0",  color = 'blue', ms=15)
             
    p3, = plt.plot(np.arange(len(N2)),N2, \
                 alpha=0.70, linewidth="4.0", linestyle="-", color = "green")
    plt.plot(np.arange(len(N2)),N2, ".",\
                 alpha=0.70, linewidth="4.0",  color = 'green', ms=15)
    
    p4, = plt.plot(np.arange(len(M2)),np.repeat(1, len(M2)), \
                 alpha=.50, linewidth="2.0", linestyle="--", color = "black")
    
    plt.title("M2, S2, and N2, Constituents at Increasing Time Series Lengths")
    plt.ylim(.75,1.25)
    plt.xlim(-.1, 4.1)
    plt.legend([p1,p2,p3,p4], ["M2","S2","N2","Expected Height"])
    plt.grid(b=True,  color='grey', linestyle="-")
    plt.savefig('M2S2N2Graph.png',bbox_extra_artists=[xlabel], bbox_inches='tight');
    plt.show()
    
def O1K1_plot():
    O1 = [1.1855,1.2356,1.2290,1.2116,1.2211,1.2285]
    K1 = [.8460,.8438,.9167,1.0643,1.1234,1.1288]
   
    fig = plt.figure(figsize=(16,7))
    ax = fig.add_subplot(111)
    ax.set_axis_bgcolor('#f7f7f7')
    
    p1, = plt.plot(np.arange(len(O1)),O1, \
                 alpha=0.70, linewidth="4.0", linestyle="-", color = "red")
    plt.plot(np.arange(len(O1)),O1, ".",\
                 alpha=0.70, linewidth="4.0",  color = 'red', ms=15)
             
    p2, = plt.plot(np.arange(len(K1)),K1, \
                 alpha=0.70, linewidth="4.0", linestyle="-", color = "blue")
    plt.plot(np.arange(len(K1)),K1, ".",\
                 alpha=0.70, linewidth="4.0",  color = 'blue', ms=15)
    
    p3, = plt.plot(np.arange(len(O1)),np.repeat(1, len(O1)), \
                 alpha=.50, linewidth="2.0", linestyle="--", color = "black")

    ax.set_ylabel('Height in Feet')
    xlabel = ax.set_xlabel("Time Series Length in Days")
    ax.set_xticklabels(["","15","30","60","120","240","480"])
    plt.title("O1 and K1 Constituents at Increasing Time Series Lengths")
    plt.ylim(.75,1.25)
    plt.xlim(-.1, 5.1)
    plt.legend([p1,p2,p3], ["O1","K1","Expected Height"],loc=4)
    plt.grid(b=True,  color='grey', linestyle="-")
    plt.savefig('O1K1Graph.png',bbox_extra_artists=[xlabel], bbox_inches='tight');
    plt.show()
    
    
def Big5_plot():
    M2 = [.9856,1.0004,1.0048,1.0005,1.00]
    S2 = [.8021,.8569,.9673,1.0111,1.00]
    N2 = [.9596,.9784,1.0017,.9997,1.00]
    O1 = [1.0194,1.0138,.9980,1.0004,.9995]
    K1 = [.7750,.8382,.9674,.9996,1.00]
   
    fig = plt.figure(figsize=(16,7))
    ax = fig.add_subplot(111)
    ax.set_axis_bgcolor('#f7f7f7')
    
    p1, = plt.plot(np.arange(len(M2)),M2, \
                 alpha=0.70, linewidth="4.0", linestyle="-", color = "red")
    plt.plot(np.arange(len(M2)),M2, ".",\
                 alpha=0.70, linewidth="4.0",  color = 'red', ms=15)
    
    p2, = plt.plot(np.arange(len(S2)),S2, \
                 alpha=0.70, linewidth="4.0", linestyle="-", color = "blue")
    plt.plot(np.arange(len(S2)),S2, ".",\
                 alpha=0.70, linewidth="4.0",  color = 'blue', ms=15)
             
    p3, = plt.plot(np.arange(len(N2)),N2, \
                 alpha=0.70, linewidth="4.0", linestyle="-", color = "green")
    plt.plot(np.arange(len(N2)),N2, ".",\
                 alpha=0.70, linewidth="4.0",  color = 'green', ms=15)
             
    p4, = plt.plot(np.arange(len(O1)),O1, \
                 alpha=0.70, linewidth="4.0", linestyle="-", color = "purple")
    plt.plot(np.arange(len(O1)),O1, ".",\
                 alpha=0.70, linewidth="4.0",  color = 'purple', ms=15)
             
    p5, = plt.plot(np.arange(len(K1)),K1, \
                 alpha=0.70, linewidth="4.0", linestyle="-", color = "orange")
    plt.plot(np.arange(len(K1)),K1, ".",\
                 alpha=0.70, linewidth="4.0",  color = 'orange', ms=15)
    
    p6, = plt.plot(np.arange(len(O1)),np.repeat(1, len(O1)), \
                 alpha=.50, linewidth="2.0", linestyle="--", color = "black")

    ax.set_ylabel('Height in Feet')
    xlabel = ax.set_xlabel("Time Series Length in Days")
    ax.set_xticklabels(["","30","60","120","240","480"])
    plt.title("M2, S2, N2, O1 and K1 Constituents at Increasing Time Series Lengths w/o Node Factors")
    plt.ylim(.75,1.25)
    plt.xlim(-.1, 4.1)
    plt.legend([p1,p2,p3,p4,p5,p6], ["M2","S2","N2","O1","K1","Expected Height"],loc=4)
    plt.grid(b=True,  color='grey', linestyle="-")
    plt.savefig('Big5Graph_1NodeFactor.png',bbox_extra_artists=[xlabel], bbox_inches='tight');
    plt.show()
 
def DepthPlot():
    dsOriginal = Dataset("Big5_480dayNewNoise.nc")
    ogTime = [x for x in dsOriginal.variables["time"]]
    ogDepth = [x for x in dsOriginal.variables["depth"]]
    dsOriginal.close()
    
    dsBoxcar = Dataset("outts_filtered_boxcar.nc")
    boxCarTime = [x for x in dsBoxcar.variables["time"]]
    boxCarDepth = [x for x in dsBoxcar.variables["depth"]]
    dsBoxcar.close()
    
    dsUsgs = Dataset("outts_filtered_usgs.nc")
    usgsTime = [x for x in dsUsgs.variables["time"]]
    usgsDepth = [x for x in dsUsgs.variables["depth"]]
    dsUsgs.close()
    
    dsDoodson = Dataset("outts_filtered_doodson.nc")
    doodsonTime = [x for x in dsDoodson.variables["time"]]
    doodsonDepth = [x for x in dsDoodson.variables["depth"]]
    dsDoodson.close()
    
    fig = plt.figure(figsize = (16,9))
    
    plt1 = plt.plot(ogTime, ogDepth, color="Red")
#     plt2 = plt.plot(boxCarTime, boxCarDepth, color = "Blue")
#     plt3 = plt.plot(usgsTime, usgsDepth, color = "Green")
#     plt4 = plt.plot(doodsonTime, doodsonDepth, color = "Purple")
    
    plt.show()
    
#Plotting 
# M2S2N2_plot() 
# O1K1_plot()
#Big5_plot()
# Static Variables
# series_length = 130
#DepthPlot()

if __name__ == '__main__':
    t_delta = .00006944444444
    # 
    constituent_data = [];
    # 
    # # M2 only, 13 hours
    # constituents = []
    # constituents.append(constituent("M2",12.4206012,1,0))
    # constituent_data.append({"data": constituents, "series_length": series_length + 2, "t_delta": t_delta, "name": "M2_Only13.nc"})
     
    series_length = 1000000
    # M2 only, amplitude 1.0
    # constituents = []
    # constituents.append(constituent("M2",12.4206012,2,0))
    # constituent_data.append({"data": constituents, "series_length": series_length  * 8, "t_delta": t_delta, "name": "M2_Only_2AmpNoise.nc",
    #                          "noise": True, "noise_level": 2})
    # 
    # constituent_data.append({"data": constituents, "series_length": series_length  * 8, "t_delta": t_delta, "name": "M2_Only_2AmpClean.nc",
    #                          "noise": False, "noise_level": 2})
    # # 
    # # N2 only, amplitude 1.0
    # constituents = []
    # constituents.append(constituent("N2",12.65834751,1,0))
    # constituent_data.append({"data": constituents, "series_length": series_length + 1, "t_delta": t_delta, "name": "N2_Only.nc"})
    # 
    # # S2 only, amplitude 1.0
    # constituents = []
    # constituents.append(constituent("S2",12.0,1,0))
    # constituent_data.append({"data": constituents, "series_length": series_length + 1, "t_delta": t_delta, "name": "S2_Only.nc"})
    # 
    # # O1 only, amplitude 1.0
    # constituents = []
    # constituents.append(constituent("O1",25.81933871,1,0))
    # constituent_data.append({"data": constituents, "series_length": series_length + 1, "t_delta": t_delta, "name": "O1_Only.nc"})
    # 
    # # K1 only, amplitude 1.0
    # constituents = []
    # constituents.append(constituent("K1",23.93447213,1,0))
    # constituent_data.append({"data": constituents, "series_length": series_length + 1, "t_delta": t_delta, "name": "K1_Only.nc"})
    # 
    # M2 & S2, amplitudes 1.0 for each, no phase difference
    # constituents = []
    # constituents.append(constituent("M2",12.4206012,1,0))
    # constituents.append(constituent("S2",12.0,1,0))
    # constituents.append(constituent("wave1",.0002777777777,1,0))
    # constituents.append(constituent("wave2",.0005555555554,2,0))
    # constituent_data.append({"data": constituents, "series_length": series_length, "t_delta": t_delta, "name": "M2_S2_plus.nc",
    #                          "noise": False, "noise_level": 0})
    
    # constituents = []
    # constituents.append(constituent("M2",12.4206012,1,0))
    # constituents.append(constituent("S2",12.0,1,0))
    # constituents.append(constituent("wave1",.0002777777777,4,0))
    # constituents.append(constituent("wave2",.0005555555554,1,0))
    # constituents.append(constituent("wave3",.00416666666664,3,0))
    # constituents.append(constituent("wave4",.00555555555554,3,0))
    # constituents.append(constituent("wave5",.00833333333332,3,0))
    # constituent_data.append({"data": constituents, "series_length": series_length, "t_delta": t_delta, "name": "M2_S2_plus2.nc",
    #                          "noise": False, "noise_level": 0})
    
    constituents = []
    # constituents.append(constituent("M2",12.4206012,1,0))
    # constituents.append(constituent("S2",12.0,1,0))
    constituents.append(constituent("wave5",.00833333333332,3,0))
    # constituents.append(constituent("wave6",.01111111111108,4,0))
    # constituents.append(constituent("wave7",.02222222222216,4,0))
    # constituents.append(constituent("wave8",.02666666666665,4,0))
    # constituents.append(constituent("wave9",.07999999999995,4,0))
    # constituents.append(constituent("wave10",.15999999999995,4,0))
    # constituents.append(constituent("wave11",.31999999999999,4,0))
    constituent_data.append({"data": constituents, "series_length": series_length, "t_delta": t_delta, "name": "30_sec_wave.nc",
                             "noise": False, "noise_level": 0})
    
    # constituents = []
    # constituents.append(constituent("M2",12.4206012,1,0))
    # constituents.append(constituent("S2",12.0,1,0))
    # constituents.append(constituent("wave1",.0002777777777,4,0))
    # constituents.append(constituent("wave2",.0005555555554,1,0))
    # constituents.append(constituent("wave3",.00416666666664,3,0))
    # constituents.append(constituent("wave4",.00555555555554,3,0))
    # constituents.append(constituent("wave5",.00833333333332,3,0))
    # constituents.append(constituent("wave6",.01111111111108,4,0))
    # constituents.append(constituent("wave7",.02222222222216,4,0))
    # constituent_data.append({"data": constituents, "series_length": series_length, "t_delta": t_delta, "name": "M2_S2_plus3Noise.nc",
    #                          "noise": True, "noise_level": 1})
    
    # constituents = []
    # constituents.append(constituent("M2",12.4206012,1,0))
    # constituents.append(constituent("S2",12.0,1,0))
    # constituents.append(constituent("wave1",.0002777777777,1,0))
    # constituents.append(constituent("wave2",.0005555555554,2,0))
    # constituent_data.append({"data": constituents, "series_length": series_length, "t_delta": t_delta, "name": "M2_S2_plus.nc",
    #                          "noise": False, "noise_level": 0})
    # 
    # # M2 & N2, amplitudes 1.0 for each, no phase difference
    # constituents = []
    # constituents.append(constituent("M2",12.4206012,1,0))
    # constituents.append(constituent("N2",12.65834751,1,0))
    # constituent_data.append({"data": constituents, "series_length": series_length + 1, "t_delta": t_delta, "name": "M2_N2.nc"})
    # 
    # # N2 & S2, amplitudes 1.0 for each, no phase difference
    # constituents = []
    # constituents.append(constituent("S2",12.0,1,0))
    # constituents.append(constituent("N2",12.65834751,1,0))
    # constituent_data.append({"data": constituents, "series_length": series_length + 1, "t_delta": t_delta, "name": "S2_N2.nc"})
     
    # M2, N2 & S2, amplitudes 1.0 for each, no phase differences, 30 day
    # constituents = []
    # constituents.append(constituent("M2",12.4206012,1,0))
    # constituents.append(constituent("S2",12.0,1,0))
    # constituents.append(constituent("N2",12.65834751,1,0))
    # constituent_data.append({"data": constituents, "series_length": series_length, "t_delta": t_delta, 
    #                          "name": "M2_S2_N2_30day.nc", "noise": False})
    # 
    # constituent_data.append({"data": constituents, "series_length": series_length, "t_delta": t_delta, 
    #                          "name": "M2_S2_N2_30dayNoise.nc", "noise": True})
    # 
    # # M2, N2 & S2, amplitudes 1.0 for each, no phase differences, 60 day
    # constituents = []
    # constituents.append(constituent("M2",12.4206012,1,0))
    # constituents.append(constituent("S2",12.0,1,0))
    # constituents.append(constituent("N2",12.65834751,1,0))
    # constituent_data.append({"data": constituents, "series_length": series_length * 2, "t_delta": t_delta, 
    #                          "name": "M2_S2_N2_60day.nc", "noise": False})
    # constituent_data.append({"data": constituents, "series_length": series_length * 2, "t_delta": t_delta, 
    #                          "name": "M2_S2_N2_60dayNoise.nc", "noise": True})
    # 
    # 
    # # M2, N2 & S2, amplitudes 1.0 for each, no phase differences, 120 day
    # constituents = []
    # constituents.append(constituent("M2",12.4206012,1,0))
    # constituents.append(constituent("S2",12.0,1,0))
    # constituents.append(constituent("N2",12.65834751,1,0))
    # constituent_data.append({"data": constituents, "series_length": series_length * 4, "t_delta": t_delta, 
    #                          "name": "M2_S2_N2_120day.nc", "noise": False})
    # constituent_data.append({"data": constituents, "series_length": series_length * 4, "t_delta": t_delta, 
    #                          "name": "M2_S2_N2_120dayNoise.nc", "noise": True})
    # 
    # M2, N2 & S2, amplitudes 1.0 for each, no phase differences, 240 day
    # constituents = []
    # constituents.append(constituent("M2",12.4206012,1,0))
    # constituents.append(constituent("S2",12.0,1,0))
    # constituents.append(constituent("N2",12.65834751,1,0))
    # constituent_data.append({"data": constituents, "series_length": series_length * 8, "t_delta": t_delta, 
    #                          "name": "M2_S2_N2_240day.nc", "noise": False})
    # constituent_data.append({"data": constituents, "series_length": series_length * 8, "t_delta": t_delta, 
    #                          "name": "M2_S2_N2_240dayNoise.nc", "noise": True})
    # 
    # # M2, N2 & S2, amplitudes 1.0 for each, no phase differences, 480 day
    # constituents = []
    # constituents.append(constituent("M2",12.4206012,1,0))
    # constituents.append(constituent("S2",12.0,1,0))
    # constituents.append(constituent("N2",12.65834751,1,0))
    # constituent_data.append({"data": constituents, "series_length": series_length * 16, "t_delta": t_delta, 
    #                          "name": "M2_S2_N2_480day.nc", "noise": False})
    # constituent_data.append({"data": constituents, "series_length": series_length * 16, "t_delta": t_delta, 
    #                          "name": "M2_S2_N2_480dayNoise.nc", "noise": True})
    # 
    # # O1 & K1, amplitudes 1.0 for each, no phase differences, 15 day
    # constituents = []
    # constituents.append(constituent("O1",25.81933871,1,0))
    # constituents.append(constituent("K1",23.93447213,1,0))
    # constituent_data.append({"data": constituents, "series_length": series_length / 2, "t_delta": t_delta, 
    #                          "name": "O1_K1_15day.nc", "noise": False})
    # constituent_data.append({"data": constituents, "series_length": series_length / 2, "t_delta": t_delta, 
    #                          "name": "O1_K1_15dayNoise.nc", "noise": True})
    # 
    # # O1 & K1, amplitudes 1.0 for each, no phase differences, 30 day
    # constituents = []
    # constituents.append(constituent("O1",25.81933871,1,0))
    # constituents.append(constituent("K1",23.93447213,1,0))
    # constituent_data.append({"data": constituents, "series_length": series_length, "t_delta": t_delta, 
    #                          "name": "O1_K1_30day.nc", "noise": False})
    # constituent_data.append({"data": constituents, "series_length": series_length, "t_delta": t_delta, 
    #                          "name": "O1_K1_30dayNoise.nc", "noise": True})
    # 
    # # O1 & K1, amplitudes 1.0 for each, no phase differences, 60 day
    # constituents = []
    # constituents.append(constituent("O1",25.81933871,1,0))
    # constituents.append(constituent("K1",23.93447213,1,0))
    # constituent_data.append({"data": constituents, "series_length": series_length * 2, "t_delta": t_delta, 
    #                          "name": "O1_K1_60day.nc", "noise": False})
    # constituent_data.append({"data": constituents, "series_length": series_length * 2, "t_delta": t_delta, 
    #                          "name": "O1_K1_60dayNoise.nc", "noise": False})
     
    # # O1 & K1, amplitudes 1.0 for each, no phase differences, 120 day
    # constituents = []
    # constituents.append(constituent("O1",25.81933871,1,0))
    # constituents.append(constituent("K1",23.93447213,1,0))
    # constituent_data.append({"data": constituents, "series_length": series_length * 4, "t_delta": t_delta, 
    #                          "name": "O1_K1_120day.nc", "noise": False})
    # constituent_data.append({"data": constituents, "series_length": series_length * 4, "t_delta": t_delta, 
    #                          "name": "O1_K1_120dayNoise.nc", "noise": True})
    # 
    # # O1 & K1, amplitudes 1.0 for each, no phase differences, 240 day
    # constituents = []
    # constituents.append(constituent("O1",25.81933871,1,0))
    # constituents.append(constituent("K1",23.93447213,1,0))
    # constituent_data.append({"data": constituents, "series_length": series_length * 8, "t_delta": t_delta, 
    #                          "name": "O1_K1_240day.nc", "noise": False})
    # constituent_data.append({"data": constituents, "series_length": series_length * 8, "t_delta": t_delta, 
    #                          "name": "O1_K1_240dayNoise.nc", "noise": True})
    # 
    # # O1 & K1, amplitudes 1.0 for each, no phase differences, 480 day
    # constituents = []
    # constituents.append(constituent("O1",25.81933871,1,0))
    # constituents.append(constituent("K1",23.93447213,1,0))
    # constituent_data.append({"data": constituents, "series_length": series_length * 16, "t_delta": t_delta, 
    #                          "name": "O1_K1_480day.nc", "noise": False})
    # constituent_data.append({"data": constituents, "series_length": series_length * 16, "t_delta": t_delta, 
    #                          "name": "O1_K1_480dayNoise.nc", "noise": True})
    
    #The Big 5 30 Day
    # constituents = []
    # constituents.append(constituent("O1",25.81933871,1,0))
    # constituents.append(constituent("K1",23.93447213,1,0))
    # constituents.append(constituent("M2",12.4206012,1,0))
    # constituents.append(constituent("S2",12.0,1,0))
    # constituents.append(constituent("N2",12.65834751,1,0))
    # constituent_data.append({"data": constituents, "series_length": series_length, "t_delta": t_delta, 
    #                          "name": "Big5_30day.nc", "noise": False, "noise_level": 1})
    # constituent_data.append({"data": constituents, "series_length": series_length, "t_delta": t_delta, 
    #                          "name": "Big5_30dayNoise.nc", "noise": True, "noise_level": 1})
    # 
    #The Big 5 60 Day
    # constituents = []
    # constituents.append(constituent("O1",25.81933871,1,0))
    # constituents.append(constituent("K1",23.93447213,1,0))
    # constituents.append(constituent("M2",12.4206012,1,0))
    # constituents.append(constituent("S2",12.0,1,0))
    # constituents.append(constituent("N2",12.65834751,1,0))
    # constituent_data.append({"data": constituents, "series_length": series_length * 2, "t_delta": t_delta, 
    #                          "name": "Big5_60day.nc", "noise": False, "noise_level": 1})
    # constituent_data.append({"data": constituents, "series_length": series_length * 2, "t_delta": t_delta, 
    #                          "name": "Big5_60dayNoise.nc", "noise": True, "noise_level": 1})
    # 
    # #The Big 5 120 Day
    # constituents = []
    # constituents.append(constituent("O1",25.81933871,1,0))
    # constituents.append(constituent("K1",23.93447213,1,0))
    # constituents.append(constituent("M2",12.4206012,1,0))
    # constituents.append(constituent("S2",12.0,1,0))
    # constituents.append(constituent("N2",12.65834751,1,0))
    # constituent_data.append({"data": constituents, "series_length": series_length * 4, "t_delta": t_delta, 
    #                          "name": "Big5_120day.nc", "noise": False})
    # constituent_data.append({"data": constituents, "series_length": series_length * 4, "t_delta": t_delta, 
    #                          "name": "Big5_120dayNoise.nc", "noise": True})
    # 
    # #The Big 5 240 Day
    # constituents = []
    # constituents.append(constituent("O1",25.81933871,1,0))
    # constituents.append(constituent("K1",23.93447213,1,0))
    # constituents.append(constituent("M2",12.4206012,1,0))
    # constituents.append(constituent("S2",12.0,1,0))
    # constituents.append(constituent("N2",12.65834751,1,0))
    # constituent_data.append({"data": constituents, "series_length": series_length * 8, "t_delta": t_delta, 
    #                          "name": "Big5_240day.nc", "noise": False, "noise_level": 1})
    # constituent_data.append({"data": constituents, "series_length": series_length * 8, "t_delta": t_delta, 
    #                          "name": "Big5_240dayNewNoise.nc", "noise": True, "noise_level": 1})
    # # 
    # # #The Big 5 480 Day
    # constituents = []
    # constituents.append(constituent("O1",25.81933871,1,0))
    # constituents.append(constituent("K1",23.93447213,1,0))
    # constituents.append(constituent("M2",12.4206012,1,0))
    # constituents.append(constituent("S2",12.0,1,0))
    # constituents.append(constituent("N2",12.65834751,1,0))
    # # constituent_data.append({"data": constituents, "series_length": series_length * 16, "t_delta": t_delta, 
    # #                          "name": "Big5_480day.nc", "noise": False})
    # constituent_data.append({"data": constituents, "series_length": series_length * 16, "t_delta": t_delta, 
    #                          "name": "Big5_480dayNewNoise.nc", "noise": True, "noise_level":1})
    
    # # Repeat the "M2 only" test with a 60-day timeseries, a 120-day timeseries and a 240-day timeseries.
    # constituents = []
    # constituents.append(constituent("M2",12.4206012,1,0))
    # 
    # #60 days
    # constituent_data.append({"data": constituents, "series_length": series_length * 2, "t_delta": t_delta, "name": "M2_60day.nc"})
    # 
    # #120 days
    # constituent_data.append({"data": constituents, "series_length": series_length * 4, "t_delta": t_delta, "name": "M2_120day.nc"})
    # 
    # #240 days
    # constituent_data.append({"data": constituents, "series_length": series_length * 8, "t_delta": t_delta, "name": "M2_240day.nc"})
    # 
    # # Repeat the "M2 & S2" test with a 60-day timeseries, a 120-day timeseries and a 240-day timeseries.
    # constituents = []
    # constituents.append(constituent("M2",12.4206012,1,0))
    # constituents.append(constituent("S2",12.0,1,0))
    # 
    # #60 days
    # constituent_data.append({"data": constituents, "series_length": series_length * 2, "t_delta": t_delta, "name": "M2_S2_60day.nc"})
    # 
    # #120 days
    # constituent_data.append({"data": constituents, "series_length": series_length * 4, "t_delta": t_delta, "name": "M2_S2_120day.nc"})
    # 
    # #240 days
    # constituent_data.append({"data": constituents, "series_length": series_length * 8, "t_delta": t_delta, "name": "M2_S2_240day.nc"})
    # 
    # # Repeat the "M2 only" test with a 30-day timeseries, but a 1-minute timestep, a 10-minute timestep, 
    # # a 30-minute timestep and a 60-minute timestep
    # constituents = []
    # constituents.append(constituent("M2",12.4206012,1,0))
    # 
    # 
    # #1 min tdelta
    # t_delta = .0166666666666667
    # constituent_data.append({"data": constituents, "series_length": int(series_length / (t_delta * 10)) + 1, "t_delta": t_delta, "name": "M2_1min.nc"})
    # 
    # #30 sec tdelta
    # t_delta = .0083333333333333
    # constituent_data.append({"data": constituents, "series_length": int(series_length / (t_delta * 10)) + 1, "t_delta": t_delta, "name": "M2_30sec.nc"})
    # 
    # #10 min tdelta
    # t_delta = .166666666666667
    # constituent_data.append({"data": constituents, "series_length": int(series_length / (t_delta * 10)) + 1, "t_delta": t_delta, "name": "M2_10min.nc"})
    # 
    # #60 min tdelta
    # t_delta = 1
    # constituent_data.append({"data": constituents, "series_length": int(series_length / (t_delta * 10)) + 1, "t_delta": t_delta, "name": "M2_60min.nc"})
    
    tdelta = 0.00041657
     
    #Create the test data
    create_test_data(constituent_data);
    #  
    # print('all done!')
     
    # 
    # Remember to run the following...
    # Repeat the "M2 only" test with the Rayleigh factor set at 1.0, 0.5 and 0.0.
     


