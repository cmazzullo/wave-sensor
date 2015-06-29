import numpy as np
cimport numpy as np

DTYPE = np.int
DTYPE2 = np.double

ctypedef np.int_t DTYPE_t
ctypedef np.double_t DTYPE2_t

cdef int length
cdef int measure_max = 1000
cdef int measure_min = -1000

cdef int check_1
cdef int check_2
cdef int check_3
qc = []

# @cython.boundscheck(False)
def run_tests(np.ndarray[DTYPE2_t, ndim=1] data):
    length = data.shape[0]
    
    for x in range(0,length):
        if x > 3 and data[x-4] == data[x-3] and data[x-3] == data[x-2] and data[x-2] == data[x-1] and data[x-1] == data[x]:
            check_1 = 254
        else:
            check_1 = 255        
        
        if data[x] > measure_max or data[x] < measure_min:
            check_2 = 253
        else:
            check_2 = 255
            
        if x > 0 and (data[x] - data[x-1] > 10
            or data[x] - data[x-1] < -10):
            print('Minus', data[x] - data[x-1])
            check_3 = 251
        else:
            check_3 = 255
            
        qc.append(bin(check_1 & check_2 & check_3)[2:])
    return qc
    
    
    