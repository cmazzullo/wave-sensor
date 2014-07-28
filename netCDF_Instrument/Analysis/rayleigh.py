'''
Created on Jul 25, 2014

@author: Gregory
'''
import numpy as np
import matplotlib.pyplot as plt
from Analysis.BG import BG
class Rayleigh(BG):
    
    def __init__(self,xi,yi,xmark,Hrms,Htr):
        self.xi = xi
        self.yi = yi
        self.x = xmark
        self.poe = np.array(np.divide(range(1,11),10.0))[::-1]
        self.poe = self.poe.concatenate([.01,.005,.002,.001,.0005])
        self.y = np.sqrt((np.negative(np.log(self.poe))))
        self.n = len(self.y)
        self.m = len(self.x)
        self.axis = [[self.x[0], self.x[self.m-1], self.y[0], self.y[self.n-1]]]
        self.dx = np.abs(self.x[self.m-1] - self.x[0])/25
        self.xh = [self.x[0],self.x[self.m-1]]
        self.dy = np.abs(self.y(self.n-1)-self.y[0])/25
        self.yv = [self.y[0],self.y[self.n-1]]
        self.Hrms = Hrms
        self.Htr = Htr
        
    def exceedance_graph(self):
        for x in range(0,self.n):
            plt.plot(self.xh,self.y[x])
            plt.text(self.x[x]-2*self.dx,self.y[x],self.poe[x])
        
        for x in range(0,self.m):
            plt.plot(self.x[0],self),
            plt.text(self.x[x] - self.dx/4,self.y[0]-self.dy,self.x[x])
            
        zi = np.sqrt(np.negative(np.log(self.yi)))
        plt.plot(self.xi,zi,'o')
        coef = np.polyfit(self.xi,zi,1)
        xa = 0.5 * np.min(self.xi)
        xb = 1.5 * np.max(self.xi)
        xx = np.concatenate(np.array(xa),self.xin,np.array(xb))
        yy = np.polyval(coef, xx)
        plt.plot(xx,yy)
        
        H1 = self.get_bg_value(self.Htr/self.Hrms, 1)
        H2 = self.get_bg_value(self.Htr/self.Hrms, 2)
        xxx = self.array_utility(self.x[0],self.x[self.m - 1])
        lxxx = len(xxx)
        yyy = list()
        
        for x in range(0,lxxx):
            if xxx[x] < self.Htr:
                yyy.append(1 - np.exp(np.negative(np.power(xxx[x]/(H1*self.Hrms),2.0))))
            else:
                yyy.append(1 - np.exp(np.negative(np.power(xxx[x]/(H2*self.Hrms),3.6))))
                
        zzz = np.sqrt(np.negative(np.log(np.subtract(1,yyy))))
        
        plt.plot(xxx,zzz,'r')
        plt.show()
            
        
    def array_utility(self,start,end):
        a = list(start)
        start += .01
        while start < end:
            a.append(start)
            start += .01
        a.append(end)
        return a
    
    
if __name__ == '__main__':
    r = Rayleigh()
    
    
    