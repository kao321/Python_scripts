#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################################################
#                                                                                                               #
#       fits_operation.py: collection of fits file related funcitons                                            #
#                                                                                                               #
#           author: t. isobe (tisobe@cfa.harvard.edu)                                                           #
#                                                                                                               #
#           last update: Jul 22, 2013                                                                           #
#                                                                                                               #
#################################################################################################################

import os
import sys
import re
import string
import random
import operator
import math
import numpy

from astropy.io import fits

sys.path.append('/data/mta/Script/Python_script2.7/')

#
#--- import several functions
#
import convertTimeFormat       as tcnv       #---- contains MTA time conversion routines
import mta_common_functions    as mcf        #---- contains other functions commonly used in MTA scripts

#-------------------------------------------------------------------------------------------------------
#-- findKeyWords: for a given fits file name, return a list of keyword lists and their values         --
#-------------------------------------------------------------------------------------------------------

def findKeyWords(file):

    """
    for a given fits file name, return a list of keyword lists and their values
    Input:      file  -- fits file name
    Oputput:    klist -- a list of keywords
                val_list -- value of the keywords
    """

    flist = fits.open(file)
    flist.close()

    fhead = flist[1].header
    klist = fhead.keys()

    val_list = []
    for i in range(0, len(klist)):
        val = flist[0].header[klist[i]]
        val_list.append(val)

    return [klist, val_list]

#-------------------------------------------------------------------------------------------------------
#-- readHeaderLine: for a given fits file name and header keyword, return the value for the keyword ----
#-------------------------------------------------------------------------------------------------------

def readHeaderLine(file, kname):

    """
    for a given fits file name and header keyword, return the value for the keyword
    Input:      file -- fits file name
                name -- keyword
    Output:     val  -- keyward value
    """
    flist = fits.open(file)
    flist.close()

    val   = flist[0].header[kname]

    return val

#-------------------------------------------------------------------------------------------------------
#-- findTableCols: find column names of table fits data                                              ---
#-------------------------------------------------------------------------------------------------------

def findTableCols(file, extent=1):

    """
    find column names of table fits data
    Input:   file       -- fits file name
    Output:  col.name   -- a list of column names
    """
    flist = fits.open(file)
    flist.close()
    cols  = flist[extent].columns

    return cols.names

#-------------------------------------------------------------------------------------------------------
#-- findTableData: extract a table data from a given fits file                                       ---
#-------------------------------------------------------------------------------------------------------

def findTableData(file, col= 'NA', extent=1):

    """
    extract a table data from a given fits file
    Input:      file    -- fits file name
                col     -- column name. if it is not given, print out all data
                           this can be a list of column names or a single column name
    Output:     fdata   -- table data or a list of table data
    """

    flist = fits.open(file)
    fdata = flist[extent].data
    flist.close()
    
    if col != 'NA':
        if isinstance(col, list) or isinstance(col, tuple):
            data_list = []
            for ent in col:
                odata = fdata[ent]
                data_list.append(odata)
            return data_list
        else:
            odata = fdata[col]
            return odata
    else:
        return fdata

#-------------------------------------------------------------------------------------------------------
#-- appendFitsTable: Appending one table fits file to the another                                    ---
#-------------------------------------------------------------------------------------------------------

def appendFitsTable(file1, file2, outname, extension = 1):

    """
    Appending one table fits file to the another
    the output table will inherit column attributes of the first fits table
    Input:      file1   --- fits table
                file2   --- fits table (will be appended to file1)
                outname --- the name of the new fits file
    Output:     a new fits file "outname"
    """

    t1 = fits.open(file1)
    t2 = fits.open(file2)
#
#-- find numbers of rows (two different ways as examples here)
#
    nrow1 = t1[extension].data.shape[0]
    nrow2 = t2[extension].header['naxis2']
#
#--- total numbers of rows to be created
#
    nrows = nrow1 + nrow2
    hdu   = fits.new_table(t1[extension].columns, nrows=nrows)
#
#--- append by the field names
#
    for name in t1[extension].columns.names:
        hdu.data.field(name)[nrow1:] = t2[extension].data.field(name)
#
#--- write new fits data file
#
    hdu.writeto(outname)

    t1.close()
    t2.close()

#-------------------------------------------------------------------------------------------------------
#-- addTwoImages: combine two image files                                                            ---
#-------------------------------------------------------------------------------------------------------

def addTwoImages(file1, file2, outname, extension=0):

    """
    combine two image files
    Input:      file1 / file2  ---- two image files
                outname        ---- the name of output fits image file
                extension      ---- ext #. dfault = 0
    Output:     outname        ---- combined image fits file header is a copy of file1
    """

    t1 = fits.open(file1)
    t2 = fits.open(file2)

    img1 = t1[extension].data
    img2 = t2[extension].data
    (x1, y1) = img1.shape
    (x2, y2) = img2.shape
    if (x1 != x2) or (y1 != y2):
        chk = 0        

    else:
        new_img = img1 + img2
        header  = fits.getheader(file1)

        fits.writeto(outname, new_img, header)

        chk =  1

    t1.close()
    t2.close()

    return chk

#-------------------------------------------------------------------------------------------------------
#-- selectTableData: select data for a given colname and the condition and create a new table fits file-
#-------------------------------------------------------------------------------------------------------

def selectTableData(file, colname, interval, outname, extension = 1, clobber='no'):

    """
    select data for a given colname and the condition and create a new table fits file
    Input:      file     --- input table fits file
                colname  --- column name
                interval --- the data interval inthe forma of <start>:<stop>
                outname  --- output file name
                clobber  --- overwrite the file if exists. if not given, 'no'


    """

    m1 = re.search('y', clobber)
    m2 = re.search('Y', clobber)
    if (m1 is not None) or (m2 is not None):
        mcf.rm_file(outname)

    t     = fits.open(file)
    tdata = t[extension].data
    
    atemp = re.split(':', interval)
    start = float(atemp[0])
    stop  = float(atemp[1])

    mask  = tdata.field(colname) >= start
    modt  = tdata[mask]
    mask  = modt.field(colname)  <= stop
    modt2 = modt[mask]

    header  = fits.getheader(file)
    data    = fits.BinTableHDU(modt2, header)
    data.writeto(outname)

#-------------------------------------------------------------------------------------------------------
#-- fitsImgStat: find min, max, avg, std, and mediam of the image fits file                          ---
#-------------------------------------------------------------------------------------------------------

def fitsImgStat(file, extension=0):

    """
    find min, max, avg, std, and mediam of the image fits file
    Input:      file      --- image fits file name
                extension --- data exteion #. default = 0
    Output:     a list of [min, max, avg, std, med]
    """

    t    = fits.open(file)
    data = t[extension].data

    results = []

    dmin = numpy.min(data)
    results.append(dmin)

    dmax = numpy.max(data)
    results.append(dmax)

    avg  = numpy.mean(data)
    results.append(avg)

    std  = numpy.std(data)
    results.append(std)

    med  = numpy.median(data)
    results.append(med)

    t.close()

    return results

#-------------------------------------------------------------------------------------------------------
#-- maxPosImgFits: find physical location of max value                                               ---
#-------------------------------------------------------------------------------------------------------

def maxPosImgFits(file, extension=0):

    """
    find physical location of max value.
    Input:      file    --- image fits file name
                extension -- extension #. default = 0
    Output:     x, y, and max val in list form
    """

    t    = fits.open(file)
    data = t[extension].data
    max  = numpy.max(data)

    (xdim, ydim) = data.shape
    xdim -= 1
    ydim -= 1
    chk = 0
    for x in range(0, xdim):
        for y in range(0, ydim):
            if data[y, x] == max:
                xpos = x
                ypos = y
                chk = 1
                break

        if chk > 0:
            break

    return (xpos, ypos, max)

#-------------------------------------------------------------------------------------------------------
#-- fitsImagThresh: trim the data at "thresh"                                                        ---
#-------------------------------------------------------------------------------------------------------

def fitsImagThresh(file, outname, thresh, val= 0, extension=0):

    """
    trim the data at "thresh"
    Input:      file      --- input image fits file
                outname   --- output image fits file name
                thresh    --- threshhold
                val       --- value to be replaced. default = 0
                extension --- ext #. defaul = 0
    Output:     outname   --- output fits image file
    """

    t    = fits.open(file)
    data = t[extension].data

    (xdim, ydim) = data.shape
    xdim -= 1
    ydim -= 1
    chk = 0
    for x in range(0, xdim):
        for y in range(0, ydim):
            if data[y, x] >= thresh:
                data[y, x] = val

    header  = fits.getheader(file)
    fits.writeto(outname, data, header)

    t.close()


#-------------------------------------------------------------------------------------------------------
#-- fitsImgSection: extract a x by y section of fits image file                                      ---
#-------------------------------------------------------------------------------------------------------

def fitsImgSection(file, x1, x2, y1, y2, outname, extension=0, clobber='no'):

    """
    extract a x by y section of fits image file
    Input:  file        --- input fits image file name
            x1, x2      --- x range
            y1, y2      --- y rnage
            outname     --- output fits image name
            extension   --- extension #. default = 0
            clobber     --- clobber or not. default = no
    Output: outname     --- fits image file of size x by y
    """


    m1 = re.search('y', clobber)
    m2 = re.search('Y', clobber)
    if (m1 is not None) or (m2 is not None):
        mcf.rm_file(outname)

    t    = fits.open(file)
    data = t[extension].data

    xsize = abs(x2 - x1)
    ysize = abs(y2 - y1)

    output = numpy.matrix(numpy.zeros([ysize, xsize]))

    for x in range(x1, x2):
        for y in range(y1, y2):
            newx = x - x1
            newy = y - y1
            output[newy, newx] = data[y, x]

    header = fits.getheader(file)
    fits.writeto(outname, output, header)

    t.close()

#-------------------------------------------------------------------------------------------------------
#-- fitsTableStat: find min, max, avg, std, and mediam of the column                                  --
#-------------------------------------------------------------------------------------------------------

def fitsTableStat(file, column, extension=1):

    """
    find min, max, avg, std, and mediam of the column. 
    Input       file    --- table fits file name
                column  --- name of the column(s). if there are more than one, must be 
                            in the form of list or tuple
                extension-- data extension #. default = 1
    Output      a list or a list of lists of [min, max, avg, std, med]
    """

    t     = fits.open(file)
    tdata = t[extension].data
    t.close()

    if isinstance(column, list) or isinstance(column, tuple):

        results = []
        for ent in column:
            data = tdata.field(ent)
            line = []
            dmin = min(data)
            line.append(dmin)
            dmax = max(data)
            line.append(dmax)
            avg  = numpy.mean(data)
            line.append(avg)
            std  = numpy.std(data)
            line.append(std)
            med  = numpy.median(data)
            line.append(med)

            if len(column) > 1:
                results.append(line)
            else:
                results = line
                break

    else:
        data = tdata.field(column)
        results = []
        dmin = min(data)
        results.append(dmin)
        dmax = max(data)
        results.append(dmax)
        avg  = numpy.mean(data)
        results.append(avg)
        std  = numpy.std(data)
        results.append(std)
        med  = numpy.median(data)
        results.append(med)

    return results

