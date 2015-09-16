#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################
#                                                                                       #
#   mta_common_functions.py: collections of python functions used by mta                #
#                                                                                       #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                       #
#       last updated: Jul 24, 2015                                                      #
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


#-----------------------------------------------------------------------------------------------------------------------
#--- chkNumeric: checkin entry is numeric value                                                                      ---
#-----------------------------------------------------------------------------------------------------------------------

def chkNumeric(elm):

    """
    check the entry is numeric. If so return True, else False.
    """

    try:
        test = float(elm)
    except:
        return False
    else:
        return True


#---------------------------------------------------------------------------------------------------------
#-- chkFile: check whether a file/directory exits in the directory given                               ---
#---------------------------------------------------------------------------------------------------------

def chkFile(inline, name = 'NA'):

    """
    check whether a file/directory exits in the directory given, 
    Input: a file/directory name with a full path   or a directory path and a file/directory name
    """
#
#--- if the second element is not given, assume that the first element contains a full path and file/directory name
#
    if name == 'NA':
        cmd =  inline
    else:
        cmd = inline + '/' + name 

    chk  = os.path.isfile(cmd)
    chk2 = os.path.isdir(cmd)
    if (chk == True) or (chk2 == True):
        return 1
    else:
        return 0
    
#----------------------------------------------------------------------------------------------------------
#--- useArcrgl: extract data using arc4gl                                                               ---
#----------------------------------------------------------------------------------------------------------

def useArc4gl(operation, dataset, detector, level, filetype, startYear = 0, startYdate = 0, stopYear = 0 , stopYdate = 0,  deposit='./', filename='NA'):

    """
    extract data using arc4gl. 
    input: start, stop (year and ydate), operation (e.g., retrive), dataset (e.g. flight), 
           detector (e.g. hrc), level (eg 0, 1, 2), filetype (e.g, evt1), output file: deposit. 
    return the list of the file name.
    """

#
#--- read a couple of information needed for arc4gl
#

    line   = bindata_dir + '.dare'
    f      = open(line, 'r')
    dare   = f.readline().strip()
    f.close()
    
    line   = bindata_dir + '.hakama'
    f      = open(line, 'r')
    hakama = f.readline().strip()
    f.close()
    
#
#--- use arc4gl to extract data
#
    if startYear > 1000:
        (year1, month1, day1, hours1, minute1, second1, ydate1) = tcnv.dateFormatCon(startYear, startYdate)
    
        (year2, month2, day2, hours2, minute2, second2, ydate2) = tcnv.dateFormatCon(stopYear, stopYdate)

        stringYear1 = str(year1)
        stringYear2 = str(year2)
    
        stringMonth1 = str(month1)
        if month1 < 10:
            stringMonth1 = '0' + stringMonth1
        stringMonth2 = str(month2)
        if month2 < 10:
            stringMonth2 = '0' + stringMonth2
    
        stringDay1 = str(day1)
        if day1 < 10:
            stringDay1 =  '0' + stringDay1
        stringDay2 = str(day2)
        if day2 < 10:
            stringDay2 = '0' + stringDay2
    
        stringHour1 = str(hours1)
        if hours1 < 10:
            stringHour1 = '0' + stringHour1
        stringHour2 = str(hours2)
        if hours2 < 10:
            stringHour2 = '0' + stringHour2
    
        stringMinute1 = str(minute1)
        if minute1 < 10:
            stringMinute1 = '0' + stringMinute1
        stringMinute2 = str(minute2)
        if minute2 < 10:
            stringMinute2 = '0' + stringMinute2
    
        stringYear =  stringYear1[2] + stringYear1[3]
        arc_start = stringMonth1 + '/' + stringDay1 + '/' + stringYear + ',' + stringHour1 + ':'+ stringMinute1 + ':00'
        stringYear =  stringYear2[2] + stringYear2[3]
        arc_stop  = stringMonth2 + '/' + stringDay2 + '/' + stringYear + ',' + stringHour2 + ':'+ stringMinute2 + ':00'

    f = open('./arc_file', 'w')
    line = 'operation=' + operation + '\n'
    f.write(line)
    line = 'dataset=' + dataset + '\n'
    f.write(line)
    line = 'detector=' + detector + '\n'
    f.write(line)
    line = 'level=' + str(level) + '\n'
    f.write(line)
    line = 'filetype=' + filetype + '\n'
    f.write(line)

    if filename != 'NA':
	    line = 'filename=' + filename + '\n'
	    f.write(line)
    else:
    	f.write('tstart=')
    	f.write(arc_start)
    	f.write('\n')
    	f.write('tstop=')
    	f.write(arc_stop)
    	f.write('\n')

    f.write('go\n')
    f.close()


#
#--- for the command is to retrieve: extract data and return the list of the files extreacted
#
    if operation == 'retrieve':
    	cmd = 'echo ' + hakama + ' |arc4gl -U' + dare + ' -Sarcocc -i arc_file'
        os.system(cmd)
        cmd = 'rm ./arc_file'
        os.system(cmd)
#
#--- move the extracted file, if depository is specified
#
        if deposit != './':
    	    cmd = 'mv *.gz ' + deposit + '.'
    	    os.system(cmd)

        xxx = os.listdir(deposit)

        cleanedData = []
        for fout in os.listdir(deposit):
            if fnmatch.fnmatch(fout , '*gz'):

#    	        cmd = 'gzip -d ' + deposit + '/*gz'
    	        cmd = 'gzip -d ' + deposit +  fout
    	        os.system(cmd)
#
#--- run arc4gl one more time to read the file names
#
                f = open('./arc_file', 'w')
                line = 'operation=browse\n'
                f.write(line)
                line = 'dataset=' + dataset + '\n'
                f.write(line)
                line = 'detector=' + detector + '\n'
                f.write(line)
                line = 'level=' + str(level) + '\n'
                f.write(line)
                line = 'filetype=' + filetype + '\n'
                f.write(line)
             
                if filename != 'NA':
	                line = 'filename=' + filename + '\n'
	                f.write(line)
                else:
    	            f.write('tstart=')
    	            f.write(arc_start)
    	            f.write('\n')
    	            f.write('tstop=')
    	            f.write(arc_stop)
    	            f.write('\n')
        
                f.write('go\n')
                f.close()
        
    	        cmd = 'echo ' + hakama + ' |arc4gl -U' + dare + ' -Sarcocc -i arc_file > file_list'
                os.system(cmd)

                f = open('./file_list', 'r')
                data = [line.strip() for line in f.readlines()]
                f.close()
                os.system('rm ./arc_file ./file_list')
#
#--- extreact fits file names and drop everything else
#
                for ent in data:
                    m = re.search('fits', ent)
                    if m is not None:
                        atemp = re.split('\s+|\t+', ent)
                        cleanedData.append(atemp[0])
	
        return cleanedData

#
#--- for the command is to browse: return the list of fits file names
#
    else:
        cmd = 'echo ' + hakama + ' |arc4gl -U' + dare + ' -Sarcocc -i arc_file > file_list'
        os.system(cmd)
        f = open('./file_list', 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()
        os.system('rm ./arc_file ./file_list')
#
#--- extreact fits file names and drop everything else
#
        cleanedData = []
        for ent in data:
            m = re.search('fits', ent)
            if m is not None:
                atemp = re.split('\s+|\t+', ent)
                cleanedData.append(atemp[0])
	
        return cleanedData



#-----------------------------------------------------------------------------------------------------------------------
#--- useDataSeeker: extract data using dataseeker.pl                                                                 ---
#-----------------------------------------------------------------------------------------------------------------------

def useDataSeeker(startYear, startYdate, stopYear, stopYdate, extract, colList):

    "extract data using dataseeker. Input:  start, stop (e.g., 2012:03:13:22:41), the list name (e.g., mtahrc..hrcveto_avg), colnames: 'time,shevart_avg'"

#
#--- set dataseeker input file
#

    (year1, month1, day1, hours1, minute1, second1, ydate1, dom1, sectime1) = tcnv.dateFormatConAll(startYear, startYdate)

    (year2, month2, day2, hours2, minute2, second2, ydate2, dom2, sectime2) = tcnv.dateFormatConAll(stopYear, stopYdate)

    f = open('./ds_file', 'w')
    line = 'columns=' + extract + '\n'
    f.write(line)
    line = 'timestart=' + str(sectime1) + '\n'
    f.write(line)
    line = 'timestop='  + str(sectime2) + '\n'
    f.write(line)
    f.close()

    cmd = 'punlearn dataseeker; dataseeker.pl infile=ds_file print=yes outfile=./ztemp.fits'
    os.system(cmd)
    cmd = 'dmlist "./ztemp.fits[cols '+ colList + '] " opt=data > ./zout_file'
    os.system(cmd)

    f = open('./zout_file', 'r')
    data = [line.strip() for line in f.readlines()]
    f.close()

    os.system('rm ./ds_file  ./ztemp.fits ./zout_file')

    return data

#---------------------------------------------------------------------------------------------------
#-- isFileEmpty: check whether file exists and then check whether the file is empty or not       ---
#---------------------------------------------------------------------------------------------------

def isFileEmpty(file):

    """
     check whether file exists and then check whether the file is empty or not 
     Input: file  ---- file name
     Output: 0    ---- no file or the file is empty
             1    ---- the file exists and it is not empty
    """
#
#--- first check whether file exists
#
    chk  = chkFile(file)
    if chk == 0:
        return 0
    else:
#
#--- then check whether the file is empty or not
#
        f    = open(file, 'r')
        data = f.read()
        f.close()
        data = data.strip()
        test = data.replace('\s+|\t+|\n+', '')
        if test != '':
            return 1
        else:
            return 0

#---------------------------------------------------------------------------------------------------
#--- readFile: check whether a file exist before reading the file                                ---
#---------------------------------------------------------------------------------------------------

def readFile(file):

    """
    check whether a file exist before reading the file
    Input:      file
    Output:     data  --- file content
    """

    data = []
    chk  = isFileEmpty(file)
    if chk > 0:
        f    = open(file, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()

    return data

#---------------------------------------------------------------------------------------------------
#--- removeDuplicate: remove duplicated lines from a file or list                               ----
#---------------------------------------------------------------------------------------------------

def removeDuplicate(file, chk = 1, dosort=1):

    """
     remove duplicated lines from a file or list
     Input: file --- if chk >= 1: file name
                     if chk == 0: a list
            dosort   if 0 No sorting, else do sortign
     Output:         if chk == 0: cleaned file
                     if chk >  0: new -- a cleaned list
    """
    if chk == 1 and chkFile(file) == 0:
        return [] 
    else:
        new = []
        if chk == 1:
            f    = open(file, 'r')
            data = [line.strip() for line in f.readlines()]
            f.close()
        else:
            data = file
    
        if len(data) > 1:
    
            if dosort > 0:
                data.sort()
    
            first = data[0]
            new = [first]
            for i in range(1, len(data)):
                ichk = 0
                for comp in new:
                    if data[i] == comp:
                        ichk = 1
                        break
                if ichk == 0:
                    new.append(data[i])
    
            if chk == 1:
                f = open(file, 'w')
                for ent in new:
                    f.write(ent)
                    f.write('\n')
                f.close()
            else:
                return new
        else:
            if chk == 1:
                pass
            else:
                return data

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def avgAndstd(data):

    n    = len(d)
    if n > 0:
        try:
            d    = numpy.array(data)
            avg  = sum(d)/n
            std  = math.sqrt(sum((x - avg)**2 for x in d) / n)
    
            return(avg, std)
        except:
            return(-999, -999)
    else:
        return(0, 0)

#---------------------------------------------------------------------------------------------------
#--- processCMD: process the command with the error check                                        ---
#---------------------------------------------------------------------------------------------------

def processCMD(cmd):

    """
     process the command with the error check
     Input:     cmd --- command line
     Output:    1   --- if there is error
                0   --- the command proccessed without a problem
    """
    prog = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
#
#--- Returns (stdoutdata, stderrdata): stdout and stderr are ignored, here
#
    prog.communicate()

    if prog.returncode:
#        raise Exception('program returned error code {0}'.format(prog.returncode))
        return 1
    else:
        return 0

#---------------------------------------------------------------------------------------------------
#--- rm_file: remove file                                                                         --
#---------------------------------------------------------------------------------------------------

def rm_file(file):
    """
    remove file
    Input:  file --- a name of file to be removed
    Output: none
    """
    chk = chkFile(file)
    if chk > 0:
        cmd = 'rm -rf ' + file
        processCMD(cmd)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

#def isLeapYear(year):
#
#    """
#    chek the year is a leap year
#    Input:year   in 4 digit
#    
#    Output:   0--- not leap year
#              1--- yes it is leap year
#    """
#
#    chk = 4.0 * int(0.25 * year)
#    if float(year) == chk:
#        return 1
#    else:
#        return 0
#

#---------------------------------------------------------------------------------------------------
#-- mk_empty_dir: empty the existing directory. if it doesnot exist, create an empty directory    --
#---------------------------------------------------------------------------------------------------

def mk_empty_dir(name):

    """
    empty the existing directory. if it doesnot exist, create an empty directory
    Input:  name    --- the name of direcotry
    Output: <chk>   --- if it is created/emptyed, return 1 otherwise 0
    """

    try:
        chk = chkFile(name)
        if chk > 0:
            cmd = 'rm -rf ' + name
            os.system(cmd)

        cmd = 'mkdir ' + name
        os.system(cmd)
        return 1
    except:
        return 0

#---------------------------------------------------------------------------------------------------
#-- get_val: read data and return a list of the data, or the first entry                         ---
#---------------------------------------------------------------------------------------------------

def  get_val(file, dir= '', lst=1):

    """
    read data and return a list of the data, or the first entry 
    Input:  file    --- the name of the file
            dir     --- the directory which the file is kept. if it is '', assume file is the full path
            lst     --- if it is 1 and only one entry, return a line, not a list
    Output: data    --- a list of the data, or data[0], if list != 1
    """

    try:
        if dir == '':
            f = open(file, 'r')
        else:
            line = dir + '/' + file
            f = open(line, 'r')
    
        data  = [line.strip() for line in f.readlines()]
        f.close()
    except:
        if lst == 1:
            return ""
        else:
            return []

#
#--- if only one entry, check whether it want to return as a list or a line
#
    if len(data) == 1:
        if lst == 1:
            return data[0]
        else:
            return data
#
#--- return normal list
#
    elif len(data) > 1:
        return data
#
#--- if it is empty, return ""
#
    else:
        if lst == 1:
            return ""
        else:
            return []

#---------------------------------------------------------------------------------------------------
#-- create_list_from_dir: create a list of files for a given directory                           ---
#---------------------------------------------------------------------------------------------------

def create_list_from_dir(fdir):
#
#--- CHECK WHETHER THIS FUNCTION IS WORKING!!!!
#
    """
    create a list of files for a given directory
    Input:  fdir    --- the directory name
    Output: data    --- a list of files in the directory
    """
    
    try:
        cmd = 'ls -rd ' + fdir + '>' + tempout
        os.system(cmd)
        data = get_val(tempout)
        mcf.rm_file(tempout)
        if isinstance(data, list):
            pass
        else:
            data = [data]
    except:
        data = []
   
    return data

#---------------------------------------------------------------------------------------------------
#-- sort_all_list: sort all lists in "inlist" by the list at the postion of "pos"                ---
#---------------------------------------------------------------------------------------------------

def sort_all_list(inlist, pos=0):

    """
    sort all lists in "inlist" by the list at the postion of "pos"
    Input:  inlist --- a list of lists. All list must have the same dimension. If not 
                       an empty list will be returned
            pos    --- a position of the list you want to use for the sorting. default = 0
    Output: sorted_lists --- a list of listed sorted by a list at "pos" position
    """
#
#--- check inlist is actually a list
#
    if isinstance(inlist, list):
        no_list = len(inlist)

        if no_list == 0:
            return []
#
#--- if the indicated position is wrong, just return the original list
#
        elif pos > no_list -1:
            return inlist
#
#--- for the case inlist contains only one list
#
        elif no_list == 1:
            if isinstance(inlist[0], list):
                inlist.sort()
                return  inlist
            else:
                return []
#
#--- for the case inlist contains more than one list
#
        elif no_list > 1:
            if isinstance(inlist[pos], list):
                chk = 0
                data    = numpy.array(inlist[pos])
                tlen    = len(data)
                sorted_index = numpy.argsort(data)
                sorted_lists = []
                for i in range(0, no_list):
#
#--- if the other entries are not lists or the length of the list is different
#--- from the list of "pos", it will return empty list
#
                    if isinstance(inlist[i], list):
                        if len(inlist[i]) == tlen:
                            data = numpy.array(inlist[i])
                            sorted_data = data[sorted_index]

                        else:
                            chk = 1
                            sorted_data = inlist[i]
                    else:
                        chk = 1
                        sorted_data = inlist[i]

                    sorted_lists.append(sorted_data)

                if chk == 0:
                    return sorted_lists
                else:
                    return []
            else:
#
#--- for the case, content of inlist is not lists
#
                if isinstance(inlist, list):
                    return inlist.sort()
                else:
                    return []
    else:
        return inlist

#---------------------------------------------------------------------------------------------------
#-- find_missing_elem: compare two lists and find elements in list1 which are not in list2        --
#---------------------------------------------------------------------------------------------------

def find_missing_elem(list1, list2):

    """
    compare two lists and find elements in list1 which are not in list2
    Input: list1 / list2    ---- two lists to be compared
    Output: mlist           ---- a list which contains elemnets which exist in list1 but not in list2
    """
    mlist = []
    if len(list1) == 0:
        return mlist
    elif len(list2) == 0:
        return list1
    else:
        for ent in list1:
            chk = 0
            for comp in list2:
                if ent == comp:
                        chk = 1
                        break
            if chk == 0:
                mlist.append(ent)
    
        return mlist 

#---------------------------------------------------------------------------------------------------
#-- separate_data_to_arrys: separate a table data into arrays of data                             --
#---------------------------------------------------------------------------------------------------

def separate_data_to_arrys(data):

    """
    separate a table data into arrays of data
    Input:  data    --- a data table
    Output: coldata --- a list of lists of each column
    """

    atemp = re.split('\s+|\t+', data[0])
    alen  = len(atemp)

    coldata = [[] for x in range(0, alen)]
    
    for ent in data:
        atemp = re.split('\s+|\t+', ent)
        for j in range(0, alen):
            coldata[j].append(atemp[j])

    return coldata

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def file_wild_serach(dir, name):

    """
    check the directory "dir" contains file(s) which name contain "name". if you want to find
    whether the directory contains data1 data2 etc, name is "data" more like ls data*
    Input:  dir     --- direcotry name
            name    --- name element you are looking for in the file name
    Output: 1       --- if the file name contains the <name>"
            0       --- the file name does not contains <name> or no files in that directory
    """

    if os.listdir(dir):
        cmd = 'ls ' + dir + '/* > ' + tempout
        os.system(cmd)
        test = open(tempout).read()
        rm_file(tempout)
        m1   = re.search(name, test)
        if m1 is not None:
            return 1
        else:
            return 0
    else:
        return 0

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def check_file_with_name(dir, part):

    try:
        if os.listdir(dir) == []:
            return False
    
        else:
            cmd = 'ls ' + dir + '> ' +  tempout
            os.system(cmd)
    
            f    = open(tempout, 'r')
            line = f.read()
         
            cmd = 'rm ' + tempout
            os.system(cmd)
    
            mc   = re.search(part, line)
            if mc is not None:
                return True
            else:
                return False
    except:
        return False


