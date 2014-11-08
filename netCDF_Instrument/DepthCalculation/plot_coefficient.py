# import numpy as np
from numpy import *
from matplotlib.pyplot import *
from scipy.optimize import newton

# plot setup
ion()
clf()
cla()

# constants
g = 9.8
rho = 1027

hs = arange(0, 50, .1)
f = .5 # example frequency

k = newton(lambda k:g*k*np.tanh(k*h) - (2*pi*0.25)**2, 0)
acceptable = cosh(k*20)/cosh(k*(10)) * ones_like(hs)
for f in arange(.1, .5, .05):
    cs = []
    for i, h in enumerate(hs):
        z = -h / 2
        k = newton(lambda k: g*k*np.tanh(k*h)-(2*pi*f)**2, 0)
        cs.append(cosh(k*h) / cosh(k*(z + h)))
    semilogy(hs, cs, linewidth=2, label='hi cut = %.1f' % f)

plot(hs, acceptable)
xlabel('Water Level (m)')
ylabel('Coefficient')
ylim(0, 100)
grid()
legend()
show()
