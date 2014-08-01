
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
        self.poe = np.concatenate((self.poe,[.01,.005,.002,.001,.0005]))
        self.y = np.sqrt((np.negative(np.log(self.poe))))
        print('wave heights',self.xi)
        self.n = len(self.y)
        self.m = len(self.x)
        self.axis = [[self.x[0], self.x[self.m-1], self.y[0], self.y[self.n-1]]]
        self.dx = np.abs(self.x[self.m-1] - self.x[0])/25
        self.xh = [self.x[0],self.x[self.m-1]]
        self.dy = np.abs(self.y[self.n-1]-self.y[0])/25
        self.yv = [self.y[0],self.y[self.n-1]]
        self.Hrms = Hrms
        self.Htr = Htr
        
    def exceedance_graph(self):
        fig = plt.figure(figsize=(16,8))
        ax = fig.add_subplot(111)
        lims = [0,1]
        for x in range(0,self.n):
            yh = [self.y[x], self.y[x]]
            ax.plot(self.xh,yh,color='grey', alpha=0.5)
            ax.text(self.x[0]-2*self.dx,self.y[x],self.poe[x])
            lims[1] = self.y[x]
        
        for x in range(0,self.m):
            xv = [self.x[x],self.x[x]]
            ax.plot(xv,self.yv,color='grey', alpha=0.5)
            ax.text(self.x[x] - self.dx/4,self.y[0]-self.dy,self.x[x])
            lims[0] = self.x[x]
            
        zi = np.sqrt(np.negative(np.log(self.yi)))
       
        ax.plot(self.xi,zi,'o',label='Observed Waves')
        coef = np.polyfit(self.xi,zi,1)
        xa = list([0.5 * np.min(self.xi)])
        xb = list([1.5 * np.max(self.xi)])
        xx = np.concatenate((np.array(xa),self.xi,np.array(xb)))
        yy = np.polyval(coef, xx)
        print('coefficient',coef)
        print('yy', yy)
        ax.plot(xx,yy, label='Rayleigh Fit')
        
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
        print('yyy', yyy)        
        zzz = np.sqrt(np.negative(np.log(np.subtract(1,yyy))))
        
        ax.plot(xxx,zzz,'r',label='BG Fit')
        ax.legend()
        
        plt.setp(ax.get_yticklabels(), visible=False)
        plt.setp(ax.get_yticklines(),visible=False)
        plt.setp(ax.get_xticklabels(), visible=False)
        plt.setp(ax.get_xticklines(),visible=False)
        plt.ylim(0,lims[1])
        plt.xlim(0,lims[0])
        plt.show()
            
        
    def array_utility(self,start,end):
        a = list([start])
        start += .01
        while start < end:
            a.append(start)
            start += .01
        a.append(end)
        return a
    
    
    

    
    