from numpy import *
from matplotlib.pyplot import *
from scipy.optimize import newton
from DepthCalculation.pressure_to_depth import g, rho

# eta to pressure
# p α ηρgcosh(k(z+H))/cosh(kH)

# Let's find the maximum wave number we'll have to worry about.

sampling_frequency = 4
nyquist_frequency = 2

# dispersion relation
# ω² = gk⋅tanh(kH)

H = 20

def omega_to_k(omega):
    """
    Gets the wave number from the angular frequency using the
    dispersion relation for water waves and Newton's method.
    """
    f = lambda k: omega**2 - k * g * np.tanh(k * H)
    return newton(f, 0)

t = arange(100)

z = -10

def coefficient(k):
    return cosh(k*(z+H))/cosh(k*H)

omegas = arange(0, 1*pi*nyquist_frequency, .001)
fs = omegas / (2*np.pi)
ks = map(omega_to_k, omegas)
cs = map(coefficient, ks)
clf()

def inverse(n):
    return 1 / n
plot(fs, list(map(inverse, cs)))
xlabel('f (Hz)')
ylabel('scaling coefficient')
grid()
show()
