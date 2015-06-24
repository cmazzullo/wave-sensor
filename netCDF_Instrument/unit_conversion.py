"""Contains conversion factors between different units.

They're all just constants, here's an example:

pressure_in_atm = 1.023 pressure_in_dbar = ATM_TO_DBAR * pressure_in_atm

"""

PSI_TO_DBAR = 0.68947573
ATM_TO_DBAR = 10.1325
PASCAL_TO_DBAR = 0.0001

USGS_PROTOTYPE_VOLTS_TO_DBAR_FUNCTION = lambda x: 0.002527 * x + 5.9984
