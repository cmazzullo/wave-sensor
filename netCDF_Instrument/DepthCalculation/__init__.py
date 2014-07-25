import numpy as np

x = np.random.rand(6)
y = np.random.rand(6)

# fit the data with a 4th degree polynomial
z4 = np.polyfit(x, y, 1) 
p4 = np.poly1d(z4) # construct the polynomial 

z5 = np.polyfit(x, y, 5)
p5 = np.poly1d(z5)

print (z4, '\n%s' % p4)
print(z5,'\n%s' % p5)
