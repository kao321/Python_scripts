#!/usr/bin/env /proj/sot/ska/bin/python

#################################################################################################
#                                                                                               #
#    this file contains functions related time format conversions.                              #
#                                                                                               #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                               #
#       last update May 30, 2014                                                                #
#                                                                                               #   
#################################################################################################

import time
import re
import sys

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
#--- mta common functions
#
import mta_common_functions as mtac


#------------------------------------------------------------------------------------------------------
#--- dateFormatConAll: equivalent of dateFormatCon, but also add dom and seconds from Jan 1, 1998   ---
#------------------------------------------------------------------------------------------------------

def dateFormatConAll(elm, *arg):

    "equivalent of dateFormatCon, but also add dom and seconds from Jan 1, 1998"

    (year, month, date, hours, minutes, seconds, ydate) = dateFormatCon(elm, *arg)

    dom     = findDOM(year, month, date, hours, minutes, seconds)
    sectime = convertDateToCTime(year, month, date, hours, minutes, seconds)

    return  (year, month, date, hours, minutes, seconds, ydate, dom, sectime)


#--------------------------------------------------------------------------------------------------------------------------
#-- dateFormatCon: convert various date format into a tuple of (year, month, day, hours, minutes, second, ydate)        ---
#--------------------------------------------------------------------------------------------------------------------------

def dateFormatCon(elm, *arg):

    "convert various date format into a tuple of (year, month, day, hours, minutes, second, ydate) "

    if mtac.chkNumeric(elm):             #--- for the case, inputs are digits, e.g, year, month, ...

        year = elm
        cnt = len(arg)
        if cnt == 1:
            ydate   = arg[0]
#
#--- check whether ydate is a fractional ydate or not, if so, compute hours, minutes, and second
#
            diff = arg[0] - int(ydate)
            if diff == 0:
                hours   = 0
                minutes = 0
                seconds = 0
            else:
                temp = 24 * diff
                hours   = int(temp)
                temp2 = 60 * (temp - hours)
                minutes = int(temp2)
                temp3 = 60  * (temp2 - minutes)
                seconds = int(temp3)

            (month, day) = changeYdateToMonDate(year, int(ydate))
        elif cnt == 2:
            month   = arg[0]
            day     = int(arg[1])

            ydate   = findYearDate(year, month, day)
        elif cnt == 4:
            ydate   = arg[0]
            hours   = arg[1]
            minutes = arg[2]
            seconds = arg[3]

            (month, day) = changeYdateToMonDate(year, int(ydate))
        elif cnt == 5:
            month   = arg[0]
            day     = arg[1]
            hours   = arg[2]
            minutes = arg[3]
            seconds = arg[4]

            ydate   = findYearDate(year, month, day)
        else:
            ydate   = 1
            month   = 1
            day     = 1
            hours   = 0
            minutes = 0
            seconds = 0


    else:
        atemp = re.split('\s+', elm)
        m = re.search('\/', elm)
        m2= re.search('\,', elm)
        n = re.search('T',  elm)

        if len(atemp) == 6:                 #--- for the case, e.g: Wed Apr  4 10:34:32 EDT 2012
            year    = int(atemp[5])
            month   = changeMonthFormat(atemp[1])
            day     = int(atemp[2])
            btemp   = re.split(':', atemp[3])
            hours   = int(btemp[0])
            minutes = int(btemp[1])
            seconds = int(btemp[2])

            yday    =  float(day) + float(hours/24.0) + float(minutes/1440.0) + float(seconds/86400)
            ydate   = findYearDate(year, month, yday)

        elif (m is not None) and (m2 is not None):     #--- for the case, e.g. 03/28/12,00:00:00
            atemp   = re.split('\,', elm)
            btemp   = re.split('\/', atemp[0])
            year    = int(btemp[2])

            if year > 90 and year < 1900:
                year += 1900
            elif year < 90:
                year += 2000

            month   = int(btemp[0])
            day     = int(btemp[1])

            btemp   = re.split(':', atemp[1])
            hours   = int(btemp[0])
            minutes = int(btemp[1])
            seconds = int(btemp[2])

            yday    =  float(day) + float(hours/24.0) + float(minutes/1440.0) + float(seconds/86400)
            ydate   = findYearDate(year, month, yday)

        elif n is not None:                 #--- for the case, e.g. 03/28/12T00:00:00
            atemp   = re.split('T', elm)
            m1      = re.search('\/', elm)
            m2      = re.search('-', elm)
            if m1 is not None:
                btemp   = re.split('\/', atemp[0])
                year    = int(btemp[2])
    
                if year > 90 and year < 1900:
                    year += 1900
                elif year < 90:
                    year += 2000
    
                month   = int(btemp[0])
                day     = int(btemp[1])

            elif m2 is not None:
                btemp = re.split('-', atemp[0])
                year  = int(btemp[0])
                month = int(btemp[1])
                day   = int(btemp[2])
    
            btemp   = re.split(':', atemp[1])
            hours   = int(btemp[0])
            minutes = int(btemp[1])
            seconds = int(btemp[2])

            yday    =  float(day) + float(hours/24.0) + float(minutes/1440.0) + float(seconds/86400)
            ydate   = findYearDate(year, month, yday)


        else:
            atemp = re.split(':', elm)
            if len(atemp) == 6:                 #--- for the case yyy:mm:dd:hh:mm:ss
                year    = int(atemp[0])
                month   = int(atemp[1])
                day     = int(atemp[2])
                hours   = int(atemp[3])
                minutes = int(atemp[4])
                seconds = int(atemp[5])
    
                yday    =  float(day) + float(hours/24.0) + float(minutes/1440.0) + float(seconds/86400)
                ydate   = findYearDate(year, month, yday)

            else:                               #--- for the cae yyyy:yday:hh:mm:ss
                year    = int(atemp[0])
                ydate   = int(atemp[1])
                hours   = int(atemp[2])
                minutes = int(atemp[3])
                seconds = int(atemp[4])
                [month, day] = changeYdateToMonDate(year, ydate)
    
                yday    =  float(day) + float(hours/24.0) + float(minutes/1440.0) + float(seconds/86400)
                ydate   = findYearDate(year, month, yday)

    line = (year, month, day, hours, minutes, seconds, ydate)
    return line

#----------------------------------------------------------------------------------------------------------------------------------------
#-- findDOM: find Chandra Days of Mission (DOM)                                                                                        --
#----------------------------------------------------------------------------------------------------------------------------------------

def findDOM(year, *arg):

    "for a given year, ydate (or month:day), hour, minutes, and seconds (either string or ints), return Chandra Days of Mission (DOM) "

    (year, month, day, hours, minutes, seconds, ydate)  = dateFormatCon(year, *arg)

    dom = ydate + hours / 24.0 + minutes / 1440.0 + seconds / 86400.0

    if(year == 1999):
        dom -= 202
    elif(year >= 2000):
        add = int ((year - 1997) / 4 )
        dom = dom + 163 + (year - 2000) * 365 + add
    else:
        dom = 0

    return dom


#----------------------------------------------------------------------------------------
#--- DOMtoYdate: change time fromat from DOM to Year and Ydate                        ---
#----------------------------------------------------------------------------------------

def DOMtoYdate(dom):

    "change time fromat from DOM to Year and Ydate"

    dom += 202
    year = 1999
    found = 0
    while (found == 0):
        chk = 4.0 * int(0.25 * year)
        if chk == year:
            base = 366
        else:
            base = 365
        
        dom -= base
        if dom < 0:
            ydate = dom + base
            found = 1
            break

        year += 1

    return (year, ydate)




#----------------------------------------------------------------------------------------
#-- changeMonthFormat: change manth format from digit to letter or letter to digit     --
#----------------------------------------------------------------------------------------

def changeMonthFormat(month = 'NA'):

    "for a given month in either digit or letters (e.g. 'Jan'), return the month in letters or digit"

    m_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    if str.isdigit(str(month)):
        position = month - 1
        if(position < 0 or position > 11):
            cmonth = 'NA'
        else:
            cmonth = m_list[position]
    else:
        cmonth = 'NA'
        for dmonth in range(0, 12):
            if str.lower(str(m_list[dmonth])) == str.lower(str(month)):
                cmonth = dmonth + 1
                break

    return cmonth


#----------------------------------------------------------------------------------------
#--- findYearDate: for a given year, month, and date, return year date                ---
#----------------------------------------------------------------------------------------

def findYearDate(year, *arg):

    "for a given year, month, and date, return year date"

    m_add = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]

    if str.isdigit(str(year)):
        month = arg[0]
        day   = arg[1]
    else:
        atemp = re.split(':', year)
        year  = int(atemp[0])
        month = int(atemp[1])
        day   = float(atemp[2])

    ydate = day + m_add[month -1]

    chk   = 4 * int(0.25 * year)
    if(chk == year and month > 2):
        ydate = ydate + 1

    return ydate

#--------------------------------------------------------------------------------------------------------------------
#--    convertDateToCTime: for a given time (in various format), return time passed from Jan 1, 1998              ---
#--------------------------------------------------------------------------------------------------------------------

def convertDateToCTime(year, *arg):

    "for a given time (in various format), return time passed from Jan 1, 1998"

    (year, month, day, hours, minutes, seconds, ydate)  = dateFormatCon(year, *arg)

    add = int ((year - 1997) / 4 )

    today = 365 * (year - 1998) + ydate + add - 1

    return 86400 * today + 3600 * hours + 60 * minutes + seconds


#---------------------------------------------------------------------------------------------------------------------
#--- convertDateToTime2: for a given year, month, date, hours, minutes, and seconds, return time passed from Jan 1, 1998
#---------------------------------------------------------------------------------------------------------------------

def convertDateToTime2(year, month, date, hours = 0, minutes = 0, seconds = 0):

    "for a given year, month, date, hours, minutes, and seconds, return time passed from Jan 1, 1998"

    ydate = int(findYearDate(year, month, date))

    time1998 = convertDateToCTime(year, ydate, hours, minutes, seconds)

    return time1998

#-------------------------------------------------------------------------------------------------------------
#---  changeYdateToMonDate: for a given year and year date, return month and month date                    ---
#-------------------------------------------------------------------------------------------------------------

def changeYdateToMonDate(year, ydate):

    "for a given year and year date, return month and month date"

    m_sub      = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    m_sub_leap = [0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]    # a list for leap year

    chk = 4 * int(0.25 * year)

    if(chk == year):
        list = m_sub_leap
    else:
        list = m_sub

    for month in range(1, 12):
        date = ydate - list[month]
        if(date <= 0):
            month = month 
            date  = ydate - list[month-1]
            break
        elif(month == 11):
            month = 12

    monthdate = [month, date]

    return monthdate

#-----------------------------------------------------------------------------------------------------------------
#---  convertCtimeToYdate: convert time in seconds from Jan 1 1998 to year:ydate:hour:minutes:seconds format
#-----------------------------------------------------------------------------------------------------------------

def convertCtimeToYdate(stime):

    "convert time in seconds from Jan 1 1998 to year:ydate:hour:minutes:seconds format "

    in_day   = stime / 86400
    day      = int(in_day)

    hr_part  = in_day - day
    in_hr    = 24 * hr_part 
    hour     = int(in_hr)

    min_part = in_hr - hour
    in_min   = 60 * min_part
    minutes  = int(in_min)

    sec_part = in_min - minutes
    seconds  = int(60 * sec_part)
  
    year = 1998
    while True:
        oneyear = 365
        chk     = 4.0 * int (0.25 * year)
        if chk == year:
            oneyear = 366

        if day < oneyear:
            break 

        day -= oneyear
        year += 1

    day += 1

    if day < 10: 
        day = '00'+ str(day)
    elif day < 100: 
        day = '0'+ str(day)

    if hour    < 10: hour    = '0' + str(hour)
    if minutes < 10: minutes = '0' + str(minutes)
    if seconds < 10: seconds = '0' + str(seconds)

    time = str(year) + ':' + str(day) + ':' + str(hour) + ':' + str(minutes) + ':' + str(seconds)

    return time

#------------------------------------------------------------------------------------------------------------------------
#---  axTimeMTAL a simple version of axTime3.                                                                         ---
#------------------------------------------------------------------------------------------------------------------------

def axTimeMTA(input):

    "a shorter version of axTime3. it takes either '2012:045:15:24:31' (' ' is required) or 445620268 format. No leap second correction."

    m = re.search(':', str(input))
    if m is not None:
        time  = re.split(':', str(input))
        year  = int (time[0])
        ydate = int (time[1])
        hour  = int (time[2])
        minute= int (time[3])
        second= int (time[4])

        ntime = convertDateToCTime(year, ydate, hour, minute, second)

    elif str.isdigit(str(input)):
        ntime = convertCtimeToYdate(float (input))
    else:
        ntime = 'NA'


    return ntime

#-----------------------------------------------------------------------------------------------------------------------
#-- currentTime: give back the current time in UTC, Local, Display, and sec1998 format                                --
#-----------------------------------------------------------------------------------------------------------------------

def currentTime(format = 'UTC'):
    
    "give back the current time in UTC, Local (format: [year, mon, day, hours, min, sec, weekday, yday, dst]),  Display (e.g., 'Fri Mar 30 08:30:04 2012'), DOM (Day of Mission), or sec1998 (time passed in seconds from Jan 1, 1998) "

    if str.upper(format) == 'UTC' or str.upper(format) == 'GMT' :
        otime = time.gmtime()
    elif str.upper(format) == 'LOCAL' :
        otime = time.localtime()
    elif str.upper(format) == 'DISPLAY' : 
        otime = time.ctime()
    elif str.upper(format) == 'DOM':
        ctime = time.localtime()
        otime = findDOM(ctime[0], ctime[7], ctime[3], ctime[4], ctime[5])
    elif str.upper(format) == 'SEC1998':
        ctime = time.localtime()
        otime = convertDateToCTime(ctime[0], ctime[7], ctime[3], ctime[4], ctime[5])
    else:
        otime = time.ctime()
    
    return otime


#---------------------------------------------------------------------------------------------------
#-- convert_time_format: convert time format from seconds to in the froma of "2009-03-15T07:13:30" -
#---------------------------------------------------------------------------------------------------

def convert_time_format(stime):

    """
    convert time format from seconds from 1998.1.1. to in the froma of "2009-03-15T07:13:30"
    Input:  time in seconds from 1998.1.1
    Output: time in format of "2009-03-15T07:13:30"
    """

    line= axTimeMTAL(stime)
    year= int(line[0])
    ydate   = int(line[1])
    hours   = int(line[2])
    minutes = int(line[3])
    seconds = int(line[4])

    (month, mdate) =  changeYdateToMonDate(year, ydate)

    if hours < 10:
        hours = '0' + str(hours)
    else:
        hours = str(hours)

    if minutes < 10:
        minutes = '0' + str(minutes)
    else:
        minutes = str(minutes)
    
    if seconds < 10:
        seconds = '0' + str(seconds)
    else:
        hours = str(seconds)
    
    line  = str(year) + '-' + str(month) + '-' + str(mdate) + 'T' + hours + ':' + minutes + ':' + seconds
    
    return line

#-----------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------

#def stimeToDom(stime):
#
#    """
#    convert time in the format of seconds from 1998.1.1 to DO<
#    Input: stime --- seconds from 1998,1,1
#    Output: dom
#    """
#
#    string = convertCtimeToYdate(stime):
#    atemp  = re.split(':', string)
#    year   = int(atemp[0])
#    ydate  = int(atemp[1])
#    hours  = int(atemp[2])
#    minutes= int(atemp[3])
#    seconds= int(atemp[4])
#
#    dom    = findDOM(year, ydate, housrs, minutes, seconds)
#
#    return dom

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

def isLeapYear(year):

    """
    chek the year is a leap year
    Input:year   in full lenth (e.g. 2014, 813)
    
    Output:   0--- not leap year
              1--- yes it is leap year
    """

    chk  = year % 4             #---- evry 4 yrs leap year
    chk2 = year % 100           #---- except every 100 years (e.g. 2100, 2200)
    chk3 = year % 400           #---- excpet every 400 years (e.g. 2000, 2400)

    val  = 0
    if chk == 0:
        val = 1
        if chk2 == 0:
            val = 0
    if chk3 == 0:
        val = 1

    return val


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
    string = convertCtimeToYdate(stime)
    atemp  = re.split(':', string)
    year   = int(atemp[0])
    ydate  = int(atemp[1])
    hours  = int(atemp[2])
    minutes= int(atemp[3])
    seconds= int(atemp[4])

    dom    = findDOM(year, ydate, hours, minutes, seconds)

    return dom

#----------------------------------------------------------------------------------------------------------------------------------------
#-- YdateToDOM: Change from year/ydate to Chandra Days of Mission (DOM)                                                                --
#----------------------------------------------------------------------------------------------------------------------------------------

def YdateToDOM(year, ydate):

    "for a given year, ydate, return Chandra Days of Mission (DOM) "

    dom = ydate

    if(year == 1999):
        dom -= 202
    elif(year >= 2000):
        add = int ((year - 1997) / 4 )
        dom = dom + 163 + (year - 2000) * 365 + add
    else:
        dom = 0

    return dom


#---------------------------------------------------------------------------------------------------
#-- sectoFracYear: convert time in seconds from 1998.1.1 to fractional year                    -----
#---------------------------------------------------------------------------------------------------

def sectoFracYear(stime):

    """
    convert time in seconds from 1998.1.1 to fractional year
    Input: stime    --- time in seconds from 1998.1.1
    Output fractional year
    """

    ltime   = convertCtimeToYdate(stime)
    atemp   = re.split(':', ltime)
    year= int(atemp[0])
    ydate   = int(atemp[1])
    hours   = int(atemp[2])
    minutes = int(atemp[3])
    seconds = int(atemp[4])
    
    chk = 4.0 * int(0.25 * year)
    if chk == year:
        base = 366
    else:
        base = 365
    
    day = ydate + hours / 24.0 + minutes / 1440.0 + seconds / 86400.0
    
    return year + day / base
    
