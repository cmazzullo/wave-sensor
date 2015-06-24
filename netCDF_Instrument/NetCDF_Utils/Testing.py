import numpy as np
from bitarray import bitarray as bit


class DataTests(object):
    """QC tests are performed on any data written to a netcdf file"""

    def __init__(self):
        self.five_count_list = list()
        self.pressure_data = None
        self.valid_pressure_range = [-1000,1000]
        self.pressure_max_rate_of_change = 10
        self.depth_data = None
        self.valid_depth_range = [-1000,1000]
        self.depth_max_rate_of_change = 20
        self.temperature_data = None
        self.valid_temperature_range = [-20,50]
        self.temperature_max_rate_of_change = None
        self.prev_value = np.NaN
        self.interpolated_data = False


    def select_tests(self, data_selection):
        '''Runs all of the netcdf Tests on the selected data, then performs an or binary mask (and) for
        those that passed, 1 for pass 0 for fail, and returns an unisgned 4bit integer, leading 1 is just a placeholder'''

        if data_selection == 'depth':
            return self.run_tests(self.depth_data, self.valid_depth_range, self.depth_max_rate_of_change)
        elif data_selection == 'temperature':
            return self.run_tests(self.temperature_data, self.valid_temperature_range \
                                  , self.temperature_max_rate_of_change)
        else:
            return self.run_tests(self.pressure_data, self.valid_pressure_range, \
                                   self.pressure_max_rate_of_change)


    def run_tests(self, data, data_range, rate_of_change):
        """Runs all of the data tests"""

        bit_array1 = [self.get_1_value(x) for x in data]
        bit_array2 = [self.get_2_value(x, data_range) for x in data]
        bit_array3 = [self.get_3_value(x, rate_of_change) for x in data]
        if self.interpolated_data == True:
            bit_array4 = [bit('11110111') for x in data]
            bit_array4[0] = bit('11111111')

        else:
            bit_array4 = [bit('11111111') for x in data]


        final_bits = [bit_array1[x] & bit_array2[x] & bit_array3[x] & bit_array4[x]
                       for x in range(0,len(data))]

        return [x.to01() for x in final_bits]


    def get_1_value(self,x):
        """Checks to see if the sensor recorded 5 identical measurements previous the the current measurement, if so
        indicate an issue with a zero in the 1 bit"""

        if len(self.five_count_list) > 5:
            self.five_count_list.pop()

        flags = np.count_nonzero(np.equal(x,self.five_count_list))
        self.five_count_list.insert(0,x)

        if flags <= 4:
            return bit('11111111')
        else:
            return bit('11111110')

    def get_2_value(self, x, data_range):
        '''Checks if the data point is within a valid range'''

        if np.greater_equal(x,data_range[0]) and \
        np.less_equal(x,data_range[1]):
            return bit('11111111')
        else:
            return bit('11111101')

    def get_3_value(self, x, rate_of_change):
        '''Checks to see if rate of change is within valid range'''

        if np.isnan(self.prev_value) or \
        np.less_equal(np.abs(np.subtract(x,self.prev_value)), rate_of_change):
            self.prev_value = x
            return bit('11111111')
        else:
            self.prev_value = x
            return bit('11111011')


if __name__ == '__main__':
    test = DataTests()
    test.pressure_data = [4,4,4,4,4,4,10,30,200000,10,-300000,10]
    data = test.select_tests('pressure')
