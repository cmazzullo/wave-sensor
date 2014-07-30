#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt

def create_data(T):
    '''Fabricates some pressure data covering time T in seconds'''
    samfreq = 4  # Samples per second
    t = np.arange(0, T, samfreq * T)
    r = np.random.normal(scale=.2, size=len(t))
    angfreq = .2
    phase = 2
    amplitude = 4
    p = amplitude + np.sin(angfreq * t + phase) + r
    return p
    
p = create_data(300)

