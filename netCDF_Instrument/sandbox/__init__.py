import numpy as np
import matplotlib.pyplot as plt

a = [1,2,3,4,5]
b = [3,1,5,2,7]

d,e,c = np.polyfit(a,b,deg=2)

plt.scatter(a,b)


yhat = [c + e*x + d*x**2 for x in a]

plt.plot(a,yhat)

plt.show()
