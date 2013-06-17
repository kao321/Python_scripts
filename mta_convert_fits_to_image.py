#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################################
#                                                                                               #
#       mta_convert_fits_to_image.py: convert a fits img file to a ps, gif, jpg, or png file    #
#                                                                                               #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#                                                                                               #
#       last update: May 13, 2013                                                               #
#                                                                                               #
#################################################################################################

import sys
import os
import string
import re
import getpass
import socket

#
#--- check whose account, and set a path to temp location
#

user = getpass.getuser()
user = user.strip()

#
#---- find host machine name
#

machine = socket.gethostname()
machine = machine.strip()

#
#--- set temp directory/file
#
tempdir = '/tmp/' + user + '/'
tempout = tempdir + 'ztemp'

#
#--- directory containin plotting related scripts
#
pbin_dir =  '/home/ascds/DS.release/otsbin/'
pbin_dir = '/usr/bin/'

#----------------------------------------------------------------------------------------------------------------
#-- mta_convert_fits_to_image: convert a fits img file to a ps, gif, jpg, or png file                         ---
#----------------------------------------------------------------------------------------------------------------

def mta_convert_fits_to_image(infile = 'NA', outfile = 'NA', scale = 'NA', size = 'NA', color = 'NA', type = 'NA'):

    """
    convert a fits img file to a ps, gif, jpg, or png file 

    infile     # input fits file name
    outfile    # output png file name without a suffix
    scale      # scale of the output image; log, linear, or power
    size       # size of the output image; format: 125x125 --- no contorl of size on ps and jpg file
    color      # color of the output image: hear, rainbow1 etc. default is grey
                 to see which color is available, type: 'ls /home/ascds/DS.release/data/*.lut'
    type       # image type: ps, gif, jpg, or png

    """

    if infile == 'NA':
        infile = raw_input('Input file (fits) name: ')
        infile = infile.strip()
    if outfile == 'NA':
        outfile = raw_input('Output file name without sufix: ')
        outfile = outfile.strip()
    if scale == 'NA':
        scale   = raw_input('Scale: ')
        scale   = scale.strip()
    if size  == 'NA':
        size    = raw_input('Size: ')
        size    = size.strip()
    if color == 'NA':
        color   = raw_input('Color: ')
        clolr   = color.strip()
    if type  == 'NA':
        type    = raw_input('Type: ')
        type    = type.strip()

#
#--- set scale
#
    if scale.lower() != 'log' and scale.lower() != 'power':
        scale = 'linear'
#
#--- set default size
#
    if size == '' or size == '-':
        size = '125x125'

#
#--- read color list
#
    cmd  = 'ls /home/ascds/DS.release/data/*.lut > ' + tempout
    os.system(cmd)
    f   = open(tempout, 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()
    cmd = 'rm ' + tempout
    os.system(cmd)
    color_list = []
    for ent in data:
        atemp = re.split('data\/', ent)
        btemp = re.split('\.lut',  atemp[1])
        color_list.append(btemp[0])
#
#--- make sure the color specified is in the list, if not, assign grey
#
    chk = 0
    color = color.lower()

    for ent in color_list:
        if color == ent:
            chk += 1

    if chk == 0:
        color = 'grey'

#
#--- set output format
#
    type = type.lower()
    choice = ['ps', 'gif', 'jpg', 'png']

    clist = [type]
    if set(clist).issubset(set(choice)):
        pass
    else:
        type='gif'

#
#--- define output file name
#
    outfile = outfile + '.' + type

#
#--- convert a fits image into an eps image
#
    cmd = 'dmimg2jpg ' + infile + ' greenfile="" bluefile="" regionfile="" outfile="foo.jpg" scalefunction="'+ scale 
    cmd = cmd + '" psfile="foo.ps"  lut=")lut.' + color + '" showgrid=no  clobber="yes"'

    os.system(cmd)
#
#--- convert and move the image to the correct format and file name
#

    if type == 'ps':
        cmd = 'mv foo.ps ' + outfile
        os.system(cmd)

    elif type == 'jpg':
        cmd = 'mv foo.jpg outfile'
        os.system(cmd)

    elif type == 'gif':
        cmd = 'echo ""|gs -sDEVICE=ppmraw  -r' + size + '  -q -NOPAUSE -sOutputFile=-  ./foo.ps |' 
        cmd = cmd + 'ppmtogif > ' + outfile
        os.system(cmd)

    elif type == 'png':
        cmd = 'echo ""|gs -sDEVICE=ppmraw  -r' + size + '  -q -NOPAUSE -sOutputFile=-  ./foo.ps |' 
        cmd = cmd +  'pnmtopng > ' + outfile
        os.system(cmd)

    os.system('rm foo.*')



#--------------------------------------------------------------------------------------------

if __name__ == '__main__':


    infile = '/data/mta_www/mta_max_exp/Cumulative/ACIS_07_1999_04_2012_s3.fits.gz'
    outfile='test'
    scale  = 'log'
    size   = '125x125'
    color  = 'heat'
    type   = 'png'
    mta_convert_fits_to_image(infile, outfile, scale, size, color, type)


