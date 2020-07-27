#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 09:07:03 2019

@author: touki
"""
import numpy as np
from scipy.fftpack import fft
from scipy.fftpack import ifft

class Spectrum:
    def __init__(self,dt=0.01,Ts=0.1,Te=10.0,T=[]):
        self.dt=dt
        self.Ts=Ts
        self.Te=Te
        self.T=T
        nf=len(T)
        for i in range(1,nf):
            if T[i]<Ts:
                iEnd=i
                break
        for i in range(1,nf):
            if T[i]<Te:
                iStart=i-1
                break
        self.range=range(iStart,iEnd)
    
    def designSpectrum(self,T):
        Sa=np.zeros(len(T))
        for i in self.range:
            Sa[i]=2000
            Ti=T[i]
            if Ti<0.3:
                Sa[i]=4463*Ti**(2/3)
            if Ti>0.7:
                Sa[i]=1104/Ti**(5/3)
        return Sa
        
    def newmark(self,w,h,ag,dt,beta):
        Sa=0
        w2=w*w
        dt2=dt*dt
        Mh=1+h*w*dt+w2*dt2*beta
        Aa=h*w*dt+(0.5-beta)*w2*dt2
        Av=2*h*w+w2*dt
        an=0
        vn=0
        dn=0
        Z=[]
        for agi in ag:
            Fh=agi-w2*dn-Aa*an-Av*vn
            a=Fh/Mh
            da=a-an
            v=vn+an*dt+0.5*da*dt
            d=dn+vn*dt+0.5*an*dt2+beta*da*dt2
            Z.append(agi-a)
            an=a
            vn=v
            dn=d
        Sa=max(np.abs(Z))*100
        return Sa
    
    def responseSpectrum(self,ag,dt,T,h,beta):
        Sa=np.zeros(len(T))
        for i in self.range:
            Ti=T[i]
            w=1/Ti*2*np.pi
            Sa[i]=self.newmark(w,h,ag,dt,beta)

        return Sa
    
    def compareSpectrum(self,SaT,T,ag,dt,h,beta):

        Sa=self.responseSprectrum(ag,dt,T,h,beta)
        n=len(ag)
        # compare spectrum
        Y=fft(ag)
        i=0;
        E=[]
        for i in self.range:
            R=SaT[i]/Sa[i]
            Y[i]=Y[i]*R
            j=n-i
            Y[j]=np.conj(Y[i])
            E.append(np.abs(R-1))
        Err=max(E)
        newag=ifft(Y)

        return Sa,newag,Err
