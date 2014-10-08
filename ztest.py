#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################
#                                                                                       #
#   mta_common_functions.py: collections of python functions used by mta                #
#                                                                                       #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                       #
#       last updated: Oct 24, 2013                                                      #
#                                                                                       #
#########################################################################################

import sys
import os
import string
import re
import getpass
import fnmatch
import math
import numpy
import subprocess

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
#--- append path to a private folder
#

sys.path.append(bin_dir)

#
#--- converTimeFormat contains MTA time conversion routines
#
import convertTimeFormat as tcnv

#
#--- check whose account, and set a path to temp location
#

user = getpass.getuser()
user = user.strip()

#
#--- set temp directory/file
#
tempdir = '/tmp/' + user + '/'
tempout = tempdir + 'ztemp'



#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def isLeapYear(year):

    """
    chek the year is a leap year
    Input:year   in 4 digit
    
    Output:   0--- not leap year
              1--- yes it is leap year
    """

    chk = 4.0 * int(0.25 * year)
    if float(year) == chk:
        return 1
    else:
        return 0


#-----------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------

def stimeToDom(stime):

    """
    convert time in the format of seconds from 1998.1.1 to DO<
    Input: stime --- seconds from 1998,1,1
    Output: dom
    """

#    string = convertCtimeToYdate(stime)
    string = tcnv.convertCtimeToYdate(stime)
    atemp  = re.split(':', string)
    year   = int(atemp[0])
    ydate  = int(atemp[1])
    hours  = int(atemp[2])
    minutes= int(atemp[3])
    seconds= int(atemp[4])

    dom    = findDOM(year, ydate, housrs, minutes, seconds)

    return dom

