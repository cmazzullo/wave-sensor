#!/usr/bin/env python

"""
NAME:
    tappy_filter.py  

SYNOPSIS:
    tappy_filter.py is only an importable library

DESCRIPTION:
    The tappy_filter.py will eventually contain all filters used by TAPPY.

OPTIONS:
    None - import only

EXAMPLES:
    As library
        import filter
        ...

#Copyright (C) 2008  Tim Cera timcera@earthlink.net
#
#
#    This program is free software; you can redistribute it and/or modify it
#    under the terms of the GNU General Public License as published by the Free
#    Software Foundation; either version 2 of the License, or (at your option)
#    any later version.
#
#    This program is distributed in the hope that it will be useful, but
#    WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
#    or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
#    for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    675 Mass Ave, Cambridge, MA 02139, USA.
"""

#===imports======================
import numpy as np
import sys

#===globals======================
modname = "filter"

#===utilities====================
def msg(txt):
    """Send message to stdout."""
    sys.stdout.write(txt)
    sys.stdout.flush()

# def debug(ftn, txt):
#     """Used for debugging."""
#     if debug_p:
#         sys.stdout.write("%s.%s:%s\n" % (modname, ftn, txt))
#         sys.stdout.flush()

def fatal(ftn, txt):
    """If can't continue."""
    msg = "%s.%s:FATAL:%s\n" % (modname, ftn, txt)
    raise SystemExit, msg
 
def usage():
    """Prints the docstring."""
    print __doc__

#====================================

def fft_lowpass(nelevation, low_bound, high_bound):
    """ Performs a low pass filter on the nelevation series.
    low_bound and high_bound specifes the boundary of the filter.
    """
    import numpy.fft as F
    if len(nelevation) % 2:
        result = F.rfft(nelevation, len(nelevation))
    else:
        result = F.rfft(nelevation)
    freq = F.fftfreq(len(nelevation))[:len(nelevation)/2]
    factor = np.ones_like(result)
    factor[freq > low_bound] = 0.0
    print result
    sl = np.logical_and(high_bound < freq, freq < low_bound)
    print factor
    print sl

    a = factor[sl]
    print 'a', a
    # Create float array of required length and reverse
    a = np.arange(len(a) + 2).astype(float)[::-1]
    print np.arange(len(a) + 2)
    print a
    # Ramp from 1 to 0 exclusive
    a = (a/a[0])[1:-1]

    # Insert ramp into factor
    factor[sl] = a
    print factor[sl]
    result = result * factor
    print result
    print 'resultnog=', len(result)
    relevation = F.irfft(result, len(nelevation))
    print 'result=', len(relevation)
    return relevation
    
def demerliac_filter(dates_filled, nelevation):
    
    kernel = [1, 3, 8, 15, 21, 32, 45, 55, 72, 91, 105, 128, 153, 
            171, 200, 231, 253, 288, 325, 351, 392, 435, 465, 512, 
                558, 586, 624, 658, 678, 704, 726, 738, 752, 762, 766,
            768, 766, 762, 752, 738, 726, 704, 678, 658, 624, 586, 
            558, 512, 465, 435, 392, 351, 325, 288, 253, 231, 200,
            171, 153, 128, 105, 91, 72, 55, 45, 32, 21, 15, 8, 3, 1]
    
    half_kern = len(kernel)//2

    nslice = slice(half_kern, -half_kern)

    relevation = np.convolve(nelevation, kernel, mode = 1)
    return dates_filled[nslice], relevation[nslice]

    
