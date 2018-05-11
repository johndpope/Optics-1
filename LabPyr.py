#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  9 14:55:31 2018
@author: rfrazin

This code is a descendant of Pyr.py.   This version is designed to accurately
reproduce lab measurements, and so allows for different paddings of the two 
FFTs and treats alignments (and possibly other) errors with free parameters.  

params is a dictionary of the basic parameters of the numerical model

"""

import numpy as np

pyrparams = dict()  # dict of nominal optical system paramers
pyrparams['lambda'] = 0.8 # wavelength (microns)
pyrparams['indref'] = 1.45 # pyramid index of refraction
pyrparams['pslope'] = 3. # slope of pyramid faces relative to horizontal (degrees)  
pyrparams['beam_diam'] = 1.e4 # input beam diameter (microns)
pyrparams['d_e2l1'] = 1.e5 # nominal distance from entrance pupil to lens1
pyrparams['f1'] = 1.e6 # focal length of lens #1 (focuses light on pyramid tip)
pyrparams['d_p2l2'] = 1.e5 # distance from pyramid tip to lens 1 (corrected for pyramid glass)
pyrparams['f2'] = 1.e5 # focal length of lens #2 (makes 4 pupil images)
pyrparams['npup'] = 33  # number of pixels in entrace pupil
pyrparams['npad1'] = 2048 # number of points in first FFT
pyrparams['npad2'] = 2048 # number of points in second FFT

# This simulator two dimentions perpendicular to the optical axis and is designed
#   to model the PyWFS in the lab.
class Pyr2D():
    def __init__(self, params=pyrparams):
        self.params = params
        return

# This simulator has only 1 dimension transverse to the optical axis.  The purpose is
#   to test numerical resolution and code algorithms/structures.
class Pyr1D():
    def __init__(self, params=pyrparams):
        return

    # This calculates the field near the focal plane of lens1, which is near the
    #   apex of the pyramid, as a function of both the distance from the entrance
    #   pupil to the lens (den) and the distance from the pupil to the experiment's
    #   focal point (dfo).  This involves 2 Fresnel propagations and quadratic 
    #   factor applied by the lens.
    # Distances are in microns
    def Prop2FirstFocus(self, pfield, den, dfo):
        return(np.nan)

# 1D planar Fresnel beam prop.
# f - complex valued field in initial plane
# z - propagation distance
# diam - diameter of beam
# lam - wavelength
#   NOTE: z, diam, lam must all be in the same units
# npad - must be greater than len(f)
def FresnelProp1D(f, z, diam, lam = 0.8, npad=2048):
    fz = myzp(f, npad)
    dx = diam/(1. + len(f)) # assumes points on f are bin centers
    k = np.linspace(- (npad+1.)/2, (npad+1.)/2, npad)*2*np.pi/(dx*lam)
    return( myfft(myfft(fz,-1)*np.exp(-1j*np.pi*lam*z*k*k), 1) )

#the FORWARD FFT corresponds to direction = -1, the inverse is +1
def myfft(g, direction=-1):  # for centered arrays, custom normalization
    if direction == -1:
        if g.ndim == 1:
            return np.fft.fftshift(np.fft.fft(np.fft.fftshift(g)))/np.sqrt(len(g))
        elif g.ndim ==2:
            return(np.fft.fftshift(np.fft.fft2(np.fft.fftshift(g)))/np.sqrt(g.shape[0]*g.shape[1]))
        else:
            raise Exception("Input array must be 1D or 2D.")
    elif direction == 1:
        if g.ndim == 1:
            return np.fft.ifftshift(np.fft.ifft(np.fft.ifftshift(g)))
        elif g.ndim ==2:
            return(np.fft.ifftshift(np.fft.ifft2(np.fft.ifftshift(g))))
        else:
            raise Exception("Input array must be 1D or 2D.")
    else:
        raise Exception("Invalid direction.")

#  this zero pad function gives rise to purely real myfft with symm. input
def myzp(f, npad):  # zero-pad function for pupil fields
    if f.ndim == 1:
        nfield = len(f) + 1
        if np.mod(nfield, 2) != 0:
            raise Exception("len(f) must be odd.")
        if npad <= len(f):
            raise Exception("npad must be greater than len(f)")
        if np.mod(npad, 2) == 1:
            raise Exception("npad must be even.")
        g = np.zeros(npad).astype('complex')
        g[int(npad/2) - int(nfield/2) + 1:int(npad/2) + int(nfield/2)] = f
        return(g)
    elif f.ndim == 2:
        if f.shape[0] != f.shape[1]:
            raise Exception("f must be square (if 2D).")
        nfield = f.shape[0] + 1
        if np.mod(nfield, 2) != 0:
            raise Exception("len(f) must be odd.")
        if npad <= f.shape[0]:
            raise Exception("npad must be greater than len(f)")
        if np.mod(npad, 2) == 1:
            raise Exception("npad must be even.")
        g = np.zeros((npad, npad)).astype('complex')
        g[int(npad/2) - int(nfield/2) + 1:int(npad/2) + int(nfield/2),
          int(npad/2) - int(nfield/2) + 1:int(npad/2) + int(nfield/2)] = f
        return(g)
    else:
        raise Exception("Input array must be 1D or 2D.")
        return(np.nan)