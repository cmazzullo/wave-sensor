import numpy as np
cimport numpy as np
cimport cython

DTYPE = np.int
DTYPE2 = np.double

ctypedef np.int_t DTYPE_t
ctypedef np.double_t DTYPE2_t

cdef int length
cdef int measure_max = 50
cdef int measure_min = 0

cdef int air_measure_max = 20

cdef int check_1
cdef int check_2
cdef int check_3
cdef int check_4


@cython.boundscheck(False)
def run_tests(np.ndarray[DTYPE2_t, ndim=1] data, int interpolate, int air):
    '''Get the quality control flags of a pressure time series'''
    
    qc = []
    bad_data = False
    length = data.shape[0]
    
    if interpolate == 0:
        check_4 = 255
    else:
        check_4 = 247
        
        
    for x in range(0,length):
        #It was requested to pull the stuck sensor test
#         if x > 3 and data[x-4] == data[x-3] and data[x-3] == data[x-2] and data[x-2] == data[x-1] and data[x-1] == data[x]:
#             check_1 = 254
#         else:
#             check_1 = 255 
        check_1 = 255
        
        #Sensor test 2, check the reading is within bounds of the valid max or min
        if air == 1:
            if data[x] > air_measure_max or data[x] < measure_min:
                check_2 = 253
                bad_data = True
            else:
                check_2 = 255
        else:
            if data[x] > measure_max or data[x] < measure_min:
                check_2 = 253
                bad_data = True
            else:
                check_2 = 255
            
        #Sensor test 3, check if there was a valid rate of change between two readings
        if x > 0 and (data[x] - data[x-1] > 10
            or data[x] - data[x-1] < -10):
            # print('Minus', data[x] - data[x-1])
            bad_data = True
            check_3 = 251
        else:
            check_3 = 255
            
        qc.append(bin(check_1 & check_2 & check_3 & check_4)[2:])
    return (qc, bad_data)
    
    
    