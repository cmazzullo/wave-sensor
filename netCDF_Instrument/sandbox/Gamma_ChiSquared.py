
import numpy as np
import scipy.stats.chi2 as chi2
#ughhhhh

def gamma_pdf(lam, r, x):
    return lam**r * x**(r-1) * np.e**(-1*lam*x) / fact(r-1)
 
def erlang_rando_var(lam, k, x):
    fun = lambda a, b ,c: np.e**(-1*a*c) * (a*c)**b / fact(b)
    return np.array([fun(lam, k_n, x) for k_n in range(0,k)]).sum()

def fact(k):
    return np.array(np.arange(1, k+1)).prod()
 
 
# print(gamma_pdf(1/2,10,25))
# print(erlang_rando_var(1/2, 10, 25))