#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################################
#                                                                                                       #
#       gaussian_fit.py: fitting a Gaussian profile for a given data                                    #
#                                                                                                       #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                                   #
#                                                                                                       #
#           last update: Jul 24, 2013                                                                   #
#                                                                                                       #
#           Ref: http://www.astro.rug.nl/software/kapteyn/kmpfittutorial.html#gaussian-profiles         #
#                                                                                                       #
#########################################################################################################

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

#--------------------------------------------------------------------------------------------------------------
#-- fit_gaussian: fitting gaussian profile: control function                                                ---
#--------------------------------------------------------------------------------------------------------------

def fit_gaussian(data, plot_op='no', xname='na', yname='na', tname='na', detail='no'):

    """
    fitting gaussian profile: control function
    Input:      data        --- input data list of lists [xdata, ydata, error]
                plot_op     --- whether you want to create a plot, if so, "yes". Default: "no"
                xname       --- x axis name 
                yname       --- y axis name
                tname       --- title
                detail      --- if you want to print out a detail fitting profile, set "yes'. Default: 'no'
    Output:     fitting parameter [noarmalization, center, sigma, zero level]
                if plotting is asked, "out.png" is created
                if detail is requested, kmpfit_info is created
    """

    x, y, err = data
#
#--- fitting parameters
#
    pinitial = [1600, 10.5, 1.5, 0]                     #---initial guess of:  [noarmalization, center, sigma, zero level]
    param = fit_model(x, y, err, pinitial,  detail)

    if plot_op == 'yes':
#
#--- plotting the result
#
        plot_fig(x, y, param, xname, yname, tname)

    return param

#--------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------

def fit_model(x, y, err, p0,  detail='no'):

    """
    fitting a model to a given data
    Input:      data        --- input data list of lists [xdata, ydata, error]
                p0          --- initial guess of the parameters in a list
                detail      --- if you want to print out a detail fitting profile, set "yes'. Default: 'no'
    Output:     fitting parameter [noarmalization, center, sigma, zero level]
    """
#
#--- convert the data to numpy array
#
    d   = numpy.array(x)
    v   = numpy.array(y)
    err = numpy.array(err)
#
#--- fitting routine starts
#
    fitobj = kmpfit.Fitter(residuals=my_residuals, deriv=my_derivs, data=(d,v,err))

    try:
        fitobj.fit(params0=p0)
    except Exception, mes:
        print "Something wrong with fit:", mes
        raise SystemExit
#
#--- if detail fitting profile is asked, print it out
#
    if detail == 'yes':
        line = "\n\n======== Results kmpfit with explicit partial derivatives =========" + "\n"
        line = line +  "Params:        " +  str(fitobj.params) + "\n"
        line = line +  "Errors from covariance matrix         : " +  str(fitobj.xerror) + "\n"
        line = line +  "Uncertainties assuming reduced Chi^2=1: " +  str(fitobj.stderr)  + "\n"
        line = line +  "Chi^2 min:     " +  str(fitobj.chi2_min) + "\n"
        line = line +  "Reduced Chi^2: " +  str(fitobj.rchi2_min) + "\n"
        line = line +  "Iterations:    " +  str(fitobj.niter) + "\n"
        line = line +  "Function ev:   " +  str(fitobj.nfev)  + "\n"
        line = line +  "Status:        " +  str(fitobj.status) + "\n"
        line = line +  "Status Message:" +  str(fitobj.message) + "\n"
        line = line +  "Covariance:\n"   +  str(fitobj.covar)  + "\n"

        f = open('./kmpfit_info', 'w')
        f.write(line)
        f.close()

    return fitobj.params

#--------------------------------------------------------------------------------------------------------------
#-- my_derivs: fitting derivatives                                                                          ---
#--------------------------------------------------------------------------------------------------------------

def my_derivs(p, data, dflags):

    """
    create fitting derivatives
    Input:  p       --- parameter list
            data    --- data list of lists [x, y, error]
            dflags  --- ??? but used by kmfit
    Output  pderiv  --- a list of derivatives
    """

    x, y, err = data
    A, mu, sigma, zerolev  = p
    pderiv = numpy.zeros([len(p), len(x)])      # You need to create the required array

    sig2 = sigma*sigma
    sig3 = sig2 * sigma
    xmu  = x-mu
    xmu2 = xmu**2
    expo = numpy.exp(-xmu2/(2.0*sig2))
    fx   = A * expo

    for i, flag in enumerate(dflags):
        if flag:
            if i == 0:
                pderiv[0] = expo
            elif i == 1:
                pderiv[1] = fx * xmu/(sig2)
            elif i == 2:
                pderiv[2] = fx * xmu2/(sig3)
            elif i == 3:
                pderiv[3] = 1.0

    pderiv /= -err
    return pderiv

#--------------------------------------------------------------------------------------------------------------
#-- my_residuals: compute residuals                                                                         ---
#--------------------------------------------------------------------------------------------------------------

def my_residuals(p, data):

    """
    compute residuals
    Input:      p    --- parameter list
                data --- data list [x, y, error], the data must be numpy array
    Output:     residuals
    """

    x, y, err = data
    
    return (y-my_model(p,x)) / err

#--------------------------------------------------------------------------------------------------------------
#-- my_model: model you want to fit on the data                                                             ---
#--------------------------------------------------------------------------------------------------------------

def my_model(p, x):

    """
    model you want to fit on the data
    Input:  p    ---- parameter list
            x    ---- an numpy array of independent variable
    Output  an numpy array of estimated values
    """

    A, mu, sigma, zerolev = p

    return( A * numpy.exp(-(x-mu)*(x-mu)/(2.0*sigma*sigma)) + zerolev )

#--------------------------------------------------------------------------------------------------------------
#-- plot_fig: plotting routine                                                                               --
#--------------------------------------------------------------------------------------------------------------

def plot_fig(x, y, p, xname, yname, tname):

    """
    plotting routine
    Input:  x        --- a list of x values
            y        --- a list of y values
            p        --- a list of parameters
            xname    --- a name of x axis
            yname    --- a name of y axis
            tname    --- title of the plot
    Output: out.png  --- a png file
    """
    rc('font', size=9)
    fig   = figure()
    frame = fig.add_subplot(1,1,1)
#
#--- plot actual data points
#
    frame.plot(x, y,  color='red', lw =0 , marker='+', markersize=10.)
#
#--- to make a model plot smooth, take  equally spanced 100 points between min and max value of x data
#
    xmin = min(x)
    xmax = max(x)
    diff = xmax - xmin
    step = diff / 100.0
    xs   = []
    for i in range(0, 100):
        xs.append(step * i)

    frame.plot(xs, my_model(p, xs), 'b', lw=2)
#
#--- axis names and title
#
    frame.set_xlabel(xname)
    frame.set_ylabel(yname)
    frame.set_title(tname,fontsize=10)
#
#--- set the size of the plotting area in inch (width: 10.0in, height 5.0in)
#
    fig = mpl.pyplot.gcf()
    fig.set_size_inches(10.0, 5.0)
#
#--- save the plot in png format
#
    fig.savefig('out.png', format='png', dpi=100)

