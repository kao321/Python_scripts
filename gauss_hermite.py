#!/usr/bin/env  /proj/sot/ska/bin/python

#################################################################################################################
#                                                                                                               #
#               gauss_hermite.py: fit Gauss-Hermite profile on a given data                                     #
#                                                                                                               #
#                   author: t. isobe (tisobe@cfa.harvard.edu)                                                   #
#                                                                                                               #
#                   last update: Sep 24, 2013                                                                   #
#                                                                                                               #
#               the code is copied from:                                                                        #
#               http://www.astro.rug.nl/software/kapteyn/kmpfittutorial.html#fitting-gauss-hermite-series       #
#                                                                                                               #
#################################################################################################################

import numpy
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
from scipy.optimize import fsolve

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
PI = numpy.pi
from math import sqrt

#-----------------------------------------------------------------------------------------------------
#-- gausshermiteh3h4: The Gauss-Hermite function                                                    --
#-----------------------------------------------------------------------------------------------------

def gausshermiteh3h4(x, A, x0, s, h3, h4):

    """
    The Gauss-Hermite function is a superposition of functions of the form
    F = (x-xc)/s                                            
    E =  A.Exp[-1/2.F^2] * {1 + h3[c1.F+c3.F^3] + h4[c5+c2.F^2+c4.F^4]} 
    """
    c0 =     sqrt(6.0)/4.0
    c1 =    -sqrt(3.0)
    c2 =    -sqrt(6.0)
    c3 = 2.0*sqrt(3.0)/3.0
    c4 =     sqrt(6.0)/3.0
    
    F = (x-x0)/s
    E = A*numpy.exp(-0.5*F*F)*( 1.0 + h3*F*(c3*F*F+c1) + h4*(c0+F*F*(c2+c4*F*F)) )

    return E

#-----------------------------------------------------------------------------------------------------
#-- hermite2gauss: Convert Gauss-Hermite parameters to Gauss(like)parameters                       ---
#-----------------------------------------------------------------------------------------------------

def hermite2gauss(par, dpar):
    """
    Convert Gauss-Hermite parameters to Gauss(like)parameters.                                        
                                                                
    We use the first derivative of the Gauss-Hermite function   
    to find the maximum, usually around 'x0' which is the center
    of the (pure) Gaussian part of the function.                          
    If F = (x-x0)/s then the function for which we want the     
    the zero's is A0+A1*F+A2*F^2+A3*F^3+A4*F^4+A5*F^5 = 0       
    c0 = 1/4sqrt(6) c1 = -sqrt(3) c2 = -sqrt(6)                 
    c3 = 2/3sqrt(3) c4 = 1/3sqrt(6)                             
    """
    sqrt2pi = sqrt(2.0*PI)
    amp, x0, s, h3, h4 = par
    damp, dx0, ds, dh3, dh4 = dpar   # The errors in those parameters
    c0 = sqrt(6.0)/4.0
    c1 = -sqrt(3.0)
    c2 = -sqrt(6.0)
    c3 = 2.0*sqrt(3.0)/3.0
    c4 = sqrt(6.0)/3.0
    
    A = numpy.zeros(6)
    A[0] = -c1*h3
    A[1] = h4*(c0-2.0*c2) + 1.0
    A[2] = h3*(c1-3.0*c3)
    A[3] = h4*(c2 - 4.0*c4)
    A[4] = c3*h3
    A[5] = c4*h4
#   
#-- Define the function that represents the derivative of
#-- the GH function. You need it to find the position of the maximum.
#
    fx = lambda x: A[0] + x*(A[1]+x*(A[2]+x*(A[3]+x*(A[4]+x*A[5]))))
    xr = fsolve(fx, 0, full_output=True)
    xm = s*xr[0] + x0
    ampmax = gausshermiteh3h4(xm, amp, x0, s, h3, h4)
#
#-- Get line strength
#
    f = 1.0 + h4 * sqrt(6.0) / 4.0
    area  = amp * s * f * sqrt2pi
    d_area = sqrt2pi * sqrt(s*s*f*f*damp*damp +\
                           amp*amp*f*f*ds*ds +\
                           3.0*amp*amp*s*s*dh4*dh4/8.0)
#
#-- Get mean
#
    mean  = x0 + sqrt(3.0)*h3*s
    d_mean = sqrt(dx0*dx0 + 3.0*h3*h3*ds*ds + 3.0*s*s*dh3*dh3)
#
#-- Get dispersion
#
    f = 1.0 + h4*sqrt(6.0)
    dispersion = abs(s * f)
    d_dispersion = sqrt(f*f*ds*ds + 6.0*s*s*dh4*dh4)
#
#-- Skewness
#
    f = 4.0 * sqrt(3.0)
    skewness = f * h3
    d_skewness = f * dh3
#
#-- Kurtosis
#
    f = 8.0 * sqrt(6.0)
    kurtosis = f * h4
    d_kurtosis = f * dh4

    res = dict(xmax=xm, amplitude=ampmax, area=area, mean=mean, dispersion=dispersion,\
              skewness=skewness, kurtosis=kurtosis, d_area=d_area, d_mean=d_mean,\
              d_dispersion=d_dispersion, d_skewness=d_skewness, d_kurtosis=d_kurtosis)
    return res
 

#-----------------------------------------------------------------------------------------------------
#-- funcG: gaussian function model                                                                ----
#-----------------------------------------------------------------------------------------------------

def funcG(p, x):
    """
    Model function is a gaussian
    """
    A, mu, sigma, zerolev = p

    return( A * numpy.exp(-(x-mu)*(x-mu)/(2*sigma*sigma)) + zerolev )

#-----------------------------------------------------------------------------------------------------
#-- funcGH: Gauss-Hermite function model                                                           ---
#-----------------------------------------------------------------------------------------------------

def funcGH(p, x):
    """
    Model is a Gauss-Hermite function
    """
    A, xo, s, h3, h4, zerolev= p
   
    return gausshermiteh3h4(x, A, xo, s, h3, h4) + zerolev

#-----------------------------------------------------------------------------------------------------
#-- residualsG: Return weighted residuals of Gauss                                                 ---
#-----------------------------------------------------------------------------------------------------

def residualsG(p, data):
    """
    Return weighted residuals of Gauss
    """
    x, y, err = data

    return (y-funcG(p,x)) / err

#-----------------------------------------------------------------------------------------------------
#-- residualsGH: Return weighted residuals of Gauss-Hermite                                        ---
#-----------------------------------------------------------------------------------------------------

def residualsGH(p, data):
    """
    Return weighted residuals of Gauss-Hermite
    """
    x, y, err = data
    return (y-funcGH(p,x)) / err


#-----------------------------------------------------------------------------------------------------
#-- gauss_hermite_fit: control function of Gauss-Hermite fitting                                   ---
#-----------------------------------------------------------------------------------------------------

def gauss_hermite_fit(data, p0, plot_op='no', xname='X', yname='Cnts', tname='Voigt Fit', xmin='na', xmax='na', ymin='na', ymax = 'na', detail='no'):

    """
    control function of Gauss-Hermite fitting
    Input:
            data         --- data list of lists [x, y, err]
            p0 =         --- parameter list: [A1, X1, S1, h31, h41, z01]
                                             A1: area covered
                                             X1: center position
                                             S1:
                                             h31: 
                                             h41:
                                             zo1:
            plot_op     --- if yes, the script will plot. default: no
            xname       --- the name of x axis
            yname       --- the name of y axis
            tname       --- title of the plot
            xmin        --- lower boundary in x of the plot
            xmax        --- upper boundray in x of the plot
            ymin        --- lower boundary in y of the plot
            ymax        --- upper boundray in y of the plot
            detail      --- if yes, it will print fitting profiles. default: no

    Output: param:       [A1, X1, S1, h31, h41, z01, height, center, width, floor]
            if plot is asked:       out.png
            if proflie is asked:    gh_fitting_profile
    """

    x, y, err = data
#
#--- convert the list ot numpy array
#
    x = numpy.array(x)
    y = numpy.array(y)
    err = numpy.array(err)

#
#---- Fit the Gaussian model
#
    [A1, X1, S1, h31, h41, z01] = p0
    pg = [A1, X1, S1, z01]                  #--- approximate the initial values using GH initial estimates

    fitterG = kmpfit.Fitter(residuals=residualsG, data=(x,y,err))
    fitterG.fit(params0=pg)

    if detail == 'yes':
        line = "\n========= Fit results Gaussian profile ==========\n\n"
        line = line +  "Initial params:" + str(fitterG.params0) + "\n"
        line = line +  "Params:        " + str(fitterG.params) + "\n"
        line = line +  "Iterations:    " + str(fitterG.niter) + "\n"
        line = line +  "Function ev:   " + str(fitterG.nfev ) + "\n"
        line = line +  "Uncertainties: " + str(fitterG.xerror) + "\n"
        line = line +  "dof:           " + str(fitterG.dof) + "\n"
        line = line +  "chi^2, rchi2:  " + str(fitterG.chi2_min)+ ' ' + str(fitterG.rchi2_min) + "\n"
        line = line +  "stderr:        " + str(fitterG.stderr   ) + "\n"
        line = line +  "Status:        " + str(fitterG.status) + "\n"

        fwhmG = 2*numpy.sqrt(2*numpy.log(2))*fitterG.params[2]
        line = line +  "FWHM Gaussian: " + str(fwhmG) + "\n"

    z0G = fitterG.params0[-1]          # Store background
#
#--- Fit the Gauss-Hermite model
#
#--- Initial estimates for A, xo, s, h3, h4, z0
#
    fitterGH = kmpfit.Fitter(residuals=residualsGH, data=(x,y,err))
#   fitterGH.parinfo = [{}, {}, {}, {}, {}]  # Take zero level fixed in fit

    fitterGH.fit(params0=p0)
    if detail == 'yes':
        line = line +  "\n\n========= Fit results Gaussian-Hermite profile ==========\n\n"
        line = line +  "Initial params:" + str(fitterGH.params0) + "\n"
        line = line +  "Params:        " + str(fitterGH.params) + "\n"
        line = line +  "Iterations:    " + str(fitterGH.niter) + "\n"
        line = line +  "Function ev:   " + str(fitterGH.nfev ) + "\n"
        line = line +  "Uncertainties: " + str(fitterGH.xerror) + "\n"
        line = line +  "dof:           " + str(fitterGH.dof) + "\n"
        line = line +  "chi^2, rchi2:  " + str(fitterGH.chi2_min) + ' '  + str(fitterGH.rchi2_min) + "\n"
        line = line +  "stderr:        " + str(fitterGH.stderr   ) + "\n"
        line = line +  "Status:        " + str(fitterGH.status) + "\n"
    
        A, x0, s, h3, h4, z0GH = fitterGH.params
#
#--- xm, ampmax, area, mean, dispersion, skewness, kurtosis 
#
        res = hermite2gauss(fitterGH.params[:-1], fitterGH.stderr[:-1])

        line = line +  "Gauss-Hermite max=%g at x=%g\n"%(res['amplitude'], res['xmax'])
        line = line +  "Area      :" + str(res['area'])       + ' ' + str('+-') + ' ' + str(res['d_area']) + "\n"
        line = line +  "Mean (X0) :" + str(res['mean'])       + ' ' + str('+-') + ' ' + str(res['d_mean']) + "\n"
        line = line +  "Dispersion:" + str(res['dispersion']) + ' ' + str('+-') + ' ' + str(res['d_dispersion']) + "\n"
        line = line +  "Skewness  :" + str(res['skewness'])   + ' ' + str('+-') + ' ' + str(res['d_skewness']) + "\n"
        line = line +  "Kurtosis  :" + str(res['kurtosis'])   + ' ' + str('+-') + ' ' + str(res['d_kurtosis']) + "\n"

        f = open('gh_fitting_profile', 'w')
        f.write(line)
        f.close()
#
#---  Plot the result
#
    if plot_op == 'yes':
        rc('legend', fontsize=6)
        fig = figure()

        frame1 = fig.add_subplot(1,1,1)
    
        if xmax != 'na':
            frame1.set_xlim(xmin=xmin, xmax=xmax, auto=False)
            frame1.set_ylim(ymin=ymin, ymax=ymax, auto=False)
    
        xd = numpy.linspace(x.min(), x.max(), 500)

        frame1.plot(x, y, 'bo', label="data")

        label = "Model with Gaussian function"
        frame1.plot(xd, funcG(fitterG.params,xd), 'm', ls='--', label=label)

        label = "Model with Gauss-Hermite function"
        frame1.plot(xd, funcGH(fitterGH.params,xd), 'b',  label=label)

        frame1.plot(xd, [z0G]*len(xd), "y", ls="-.", label='Background G')
        frame1.plot(xd, [z0GH]*len(xd), "y", ls="--", label='Background G-H')

        frame1.set_xlabel(xname)
        frame1.set_ylabel(yname)

        t = (res['area'], res['mean'], res['dispersion'], res['skewness'], res['kurtosis'])
        title = tname +  "  GH: $\gamma_{gh}$=%.1f $\mu_{gh}$=%.1f $\sigma_{gh}$ = %.2f $\\xi_1$=%.2f  $\\xi_f$=%.2f"%t
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
        [A1, X1, S1, h31, h41, z01]     = fitterGH.params
        [height, center, width, floor]  = fitterG.params

    return [A1, X1, S1, h31, h41, z01, height, center, width, floor]

