#!/usr/bin/env /proj/sot/ska/bin/python

#####################################################################################################
#                                                                                                   #
#   find_moving_average.py: find moving average and envelops on the given data set                  #
#                                                                                                   #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                                   #
#           Last update: Jul 3, 2013                                                                #
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
#--- converTimeFormat contains MTA time conversion routines
#
import convertTimeFormat    as tcnv
import mta_common_functions as mcf

from kapteyn import kmpfit
#
#--- temp writing file name
#

rtail  = int(10000 * random.random())
zspace = '/tmp/zspace' + str(rtail)

#---------------------------------------------------------------------------------------------------
#-- run_moving_average: moving average calling function. Read data and run the function          ---
#---------------------------------------------------------------------------------------------------

def run_moving_average():

    """
    moving average calling function. Read data and run the function

   USAGE:                                      
       find_moving_avg.py <file name> <a period> <degree> <out file>    
                   <option: nodrop = 0>
                                           
       example 1: find_moving_avg.py input_data 10 4 out_data       
               (if you want to drop outlayers)             
       example 2: find_moving_avg.ps input_data 10 4 out_data  nodrop=0
               (if you want to use all the data to fit the line)   
    Input
       file name:  input data file name in (indepedent depedent) format    
               the x and y are separated by a space            
       arange:     interval of the sampling
       nterms:     degree of polynomial fit
       outfile:    output file name
       nodrop:     indicator of how the outlyers will be treated

    Output: outfile (named at input)
            columns: 1. x value (center of the period)
                     2. moving average
                     3. standard deviatiaon of the period
                     4. min of the period
                     5. max of the period
                     6. n-th degree of polynomial fit for moving averge
                     7. n-th degree of polynomial fit for lower envelope
                     8. n-th degree of polynomial fit for upper envelope
                     9. n-th degree of polynomial fit for standard deviation
               
    Read find_moving_average help for more information

    """                                         
#
#---- read input values; nodrop is an option
#
    if len(sys.argv) == 5:
        file    = sys.argv[1]
        arange  = sys.argv[2]
        nterms  = sys.argv[3]
        outfile = sys.argv[4]
        nodrop  = 0
    elif len(sys.argv) == 6:
        file    = sys.argv[1]
        arange  = sys.argv[2]
        nterms  = sys.argv[3]
        outfile = sys.argv[4]
        nodrop  = sys.argv[5]

    arange  = float(arange)
    nterms  = int(nterms)
#
#--- read data
#
    (x, y) = readData(file)
#
#-- calling the maion function
#
    [xcent, movavg, sigma, min_sv, max_sv, y_avg, y_min, y_max, y_sig] = find_moving_average(x, y, arange, nterms, nodrop)
#
#--- print out the results
#
    fo = open('outfile', 'w')
    for i in range(0, len(xcent)):
        fo.write(str(xcent[i]))
        fo.write('\t')
        fo.write(str(movavg[i]))
        fo.write('\t')
        fo.write(str(sigma[i]))
        fo.write('\t')
        fo.write(str(min_sv[i]))
        fo.write('\t')
        fo.write(str(max_sv[i]))
        fo.write('\t')
        fo.write(str(y_avg[i]))
        fo.write('\t')
        fo.write(str(y_min[i]))
        fo.write('\t')
        fo.write(str(y_max[i]))
        fo.write('\t')
        fo.write(str(y_sig[i]))
        fo.write('\n')

    fo.close()

#---------------------------------------------------------------------------------------------------
#-- find_moving_average: compute moving average and lower and upper envelop of the data         ----
#---------------------------------------------------------------------------------------------------

def find_moving_average(xorg, yorg, arange, nterms, nodrop = 0):
    
    """
   fit a moving average, a n-th degree polynomial, and an envelope to a given data (x, y)        
                                           
   INPUT:                                      
       xorg:       independent variable list
       yorg:       dependen variable list
       arange:     a period for a moving average               
                   take this so that each period has enough    
                   data points. if you take the period wider   
                   the moving average get more smoother        
       nterms:     a degree of polynomial fitting (<= 5 are probably safe) 
                   if they are not enough data points, take lower  
                   degree. otherwise, it may not give a good fit   
       ndrop = 0:  indicator of how the outlyers will be handled. See below
                                           
   OUTPUT:     an list of lists of:
               mvavg            a moving average           
               sigma            a standard deviation of the mvavg  
               min_sv           data used to compute bottom envlope
               max_sv           data used to compute top envlope   
               bottom           a polynomial fitted bottom envelop 
               middle           a polynomial fitted middle envelop 
               top              a polynomial fitted top envelop    
               std_fit          a polynomial fit for std       
                                           
   Note:                                       
       To drop outlyers, this script uses two methods to exclude outlyers  
           * outside of 3 sigma from a straight fitted line to the data    
             are dropped                           
           * 0.5% of the lowest and 0.5% highest data are dropped      
       If you do not want to drop the data, then use the option        
           nodrop = 1: only 3 sigma method is used               
           nodrop = 2: only 0.5% of both end will be dropped         
           nodrop = 3:  both mechanisms are not used              
       If there is no option, it will use both to exclude outlyers      

    """
#
#--- fit a straight line
#
    (intercept, slope) = fit_poly(xorg, yorg, 2)
#
#--- find 3 sigma distance from the fitted line
#
    std    = findSlopeSigma(xorg, yorg, intercept, slope)
    slimit = 3.0 * std
#
#--- find top and bottom 5% values
#
    (blimit, tlimit) = findCutValues(yorg)
#
#--- drop outliers if nodrop option indicates so
#
    xdata = []
    ydata = []
    for i in range(0, len(xorg)):
        if nodrop == 0 or nodrop == 1:
            diff = yorg[i] - intercept - slope * xorg[i]
            if diff > slimit:
                continue
        if nodrop == 9 or nodrop == 2:
            if yorg[i] < blimit or yorg[i] > tlimit:
                continue

        xdata.append(xorg[i])
        ydata.append(yorg[i])
#
#--- find moving average
#
    (xcent, movavg, sigma, min_sv, max_sv) = findMovingAvg(xdata, ydata, arange)
#
#--- n-th degree polynomial fitting: moving average
#
    acoeff = fit_poly(xcent, movavg, nterms)                   #---- polynomial coeff estimation
    y_avg  = estimatepolyfit(xcent, acoeff)                    #---- estimated fit
#
#--- n-th degree polynomial fitting: lower envelope
#
    acoeff = fit_poly(xcent, min_sv, nterms)
    y_min  = estimatepolyfit(xcent, acoeff)
#
#--- n-th degree polynomial fitting: upper envelope
#
    acoeff = fit_poly(xcent, max_sv, nterms)
    y_max  = estimatepolyfit(xcent, acoeff)
#
#--- n-th degree polynomial fitting: standard deviation
#
    acoeff = fit_poly(xcent, sigma, nterms)
    y_sig  = estimatepolyfit(xcent, acoeff)

    return [xcent, movavg, sigma, min_sv, max_sv, y_avg, y_min, y_max, y_sig]

#---------------------------------------------------------------------------------------------------
#--  readData: read data from a given data file                                                  ---
#---------------------------------------------------------------------------------------------------

def readData(file):

    """
     read data from a given data file 
     Input: file
     Output: (<x array>, <y array>)
     Note: the file contins two column data which separated by either space (\t+, \s+), ",", ":", or ";".
     The values are converted into float.
    """

    f     = open(file, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
#
#--- check data and devide them into x and y
    xorg = []
    yorg = []
    for ent in data:
#
#--- if it is commented out, skip the line
#
        m = re.search('#', ent)
        if m is not None:
            continue
#
#--- check which divider the data is using
#
        m1 = re.search(':', ent)
        m2 = re.search(',', ent)
        m3 = re.search(';', ent)
        if m1 is not None:
            atemp = re.split(':', ent)
        elif m2 is not None:
            atemp = re.split(',', ent)
        elif m3 is not None:
            atemp = re.split(';', ent)
        else:
            try:
                atemp = re.split('\s+|\t+', ent)
            except:
                continue

        try:
            xval = float(atemp[0])
            yval = float(atemp[1])
            xorg.append(xval)
            yorg.append(yval)
        except:
            pass

    return (xorg, yorg)

#---------------------------------------------------------------------------------------------------
#--  findSlopeSigma: finds a standard deviation for the residuals from a fitted straight line    ---
#---------------------------------------------------------------------------------------------------
        
def findSlopeSigma(x, y, intercept, slope):

    """
    finds a standard deviation for the residuals from a fitted straight line
    Inout:      x         --- independent value (array)
                y         --- dependent value (array)
                intercept --- intercept of the fitted line
                slope     --- slope of the fitted line
    Output:     std       --- standard deviation of the residuals from the fitted line
    """

    sum  = 0.0
    sum2 = 0.0

    for i in range(0, len(x)):
        diff  = y[i] - intercept - slope * x[i]
        sum  += diff
        sum2 += diff * diff

    avg = float(sum)/float(len(x))
    std = math.sqrt(float(sum2) / float(len(x)) - avg * avg)

    return std

#---------------------------------------------------------------------------------------------------
#--- findCutValues: finds the values of thetop and the bottom 0.5% of the data                   ---
#---------------------------------------------------------------------------------------------------

def findCutValues(y):

    """
    finds the values of thetop and the bottom 0.5% of the data
    Input:      y            --- array
    Output:     (ybot, ytop) --- bottom and top 0.5% values of the data
    """
    temp = sorted(y)
    nlim = int(0.005 * len(y))

    ybot = y[nlim]
    ytop = y[len(y) - nlim]

    return(ybot, ytop)

#---------------------------------------------------------------------------------------------------
#--- findMovingAvg: estimate moving average, top and bottom envelope                            ----
#---------------------------------------------------------------------------------------------------

def findMovingAvg(xdata, ydata, arange):

    """
    estimate moving average, top and bottom envelope
    Input:      xdata --- independent variable (array)
                ydata --- dependent variable (array)
                arange--- the interval which you want to find an average
    Output:     xcent --- the mid value of the interval (independent value)
                movavg--- the moving average of the period
                sigma --- the standard deviation of the period
                min_sv--- the min of the period
                max_sv--- the max of the period
    """

    xcent   = []
    movavg  = []
    sigma   = []
    max_sv  = []
    min_sv  = []
#
#--- initialize
#
    start = xdata[0]
    end   = start + arange
    sum   = 0.0
    sum2  = 0.0
    smax  = -1.0e5
    smin  =  1.0e5
    mcnt  = 0

    for i in range(0, len(xdata)):
#
#--- if the data value is in the range, just accumulate
#
        if xdata[i] >= start and xdata[i] < end:
            sum  += ydata[i]
            sum2 += ydata[i] * ydata[i]
            if ydata[i] > smax:
                smax = ydata[i]
            if ydata[i] < smin:
                smin = ydata[i]
            mcnt += 1

        elif xdata[i] <= start:
#
#--- if the data value has not reached to the beginning value, skip
#    
            continue

        elif xdata[i] >= end:
#
#--- if the data value is beyond the upper range, compute average
#
            if mcnt == 0:
#
#--- if there is no data, skip
#
                while(xdata[i] >= end):
                    start = end
                    end   = start + arange

                sum  += ydata[i]
                sum2 += ydata[i] * ydata[i]
                if ydata[i] > smax:
                    smax = ydata[i]
                if ydata[i] < smin:
                    smin = ydata[i]
                mcnt += 1
            else:
                avg = float(sum) / float(mcnt)
                try:
                    std = math.sqrt(float(sum2) /float(mcnt) - avg * avg)
                except:
                    std = 0.0
                movavg.append(avg)
                sigma.append(std)
                max_sv.append(smax)
                min_sv.append(smin)
#
#--- take the mid point of the range to x value
#
                midx = 0.5 * float(start + end)
                xcent.append(midx)
    
                start = end
                end   = start + arange
                sum   = 0.0
                sum2  = 0.0
                smax  = -1.0e5
                smin  =  1.0e5
                mcnt  = 0

    return (xcent, movavg, sigma, min_sv, max_sv) 

#---------------------------------------------------------------------------------------------------
#--- estimatepolyfit: compute polynomial fit value for given parameter sets                      ---
#---------------------------------------------------------------------------------------------------

def estimatepolyfit(x, acoeff):

    """
    compute polynomial fit value for given parameter sets
    Input:      x      ---   independent variable array
                acoeff --- array of polynomial coefficients
    Output:     yest   --- the estimated fitted values (array)
    """

    numcoeff = len(acoeff)

    yest = []
    for i in range(0, len(x)):
        yval = 0
        for j in range(0, numcoeff):
            yval = yval + acoeff[j] *  x[i] ** j

        yest.append(yval)

    return yest

#---------------------------------------------------------------------------------------------------
#-- fit_poly: estimate polynomial fitting coefficients                                          ----
#---------------------------------------------------------------------------------------------------

def fit_poly(x, y, nterms):

    """
    estimate polynomial fitting coefficients
    Input:      x      --- independent variable (array)
                y      --- dependent variable (array)
                nterms --- degree of polynomial fit
    Output:     fitobj.params --- array of polynomial fit coefficient

    Note: for the detail on kmpfit, read: 
                http://www.astro.rug.nl/software/kapteyn/kmpfittutorial.html#a-basic-example
    """
#
#--- make sure that the arrays are numpyed
#
    d = numpy.array(x)
    v = numpy.array(y)
#
#--- set the initial estimate of the coefficients, all "0" is fine
#
    paraminitial = [0.0 for i in range(0, nterms)]
#
#--- call kmfit
#
    fitobj       = kmpfit.Fitter(residuals=residuals, data=(d,v))

    try:
        fitobj.fit(params0=paraminitial)
    except:
        print "Something wrong with fit" 
        raise SystemExit


    return fitobj.params

#---------------------------------------------------------------------------------------------------
#--- residuals: compute residuals                                                                ---
#---------------------------------------------------------------------------------------------------

def residuals(p, data):

    """
    compute residuals
    Input:  p    --- parameter array
            data ---  data (x, y)  x and y must be numpyed
    """
    x, y = data

    return y - model(p, x)

#---------------------------------------------------------------------------------------------------
#--- model: the model to be fit                                                                  ---
#---------------------------------------------------------------------------------------------------

def model(p, x):

    """
    the model to be fit
    Input:  p   --- parameter array
            x   --- independent value (array --- numpyed)
    """

    plen = len(p)
    yest = [p[0] for i in range(0, len(x))]
    for i in range(1, plen):
        yest += p[i] * x**i

    return yest

#------------------------------------------------------------------------------------

if __name__ == '__main__':
    
    run_moving_average()
