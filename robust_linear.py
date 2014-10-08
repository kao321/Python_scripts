#!/usr/bin/env /proj/sot/ska/bin/python

#############################################################################################
#                                                                                           #
#   robust_linear.py:   compute a linear fit using robust method                            #
#                       Numerical Recipes (FORTRAN version) p.544                           #
#                                                                                           #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                           #
#           Last update:     Jan 15, 2014                                                   #
#                                                                                           #
#############################################################################################

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

#---------------------------------------------------------------------------------------------------
#-- robust_fit: compute a linear fit parameters using rubst fit                                  ---
#---------------------------------------------------------------------------------------------------

def robust_fit(x, y, iter=0):

    """
    compute a linear fit parameters using rubst fit
    Input:      x   --- a list of independent variable
                y   --- a list of dependent variable
                iter--- if it is larger than 0, the error in a slope is computed
    Output:     alpna   --- intersection
                beta    --- slope
                berr    ---- error of slope if iter > 0
    """
    tot = len(x)
    sumx = 0.0
    sumy = 0.0
#
#---robust fit works better if the intercept is close to the middle of the data cluster.
#
    for n in range(0, tot):
        sumx += x[n]
        sumy += y[n]

    xavg = sumx / tot
    yavg = sumy / tot

    xval = []
    yval = []
    for n in range(0, tot):
        xval.append(x[n] - xavg)
        yval.append(y[n] - yavg)

    (alpha, beta) = medfit(xval, yval)

    alpha += beta * (-1.0 * xavg) + yavg
#
#--- estimate the error in the slope
#
    if iter > 0:
        berr = find_ebar(x, y, rounds = iter)
    else:
        berr = -999

    return (alpha, beta, berr)

#---------------------------------------------------------------------------------------------------
#-- least_sq: compute a linear fit parameters using least sq method                              ---
#---------------------------------------------------------------------------------------------------

def least_sq(xval, yval):

    """
    compute a linear fit parameters using least sq method
    Input:  xval    --- a list of independent variable
            yval    --- a list of dependent variable
    Output: aa      --- intersect
            bb      --- slope
            delta   --- denominator
    """

    tot = len(xval)
    sx  = 0.0
    sy  = 0.0
    sxy = 0.0
    sxx = 0.0

    for j in range(0, tot):
        sx  += xval[j]
        sy  += yval[j]
        sxy += xval[j] * yval[j]
        sxx += xval[j] * xval[j]

    delta = tot * sxx - sx * sx

    aa    = (sxx * sy  - sx * sxy) / delta
    bb    = (tot * sxy - sx * sy)  / delta

    return (aa, bb, delta)


#---------------------------------------------------------------------------------------------------
#-- medfit: fit a straight line according to robust fit                                          ---
#---------------------------------------------------------------------------------------------------

def medfit(xval, yval):

    """
    fit a straight line according to robust fit Numerical Recipes (FORTRAN version) p.544
    Input:  xval    --- a list of independent variable
            yval    --- a list of dependent variable
    Output: alpha   --- intersect
            beta    --- slope
    """

    tot = len(xval)
#
#--- first compute a least sq. solution
#
    (aa, bb, delta) = least_sq(xval, yval)
#
#--- save the values for the case the values did not converse
#
    asave = aa
    basve = bb

    chisq = 0.0
    for j in range(0, tot):
        diff   = yval[j] - (aa + bb * xval[j])
        chisq += diff * diff

    sigb       = math.sqrt(chisq / delta)
    b1         = bb
    (f1, abdev)= rofunc(b1, xval, yval)
    b2         = bb + sign(3.0 * sigb, f1)
    (f2, abdev)= rofunc(b2, xval, yval)

    iter = 0
    while f1 * f2 > 0.0:
        bb = 2.0 * b2 - b1
        b1 = b2
        f1 = f2
        b2 = bb
        (f2, abdev) = rofunc(b2, xval, yval)
        iter += 1
        if iter > 100:
            break

    sigb *= 0.01
    iter  = 0
    while abs(b2 - b1) > sigb:
        bb = 0.5 * (b1 + b2)
        if (bb == b1) or (bb == b2):
            break
        (f, abdev) = rofunc(bb, xval, yval)
        if f * f1 >= 0.0:
            f1 = f
            b1 = bb
        else:
            f2 = f
            b2 = bb

        iter += 1
        if iter > 100:
            break

    alpha = aa
    beta  = bb

    if iter >= 100:
        alpha = asave
        beta  = bsave

    abdev = abdev / tot

    return (alpha, beta)

#---------------------------------------------------------------------------------------------------
#-- rofunc: evaluatate 0 = SUM[ x *sign(y - a bx)]                                               ---
#---------------------------------------------------------------------------------------------------

def rofunc(b_in, xval, yval):

    """
    evaluatate 0 = SUM[ x *sign(y - a bx)]
    Input:  b_in    --- slope
            xval    --- a list of independent variable
            yval    --- al ist of dependent variable
    Ouptput: sum    --- evaluated results
            abdev   --- a+b deviation
    """

    tot = len(xval)

    n1  = tot + 1
    nm1 = 0.5 * n1
    nmh = n1  - nm1
    arr = [0.0 for x in range(0, tot)]
    for j in range(0, tot):
        arr[j] = yval[j] - b_in * xval[j]

    arr.sort(key=float)
    aa  = 0.5 * (arr[int(nm1)] + arr[int(nmh)])
    sum = 0.0
    abdev = 0.0
    for j in range(0, tot):
        d      = yval[j] - (b_in * xval[j] + aa)
        abdev += abs(d)
        sum   += xval[j] * sign(1.0, d)

    return (sum, abdev)

#---------------------------------------------------------------------------------------------------
#-- sign: sign function                                                                           --
#---------------------------------------------------------------------------------------------------

def sign(e1, e2):

    """
    sign function
    Input:  e1, e2
    Output: sign * el
    """

    if e2 >= 0:
        sign = 1
    else:
        sign = -1

    return sign * e1

#---------------------------------------------------------------------------------------------------
#-- find_ebar: find error bar for slope using bootstrapp method                                  ---
#---------------------------------------------------------------------------------------------------

def find_ebar(x, y, rounds=100):

    """
    find error bar for slope using bootstrapp method  
    Input:  x   ---- a list of independent variable
            y   ---- a list of dependent variable
            rounds --- how many iterations should be run. default = 100
    Output: std ---- a sigma of the slope
    """

    tot  = len(x)
    sum  = 0.0
    sum2 = 0.0

    for m in range(0, rounds):
        xdata = []
        ydata = []
        for k in range(0, tot):
            no = int(tot * random.random())
            xdata.append(x[no])
            ydata.append(y[no])

        (intc, slope, err) = robust_fit(xdata, ydata, iter=0)
        sum  += slope
        sum2 += slope * slope

    avg = sum / rounds 
    std = math.sqrt(sum2 / rounds - avg * avg)

    return std

