from numpy import arange
import pandas as pd

a = arange(0,900,50)
for x in a:
    print(x)
    
df= pd.read_csv("C:\\Users\\Gregory\\Documents\\GitHub\\wave-sensor\\netCDF_Instrument\\Instruments\\benchmark\\RBR_RSK_Test.txt", \
                skiprows=8227, delim_whitespace=True, \
                            header=None, engine='c', usecols=[0,1,2])
for x in df.itertuples():
    print(x)