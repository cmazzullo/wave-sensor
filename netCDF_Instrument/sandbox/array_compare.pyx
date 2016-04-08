import numpy as np
cimport numpy as np
cimport cython

DTYPE2 = np.double
ctypedef np.double_t DTYPE2_t

#OPTIMIZATION FOR C METHOD, NO BOUNDS CHECK IMPROVES PERFORMANCE
@cython.boundscheck(False)
def array_compare(np.ndarray[DTYPE2_t, ndim=1] wire_data,
                  np.ndarray[DTYPE2_t, ndim=1] instrument_data):
    
    cdef final_min = 9999999
    cdef final_start = 0
    cdef final_finish = 0
    cdef start = 0
    cdef endrange
    cdef interp_length
    
    #GET WIRE DATA LENGTH AND INSTRUMENT LENGTH
    endrange = len(wire_data)
    interp_length = len(instrument_data)
    
    #BRUTE FORCE METHOD TO CHECK WHICH PART OF THE INSTRUMENT DATA THE WIRE DATA FITS OVER THE BEST
    while endrange < interp_length:
        min_array = np.sqrt(np.divide(np.sum(np.square(np.subtract(instrument_data[start:endrange],wire_data))), endrange - start))
        if min_array < final_min:
            final_min = min_array
            final_start = start;
            final_finish = endrange;
            
        start += 1
        endrange += 1
        
    #RETURN THE INDICES AND THE FINAL EUCLIDEAN DISTANCE OF THE INSTRUMENT FROM THE WIRE DATA
    return final_start, final_finish, final_min