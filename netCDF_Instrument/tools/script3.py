#!/usr/bin/env python3
from NetCDF_Utils.edit_netcdf import NetCDFReader
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.dates as pltdates
import pandas as pd
import math

class MovingAverage(NetCDFReader):

    def __init__(self):
        super().__init__()
        self.frequency = 3
        self.in_file_name = "script3in.nc"
        self.start_index = -1
        self.end_index = -1
        self.averaged_data = []
        self.rolling_mean = None
        self.window_size = None

    def collect_data(self):
        self.get_test_data(self.in_file_name, time_convert=True)
        self.filter_data()

    def calc_moving_average(self, window_seconds, file_format = "png", out_file_name = "Rolling_Average"):
        '''This filters out flagged bad data then performs a centered moving average on the data

        Arguments
        window_seconds -- the size of the window to average for the data
        '''
        self.window_size = window_seconds / (1 / self.frequency)
        self.min_periods = int(math.ceil(self.window_size * .9))
        data_series = pd.Series(self.depth_data, index=self.times)
        self.rolling_mean = pd.rolling_mean(data_series, self.window_size, center=True, min_periods=self.min_periods)
        self.graph_data(file_format, out_file_name)

    def filter_data(self):
        '''Filters out flagged bad data, if bad assign NaN and then interpolate all NaN data'''

        test_series = pd.Series(self.pressure_qc)
        test_series[test_series != 1111] = np.NaN
# for the mean time we will no longer interpolate the data, instead there will be a missing value if there
# is less than90% of the rolling average


#         wrong_index = test_series[test_series != 1111].index
#         depth_series = pd.Series(self.depth_data)

        #Set NaN to flagged bad data
#         for x in wrong_index:
#             np.putmask(depth_series.values, depth_series.index==x, np.NaN)
#
        #interpolate NaN data
#         x = np.interp(np.arange(len(self.pressure_data)),[x for x in np.arange(len(depth_series.index)) \
#                       if x not in wrong_index] ,depth_series.values[pd.notnull(depth_series.values)])
#
#         self.depth_data = x

    def graph_data(self, file_format, out_file_name):
        '''graphs both rolling average and original depth data'''
        fig = plt.figure(figsize=(18,6))
        ax = fig.add_subplot(111)
        ax.set_axis_bgcolor('#f7f7f7')
        ax.set_xlabel('Time between %s : %s' % (self.times[0], self.times[::-1][0]))
        ax.set_ylabel('Water Level in Meters')

        #plt.grid(b=True, which='both', axis='both',color='grey', linestyle="-")
        plt.title("Filtered Water Level Data")

        p1, = plt.plot(self.times,self.depth_data,alpha=0.70)
        p2, = plt.plot(self.rolling_mean.index,self.rolling_mean.values, color="red",alpha=0.85)

        extra = Rectangle((0, 0), 1, 1, fc="w", fill=False, edgecolor='none', linewidth=0)
        hfmt = pltdates.DateFormatter('\n%m/%d')
        hfmt2 = pltdates.DateFormatter('%H:%M')

        ax.xaxis.set_minor_locator(pltdates.HourLocator(interval = 6))
        ax.xaxis.set_minor_formatter(hfmt2)
        ax.xaxis.grid(True, which="minor", linestyle="-")
        ax.xaxis.set_major_locator(pltdates.DayLocator())
        ax.xaxis.set_major_formatter(hfmt)
        ax.yaxis.grid()

        plt.legend([extra,p1,p2],["Data Recorded at Lat %s Lon %s" % (self.latitude,self.longitude), \
                                  "Original Water Level","Moving Average with %d second window" % \
                                   (self.window_size / self.frequency)], \
                   bbox_to_anchor=(.70, 1.10), loc=2, borderaxespad=0.0)
        plt.savefig(filename= '%s.%s' % (out_file_name,file_format), format=file_format)
        plt.show()



if __name__ == '__main__':
    a = MovingAverage()
    a.collect_data()
    a.calc_moving_average(30)
