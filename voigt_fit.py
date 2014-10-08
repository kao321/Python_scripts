#!/usr/bin/env  /proj/sot/ska/bin/python

#####################################################################################################################
#                                                                                                                   #
#           voigt_fit.py: fitting Voigt line profile to the given data                                              #
#                                                                                                                   #
#                   author: t. isobe (tisobe@cfa.harvard.edu)                                                       #
#                                                                                                                   #
#                   last update: Jul 25, 2013                                                                       #
#                                                                                                                   #
#           the code is copied from:                                                                                #
#                   http://www.astro.rug.nl/software/kapteyn/kmpfittutorial.html#fitting-voigt-profiles             #
#                                                                                                                   #
#####################################################################################################################

import os
import sys
import re
import string
import random
import operator
import math
import numpy
#
#--- pylab plotting routine related modules
#
import matplotlib as mpl

from matplotlib.pyplot import figure, show, rc
from scipy.special import wofz
#
#--- reading directory list
#
path = '/data/mta/Script/Python_script2.7/house_keeping/dir_list'

f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)
#
#--- append a path to a private folder to python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#---  importing kapteyn routines
#
from kapteyn import kmpfit

ln2 = numpy.log(2)

#-----------------------------------------------------------------------------------------------------
#-- voigt: real part of Faddeeva function.                                                         ---
#-----------------------------------------------------------------------------------------------------

def voigt(x, y):

   """
   The Voigt function is also the real part of 
   w(z) = exp(-z^2) erfc(iz), the complex probability function,
   which is also known as the Faddeeva function. Scipy has 
   implemented this function under the name wofz()

   Input:   x and y
   Output:  real part of Faddeeva function.
   """

   z = x + 1j*y
   I = wofz(z).real
   return I

#-----------------------------------------------------------------------------------------------------
#-- Voigt: voigt line shape                                                                        ---
#-----------------------------------------------------------------------------------------------------

def Voigt(nu, alphaD, alphaL, nu_0, A, a=0, b=0):

   """
   The Voigt line shape in terms of its physical parameters
   Input:   
            nu     --- x-values, usually frequencies.
            alphaD --- Half width at half maximum for Doppler profile
            alphaL --- Half width at half maximum for Lorentz profile
            nu_0   --- Central frequency
            A      --- Area under profile
            a, b   --- Background as in a + b*x
   Output: voigt line profile
   """
   f = numpy.sqrt(ln2)
   x = (nu-nu_0)/alphaD * f
   y = alphaL/alphaD * f
   backg = a + b*nu 
   V = A*f/(alphaD*numpy.sqrt(numpy.pi)) * voigt(x, y) + backg
   return V

#-----------------------------------------------------------------------------------------------------
#-- funcV: Compose the Voigt line-shape                                                             --
#-----------------------------------------------------------------------------------------------------

def funcV(p, x):

    """
    Compose the Voigt line-shape
    Input: p       --- parameter list [alphaD, alphaL, nu_0, A, a, b]
           x       --- x value list
    Output: voigt line profile
    """
    alphaD, alphaL, nu_0, I, a, b = p
    return Voigt(x, alphaD, alphaL, nu_0, I, a, b)

#-----------------------------------------------------------------------------------------------------
#-- funcG: Gaussina Model                                                                          ---
#-----------------------------------------------------------------------------------------------------

def funcG(p, x):

    """
    Model function is a gaussian
    Input: p       --- parameter list [A, mu, sigma, zerolev]
          x       --- x value list
    """
    A, mu, sigma, zerolev = p
    return( A * numpy.exp(-(x-mu)*(x-mu)/(2*sigma*sigma)) + zerolev )

#-----------------------------------------------------------------------------------------------------
#-- residualsV: Return weighted residuals of Voigt                                                 ---
#-----------------------------------------------------------------------------------------------------

def residualsV(p, data):
    """
    Return weighted residuals of Voigt
    Input: p       --- parameter list [alphaD, alphaL, nu_0, A, a, b]
           data    --- a list of list (x, y, err)
    """
    x, y, err = data
    return (y-funcV(p,x)) / err

#-----------------------------------------------------------------------------------------------------
#-- residualsG: Return weighted residuals of Gauss                                                 ---
#-----------------------------------------------------------------------------------------------------

def residualsG(p, data):
    """
    Return weighted residuals of Gauss
    Input: p       --- parameter list [A, mu, sigma, zerolev]
           data    --- a list of list (x, y, err)
    """
    x, y, err = data
    return (y-funcG(p,x)) / err

#-----------------------------------------------------------------------------------------------------
#-- fit_voigt: a control function of fitting voigt profile to the given data                       ---
#-----------------------------------------------------------------------------------------------------

def fit_voigt(data, p0,  plot_op='no', xname='X', yname='Cnts', tname='Voigt Fit', xmin='na', xmax='na', ymin='na', ymax = 'na', detail='no'):

    """
    a control function of fitting voigt profile to the given data
    Input:  data    --- data list of [x, y, err]
            p0      --- initial guess of: [alphaD, alphaL, nu_0, A, a, b]
                        nu: x-values, usually frequencies.
                        alphaD: Half width at half maximum for Doppler profile
                        alphaL: Half width at half maximum for Lorentz profile
                        nu_0: Central frequency
                        A: Area under profile
                        a, b: Background as in a + b*x
            plot_op --- whether you want to plot figure, if so "yes". default: 'no'
            xname   --- name of x axis
            yname   --- name of y axis
            tname   --- title
            xmin    --- low end of x axis
            xmax    --- high end of x axis
            ymin    --- low end of y axis
            ymax    --- high end of y axis
            detail  --- whether you want to print detail result. if so "yes". default: 'no'
    Output: voigt parameters and Gaussian parameters
                [alphaD, alphaL, nu_0, A, a, b, height, center, sigma, zerolevel]
            if asked, a png plot: out.png
            if asked, a detail profile: voigt_fitting_profile
    """
    x, y, err = data
#
#--- make sure that data are numpy array
#
    x   = numpy.array(x)
    y   = numpy.array(y)
    err = numpy.array(err)
    N   = len(y)
#
#--- Do the fit
#
    fitter = kmpfit.Fitter(residuals=residualsV, data=(x,y,err))
    fitter.parinfo = [{}, {}, {}, {}, {}, {'fixed':True}]  # Take zero level fixed in fit
    fitter.fit(params0=p0)
#
#--- if detail profile is requsted, print them
#
    if detail == 'yes':
        line = "\n========= Fit results Voigt profile =========\n\n"
        line = line +  "Initial params:" + str(fitter.params0) + "\n"
        line = line +  "Params:        " + str(fitter.params) + "\n"
        line = line +  "Iterations:    " + str(fitter.niter) + "\n"
        line = line +  "Function ev:   " + str(fitter.nfev ) + "\n"
        line = line +  "Uncertainties: " + str(fitter.xerror) + "\n"
        line = line +  "dof:           " + str(fitter.dof) + "\n"
        line = line +  "chi^2, rchi2:  " + str(fitter.chi2_min) + ' ' +  str(fitter.rchi2_min) + "\n"
        line = line +  "stderr:        " + str(fitter.stderr   ) + "\n"
        line = line +  "Status:        " + str(fitter.status) + "\n"
    
        alphaD, alphaL, nu_0, I, a_back, b_back = fitter.params
        c1 = 1.0692
        c2 = 0.86639
        hwhm = 0.5*(c1*alphaL+numpy.sqrt(c2*alphaL**2+4*alphaD**2))
        line = line +  "\nFWHM Voigt profile:     " + str(2*hwhm) + "\n"
        f = numpy.sqrt(ln2)
        Y = alphaL/alphaD * f
        amp = I/alphaD*numpy.sqrt(ln2/numpy.pi)*voigt(0,Y)
        line = line +  "Amplitude Voigt profile:" + str(amp) + "\n"
        line = line +  "Area under profile:     " + str(I) + "\n"

#
#--- Fit the Gaussian model
#
    [alphaD, alphaL, nu_0, A, a, b] = p0
    pg = [A, nu_0, alphaL, a]

    fitterG = kmpfit.Fitter(residuals=residualsG, data=(x,y,err))
#    fitterG.parinfo = [{}, {}, {}, {}, {}]  # Take zero level fixed in fit
    fitterG.fit(params0=pg)

    if detail == 'yes':
        line = line +  "\n\n========= Fit results Gaussian profile ==========\n\n"
        line = line +  "Initial params:" + str(fitterG.params0) + "\n"
        line = line +  "Params:        " + str(fitterG.params) + "\n"
        line = line +  "Iterations:    " + str(fitterG.niter) + "\n"
        line = line +  "Function ev:   " + str(fitterG.nfev ) + "\n"
        line = line +  "Uncertainties: " + str(fitterG.xerror) + "\n"
        line = line +  "dof:           " + str(fitterG.dof) + "\n"
        line = line +  "chi^2, rchi2:  " + str(fitterG.chi2_min) + ' ' +  str(fitterG.rchi2_min) + "\n"
        line = line +  "stderr:        " + str(fitterG.stderr   ) + "\n"
        line = line +  "Status:        " + str(fitterG.status) + "\n"
     
        fwhmG = 2*numpy.sqrt(2*numpy.log(2))*fitterG.params[2]
        line = line +  "FWHM Gaussian: " + str(fwhmG) + "\n"

        f = open('./voigt_fitting_profile', 'w')
        f.write(line)
        f.close()
#
#--- Plot the result
#
    if plot_op == 'yes':
        rc('legend', fontsize=6)
        fig = figure()

        frame1 = fig.add_subplot(1,1,1)

        if xmax != 'na':
            frame1.set_xlim(xmin=xmin, xmax=xmax, auto=False)
            frame1.set_ylim(ymin=ymin, ymax=ymax, auto=False)

        xd = numpy.linspace(x.min(), x.max(), 200)

        frame1.plot(x, y, 'bo', label="data")

        label = "Model with Voigt function"
        frame1.plot(xd, funcV(fitter.params,xd), 'g', label=label)

        label = "Model with Gaussian function"
        frame1.plot(xd, funcG(fitterG.params,xd), 'm', ls='--', label=label)

        offset = a_back+b_back*nu_0
        frame1.plot((nu_0-hwhm,nu_0+hwhm), (offset+amp/2,offset+amp/2), 'r', label='fwhm')

        frame1.plot(xd, a_back+b_back*xd, "y", label='Background')

        frame1.set_xlabel(xname)
        frame1.set_ylabel(yname)

        vals = (fitter.chi2_min, fitter.rchi2_min, fitter.dof)

        [alphaD, alphaL, nu_0, A, a, b] = fitter.params
        t = (alphaD, alphaL, nu_0, A, a, b)

        title = tname +  "  Voigt: $\\alpha_D$=%.2f $\\alpha_L$=%.2f $\\nu_0$ = %.2f A=%.2f  a=%.2f b = %.2f"%t
        frame1.set_title(title, fontsize=9)

        frame1.grid(True)
        leg = frame1.legend(loc=1)

#
#--- set the size of the plotting area in inch (width: 10.0in, height 5.0in)
#
        fig = mpl.pyplot.gcf()
        fig.set_size_inches(10.0, 5.0)
#
#--- save the plot in png format
#
        fig.savefig('out.png', format='png', dpi=100)

#
#--- returning parameters
#
    [alphaD, alphaL, nu_0, A, a, b] = fitter.params
    [height, center, width, floor]  = fitterG.params

    return [alphaD, alphaL, nu_0, A, a, b, height, center, width, floor]
