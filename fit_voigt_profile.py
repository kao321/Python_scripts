#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################################
#                                                                                                   #
#      fit_voigt_profile.py: fitting Voigt or Gaussian profile on a given data                      # 
#                                                                                                   #
#           author: t. isobe(tisobe@cfa.harvard.edu)                                                #
#                                                                                                   #
#           Last Update:    May 14, 2014                                                            #
#                                                                                                   #
#####################################################################################################

import os
import sys
import re
import string
import random
import operator
import math
import numpy
import astropy.io.fits  as pyfits

import matplotlib as mpl

if __name__ == '__main__':
        mpl.use('Agg')
#
#--- reading directory list
#
path = '/data/mta/Script/Python_script2.7/house_keeping/dir_list'

f= open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()

for ent in data:
    atemp = re.split(':', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)
#
#--- append  pathes to private folders to a python directory
#
sys.path.append(bin_dir)
sys.path.append(mta_dir)
#
#--- import several functions
#
import convertTimeFormat          as tcnv       #---- contains MTA time conversion routines
import mta_common_functions       as mcf        #---- contains other functions commonly used in MTA scripts

from scipy.special import wofz
from kapteyn import kmpfit
ln2 = numpy.log(2)

#
#--- temp writing file name
#
rtail  = int(10000 * random.random())       #---- put a romdom # tail so that it won't mix up with other scripts space
zspace = '/tmp/zspace' + str(rtail)

#---------------------------------------------------------------------------------------------------
#--- fit_voigt_profile: fitting Voigt or Gaussian profile on a given data                        ---
#---------------------------------------------------------------------------------------------------

def  fit_voigt_profile(x, y, type='voigt',  plot_title='', xname='',yname=''):

#
#--- if type == 'voigt', fit a voigt distribution on the data
#
    if type == 'voigt':
        [center, width, amp, alphaD, alphaL, I, a_back, b_back] = voigt_fit(x, y)
#
#--- plot the data
#
        if plot_title != '':
                plot_voigt(x, y, center, width, amp, alphaD, alphaL, center, I, a_back, b_back, plot_title, xname, yname)

        return  [center, width, amp, alphaD, alphaL, I, a_back, b_back]
#
#--- otherwise gaussian fit
#
    else:
        [center, width, amp] = fit_gauss(x, y)
        if plot_title != '':
            plot_gauss(x, y, center, width, amp, plot_title)

        return [center, width, amp]


#---------------------------------------------------------------------------------------------------
#-- find_med: find median point of pha postion                                                   ---
#---------------------------------------------------------------------------------------------------

def find_center(x, y):

    """
    find median point of pha postion
    Input:       x ---  a list of pha counts
    OUtput:     position of the estimated median
    """

    sorted_y = sorted(y)
    ypos     = int(0.95 * len(y))
    target   = sorted_y[ypos]

    xpos     = 0
    for i in range(0, len(y)):
        if y[i] == target:
            xpos = x[i]
            break

    return  xpos

#---------------------------------------------------------------------------------------------------
#-- fit_gauss: fitting a normal distribution on a given data                                     ---
#---------------------------------------------------------------------------------------------------

def fit_gauss(x, y):

    """
    fitting a normal distribution on a given data
    Input:  x   --- a list of the bin
            y   --- a list of the count
    Output: amp --- amp of the a normal distribution
            cent--- center of the normal distribution
            width--- width of the normal distribution

    """
    nx = numpy.array(x)
    ny = numpy.array(y)
    ne = numpy.ones(len(ny))
#
#--- we need to give an initial guess
#
    ymax = numpy.max(ny)
    cest  = find_center(x, y)
    p0 = [ymax, cest, 10, 0]

    fitobj = kmpfit.Fitter(residuals=residualsG, data=(nx,ny,ne))
    fitobj.fit(params0=p0)
    [amp, cent, width, floor] = fitobj.params

    return [cent, width, amp]

#---------------------------------------------------------------------------------------------------
#-- plot_voigt: plotting a fitted result on the data                                             ---
#---------------------------------------------------------------------------------------------------

def plot_voigt(x, y,center, width, amp,  alphaD, alphaL, nu_0, I, a_back, b_back, name='',xname='', yname='', outfile='out.png'):

    """
    plotting a fitted result on the data
    Input:      x   ---- a list of bin value
                y   ---- a list of phas
                amp ---- amp of the normal distribution
                center ---- center of the normal distribution
                width  ---- width of the normal distribution
                name   ---- title of the plot; default ""
                outfile --- output file name; defalut "out.png"
    Output:     outfile in <plot_dir>
    """
#
#--- set plotting range
#
    xmin = int(min(x))
    xmax = int(max(x)) + 1
    ymin = 0
    ymax = int(1.1 * max(y))
#
#--- create Gaussian distribution
#
    p    = (alphaD, alphaL, nu_0, I, a_back, b_back)
    est_v = []
    est_list = []
    for v in range(0, xmax):
        est = funcV(p, v)
        est_v.append(v)
        est_list.append(est)
#
#--- clean up the plotting device
#
    plt.close('all')
#
#---- set a few parameters
#
    mpl.rcParams['font.size'] = 9
    props = font_manager.FontProperties(size=9)
    
    plt.axis([xmin, xmax, ymin, ymax])
    plt.xlabel(xname, size=9)
    plt.ylabel(yname, size=9)
    plt.title(name, size=9)
#
#--- set information text postion and content
#
    tx  = 0.5 * xmax
    ty  = 0.9 * ymax
    line = 'Amp: ' + str(round(amp,2)) + '   Center: ' + str(round(center,2)) + '   FWHM: ' + str(round(width,2))
    plt.text(tx, ty, line)
#
#--- actual plotting
#
    p, = plt.plot(x, y, marker='.', markersize=4.0, lw = 0)
    p, = plt.plot(est_v, est_list, marker= '', lw=3)
#
#--- set the size of the plotting area in inch (width: 10.0in, height 2.08in x number of panels)
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10.0, 5.0)
#
#--- save the plot in png format
#
    plt.savefig(outfile, format='png', dpi=100)

#---------------------------------------------------------------------------------------------------
#-- plot_gauss: plotting a fitted result on the data                                             ---
#---------------------------------------------------------------------------------------------------

def plot_gauss(x, y, center, width,amp,  name='', xname='', yname='', outfile='out.png'):

    """
    plotting a fitted result on the data
    Input:  x   ---- a list of bin value
    y   ---- a list of phas
    amp ---- amp of the normal distribution
    center ---- center of the normal distribution
    width  ---- width of the normal distribution
    name   ---- title of the plot
    outfile --- out put file name
    Output: outfile in <plot_dir>
    """
#
#--- set plotting range
#
    xmin = int(min(x))
    xmax = int(max(x)) + 1
    ymin = 0
    ymax = int(1.1 * max(y))
#
#--- create Gaussian distribution
#
    p= (amp, center, width, 0)
    est_v    = []
    est_list = []
    for v in range(0, xmax):
        est = funcG(p, v)
        est_v.append(v)
        est_list.append(est)
#
#--- clean up the plotting device
#
    plt.close('all')
#
#---- set a few parameters
#
    mpl.rcParams['font.size'] = 9
    props = font_manager.FontProperties(size=9)
    
    plt.axis([xmin, xmax, ymin, ymax])
    plt.xlabel(xname, size=9)
    plt.ylabel(yname, size=9)
    plt.title(name, size=9)
#
#--- set information text postion and content
#
    tx  = 0.5 * xmax
    ty  = 0.9 * ymax
    line = 'Amp: ' + str(round(amp,2)) + '   Center: ' + str(round(center,2)) + '   Width: ' + str(round(width,2))
    plt.text(tx, ty, line)
#
#--- actual plotting
#
    p, = plt.plot(x, y, marker='.', markersize=4.0, lw = 0)
    p, = plt.plot(est_v, est_list, marker= '', lw=3)
#
#--- set the size of the plotting area in inch (width: 10.0in, height 2.08in x number of panels)
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10.0, 5.0)
#
#--- save the plot in png format
#
    plt.savefig(outfile, format='png', dpi=100)

#----------------------------------------------------------------------------------
#-- funcG: Model function is a gaussian                                         ---
#----------------------------------------------------------------------------------

def funcG(p, x):
    """
    Model function is a gaussian
    Input:  p   --- (A, mu, sigma, zerolev) 
    x  
    Output: estimated y values
    """
    A, mu, sigma, zerolev = p
    return( A * numpy.exp(-(x-mu)*(x-mu)/(2*sigma*sigma)) + zerolev )

#----------------------------------------------------------------------------------
#-- residualsG: Return weighted residuals of Gauss  ---
#----------------------------------------------------------------------------------

def residualsG(p, data):

    """
    Return weighted residuals of Gauss
    Input:  p --- parameter list (A, mu, sigma, zerolev) see above
    x, y --- data
    Output:  array of residuals
    """
    
    x, y, err = data
    return (y-funcG(p,x)) / err

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def voigt(x, y):
   # The Voigt function is also the real part of 
   # w(z) = exp(-z^2) erfc(iz), the complex probability function,
   # which is also known as the Faddeeva function. Scipy has 
   # implemented this function under the name wofz()
   z = x + 1j*y
   I = wofz(z).real
   return I


#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def Voigt(nu, alphaD, alphaL, nu_0, A, a=0, b=0):
   # The Voigt line shape in terms of its physical parameters
   f = numpy.sqrt(ln2)
   x = (nu-nu_0)/alphaD * f
   y = alphaL/alphaD * f
   backg = a + b*nu 
   V = A*f/(alphaD*numpy.sqrt(numpy.pi)) * voigt(x, y) + backg
   return V


#---------------------------------------------------------------------------------------------------
#-- funcV: Compose the Voigt line-shape                                                          ---
#---------------------------------------------------------------------------------------------------

def funcV(p, x):
    # Compose the Voigt line-shape
    alphaD, alphaL, nu_0, I, a, b = p
    return Voigt(x, alphaD, alphaL, nu_0, I, a, b)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def residualsV(p, data):
   # Return weighted residuals of Voigt
   x, y, err = data
   return (y-funcV(p,x)) / err

#---------------------------------------------------------------------------------------------------
#-- voigt_fit: fitting voigt profile to the data                                                 ---
#---------------------------------------------------------------------------------------------------

def voigt_fit(x, y):

    """
    fitting voigt profile to the data
    Input:      x   --- independent var
                y   --- dependent var
    Output: [nu_0, hwhm, amp, alphaD, alphaL, nu_0, I, a_back, b_back]
            nu_0 --- central postion
            hwhm    --- HWHM
            amp     --- amp
            alphaD  --- doppler alpha
            alphaL  --- lorntz  alpha
            I       --- area under profile
            a_back  --- base line intercept
            b_back  --- base line slope

    """

    N = len(y)
    x   = numpy.array(x)
    y   = numpy.array(y)
    err = numpy.ones(N)
#
#--- initial guess
#
    A      = max(y)
    alphaD = 0.5
    alphaL = 0.5
    a      = 0
    b      = 0
    nu_0   = find_center(x, y)
    
    p0 = [alphaD, alphaL, nu_0, A, a, b]

#
#--- fit the model
#
    fitter = kmpfit.Fitter(residuals=residualsV, data=(x,y,err))
    fitter.parinfo = [{}, {}, {}, {}, {}, {'fixed':True}]  # Take zero level fixed in fit
    fitter.fit(params0=p0)
    
    alphaD, alphaL, nu_0, I, a_back, b_back = fitter.params

#
#--- compute width: HWHM
#
    c1 = 1.0692
    c2 = 0.86639
    hwhm = 0.5*(c1*alphaL+numpy.sqrt(c2*alphaL**2+4*alphaD**2))
    hwhm = 2.0 * hwhm
#
#--- compute amp
#
    f = numpy.sqrt(ln2)
    Y = alphaL/alphaD * f
    amp = I/alphaD*numpy.sqrt(ln2/numpy.pi)*voigt(0,Y)
    
    return [nu_0, hwhm, amp, alphaD, alphaL, I, a_back, b_back]


#--------------------------------------------------------------------

#
#--- pylab plotting routine related modules
#

from pylab import *
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines as lines

if __name__ == '__main__':
#
#--- check an input file name
#
    if len(sys.argv) == 2:
        file = sys.argv[1]
        type  = 'voigt'
        title = ''
        xname = 'PHA'
        yname = 'Counts'
    elif len(sys.argv) == 3:
        file = sys.argv[1]
        type = sys.argv[2]
        title = ''
        xname = 'PHA'
        yname = 'Counts'
    elif len(sys.argv) == 4:
        file = sys.argv[1]
        type = sys.argv[2]
        title = sys.argv[3]
        xname = 'PHA'
        yname = 'Counts'
    elif len(sys.argv) == 5:
        file = sys.argv[1]
        type = sys.argv[2]
        title = sys.argv[3]
        xname = sys.argv[4]
        yname = 'Counts'
    elif len(sys.argv) == 6:
        file = sys.argv[1]
        type = sys.argv[2]
        title = sys.argv[3]
        xname = sys.argv[4]
        yname = sys.argv[5]
    elif len(sys.argv) > 6:
        print 'too many input, you can put:'
        print '<file name> <type(optional): voigt/gauss> <title(optionanl)> <x axis name(optional)> <y axis name(optional)>'
        exit(1)
    else:
        print "you need to add an input file name"
        print '<file name> <type(optional): voigt/gauss> <title(optionanl)> <x axis name(optional)> <y axis name(optional)>'
        exit(1)

#
#--- read data in
#
    f    = open(file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
    x    = []
    y    = []
    for ent in data:
        atemp = re.split('\s+|\t+', ent)
        x.append(float(atemp[0]))
        y.append(float(atemp[1]))

    out = fit_voigt_profile(x, y, type, title,  xname, yname)
    print str(out)


