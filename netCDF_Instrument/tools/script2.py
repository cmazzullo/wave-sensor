#!/usr/bin/env python3
"""
Created on Thu Aug  7 08:20:07 2014

@author: cmazzullo

Inputs: One netCDF file containing water pressure and one containing
air pressure.

Outputs: One netCDF file containing water pressure, interpolated air
pressure, and water level.
"""


import numpy as np
import shutil
import pressure_to_depth as p2d
import NetCDF_Utils.nc as nc
import NetCDF_Utils.Testing as tests


def make_depth_file(water_fname, air_fname, out_fname, method='combo'):
    """Adds depth information to a water pressure file.

    The argument air_fname is optional, when set to '' no air
    pressure is used.
    """
    device_depth = -1 * nc.get_device_depth(water_fname)
    water_depth = nc.get_water_depth(water_fname)
    timestep = 1 / nc.get_frequency(water_fname)
    sea_pressure = nc.get_pressure(water_fname)
    sea_time = nc.get_time(water_fname)
    sea_qc = nc.get_pressure_qc(water_fname)
    air_qc = None
    test = tests.DataTests()
    test.interpolated_data = True
    if air_fname != '':
        raw_air_pressure = nc.get_air_pressure(air_fname)
        air_time = nc.get_time(air_fname)
        air_pressure = np.interp(sea_time, air_time, raw_air_pressure,
                                 left=nc.FILL_VALUE, right=nc.FILL_VALUE)
        sea_pressure = sea_pressure - air_pressure
        sea_pressure[np.where(air_pressure == nc.FILL_VALUE)] = nc.FILL_VALUE
        test.pressure_data = air_pressure
        air_qc = test.select_tests('')
    if method == 'combo':
        depth = p2d.combo_method(sea_time, sea_pressure,
                                 device_depth, water_depth, timestep)
    elif method == 'naive':
        depth = p2d.hydrostatic_method(sea_pressure)
    if len(depth) == len(sea_pressure) - 1: # this is questionable
        depth = np.append(depth, np.NaN)
    shutil.copy(water_fname, out_fname)
    if air_fname != '':
        nc.append_air_pressure(out_fname, air_pressure)
    nc.append_depth_qc(out_fname, sea_qc, air_qc)
    nc.append_depth(out_fname, depth)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("water_fname",
                        help="a netCDF file containing water pressure data")
    parser.add_argument("air_fname",
                        help="a netCDF file containing air pressure data")
    parser.add_argument("out_fname",
                        help="where you want to put the output file")
    parser.add_argument("--fft",
                        help="don't remove linear trends first",
                        dest='method',
                        const='fft',
                        default='combo',
                        action='store_const')
    parser.add_argument("--naive",
                        help="only find the hydrostatic depth",
                        dest='method',
                        const='naive',
                        default='combo',
                        action='store_const')
    args = parser.parse_args()
    make_depth_file(args.water_fname, args.air_fname, args.out_fname,
                    method=args.method)
