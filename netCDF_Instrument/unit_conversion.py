"""Contains conversion factors between different units.

They're all just constants, here's an example:

pressure_in_atm = 1.023 pressure_in_dbar = ATM_TO_DBAR * pressure_in_atm

"""


def pressure_convert(x):
    '''Convert volts to pascals'''
    return ((x * (30 / 8184) - 6) + 14.7) / 1.45037738

PSI_TO_DBAR = 0.68947573
ATM_TO_DBAR = 10.1325
PASCAL_TO_DBAR = 0.0001

USGS_PROTOTYPE_VOLTS_TO_DBAR_FUNCTION = lambda x: 2.5274e-3 * x + 5.998439
