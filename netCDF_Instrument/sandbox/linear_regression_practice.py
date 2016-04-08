'''
Created on Apr 7, 2016

@author: chogg
'''

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

h_carbon = [0.99,1.02,1.15,1.29,1.46,1.36,.87, \
            1.23,1.55,1.40,1.19,1.15,.98,1.01, \
            1.11,1.20,1.26,1.32,1.43,.95]

purity = [90.01,89.05,91.43,93.74,96.73,94.45, \
          87.59,91.77,99.42,93.65,93.54,92.52, \
          90.56,89.54,89.85,90.39,93.25,93.41,94.98,87.33]

df = pd.DataFrame({'h-carbon':pd.Series(h_carbon), \
                   'purity':pd.Series(purity)})
df = df.sort_values('h-carbon')

hc = df['h-carbon'].values
pur = df['purity'].values
#n = 20 is implied
def process_data(n = 20):
    
    
    print(df)
    print(Sxx(),Sxy())
    beta_hat1 = Sxy()/Sxx()
    beta_hat0 = np.mean(pur) - (beta_hat1 * np.mean(hc))
      
    y_hat = [beta_hat0 + (beta_hat1 * x) for x in hc]
     
    return y_hat
    
    
def Sxx():
    return np.sum(hc**2) - \
         (np.sum(hc)**2/ len(hc))
         
def Sxy():
    return np.sum(hc * pur) - \
        ((np.sum(hc)*np.sum(pur)) \
         / len(hc))
    

if __name__ == '__main__':
    y_hat = process_data()
    plt.scatter(h_carbon, purity)
    plt.plot(hc, y_hat)
    
    a, b = np.polyfit(hc, pur, deg=1)
    plt.plot()
    print(a,b)
    y_hat2 = [b + (a*x) for x in hc]
    plt.plot(hc, y_hat2) 
    plt.xlabel('Hydrocarbon Level')
    plt.ylabel('Purity')
    plt.show()
    