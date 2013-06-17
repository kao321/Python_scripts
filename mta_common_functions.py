#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################
#                                                                                       #
#   mta_common_functions.py: collections of python functions used by mta                #
#                                                                                       #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                       #
#                                                                                       #
#       last updated: Jun 04, 2013                                                      #
#                                                                                       #
#########################################################################################

import sys
import os
import string
import re
import getpass
import fnmatch

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

        m = re.search('/', inline)
        if m is not  None:
	    if inline[-1] == '/':
		inline = inline[:-1]

            atemp = re.split('/', inline)
        
#
#--- for the case the name starts with "./"
#
            if atemp[0] == '.':
                dir  = './'
		if len(atemp) > 1:
		    for i in range(1, len(atemp) -1):
		        dir = dir + '/' + atemp[i]
                	file = atemp[len(atemp)-1]
		else:
                    file = atemp[1]
		
#
#--- for the case only a file/directory name is given
#
            elif len(atemp) == 0:
                dir  = './'
                file = inline
#
#--- for the case the full path and a file/directory name is given
#
            else:
                dir = '/' +  atemp[1]
                for i in range(2, len(atemp)-1):
                    dir = dir + '/' + atemp[i]
                dir = dir + '/'
     
                file  = atemp[len(atemp)-1]
		if file == '':
                	file  = atemp[len(atemp)-2]
        else:
            dir  = './'
            file = inline
#
#--- for the case directory path and the file/directory name is separately given
#
    else:
        dir  = inline
        file = name

#
#--- now find whetner the file/directory exists in the directory
#
    chk = 0
    try:
        m    = re.search('\/', file)
        if m is not None:
            temp = file.replace('/', '')
            file = temp

        for fout in os.listdir(dir):
            if fout == file:
                chk += 1
                break

    except:
        pass

    if chk > 0:
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
        data = [line.strip() for line in f.readlines()]
        f.close()
        if len(data) > 0:
            return 1
        else:
            return 0

#---------------------------------------------------------------------------------------------------
#--- removeDuplicate: remove duplicated lines from a file or list                               ----
#---------------------------------------------------------------------------------------------------

def removeDuplicate(file, chk = 1):

    """
     remove duplicated lines from a file or list
     Input: file --- if chk == 0: file name
                     if chk >  0: a list
     Output:         if chk == 0: cleaned file
                     if chk >  0: new -- a cleaned list
    """

    new = []
    if chk == 1:
        f    = open(file, 'r')
        data = [line.strip() for line in f.readlines()]
        f.close()
    else:
        data = file

    if len(data) > 1:
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
