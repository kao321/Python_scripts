#!/usr/bin/env /proj/sot/ska/bin/python

#########################################################################################################################################
#                                                                                                                                       #
#           plotting_routine_set.py: contain plotting routines                                                                          #
#                                                                                                                                       #
#                                                                                                                                       #
#--- single panel, single data set:                                     plot_single_panel                                               #
#                                                                                                                                       #
#--- multiple panels with single data set for each panel:               plot_multi_panel                                                #
#                                                                                                                                       #
#--- multiple pnaels with specified column #:                           plot_multi_columns                                              #
#                                                                                                                                       #
#--- single panel with multiple datasets:                               plot_multi_entries                                              #
#                                                                                                                                       #
#--- single panel with single data set with moving average envelope:    plot_moving_average                                             #
#       this must use with     moving_avg = fmv.find_moving_average(xdata, ydata, 50.0, 5)                                              #
#                                                                                                                                       #
#--- setting min and max of plotting range                              set_min_max                                                     #
#                                                                                                                                       #
#       author: t. isobe (tisobe@cfa.harvard.edu)                                                                                       #
#                                                                                                                                       #
#       last update: Jun 19, 2014                                                                                                       #
#                                                                                                                                       #
#########################################################################################################################################

import os
import sys
import re
import string

import matplotlib as mpl

if __name__ == '__main__':

    mpl.use('Agg')

from pylab import *
import matplotlib.pyplot       as plt
import matplotlib.font_manager as font_manager
import matplotlib.lines        as lines
#
#--- reading directory list
#
path = '/data/mta/Script/Python_script2.7/dir_list_py'

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
import find_moving_average  as fmv
import robust_linear        as robust


#---------------------------------------------------------------------------------------------------
#--- plot_multi_panel: plots multiple data in separate panels                                    ---
#---------------------------------------------------------------------------------------------------

def plot_multi_panel(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, xname, yname, entLabels, outname, yerror=0, fsize = 9, psize = 2.0, marker = 'o', pcolor =7, lcolor=7,lsize=0, resolution=100, linefit=0, connect=0):

    """
    This function plots multiple data in separate panels
    Input:  xmin, xmax  plotting range of x axis
            xSets:      a list of lists containing x-axis data
            ySets:      a list of lists containing y-axis data
            yMinSets:   a list of ymin 
            yMaxSets:   a list of ymax
            xname:      x axis label
            yname:      y axis label
            entLabels:  a list of the names of each data
            outname:    a name of plotting file
            yerror:     a list of lists of error on y, or if it is '0' no error bar on y, default = 0
            fsize:      font size, default = 9
            psize:      plotting point size, default = 2.0
            marker:     marker shape, defalut = 'o'
            pcolor:     color of the point, default= 7 ---> 'black'
            lcolor:     color of the fitted line, default = 7 ---> 'black'
                colorList = ('blue', 'red', 'green', 'aqua', 'fuchsia','lime', 'maroon', 'black', 'olive', 'yellow')
            lsize:      fitted line width, defalut = 1
            resolution: plotting resolution in dpi, default = 100
            linefit:    if 1, linear line is fitted, default: 0
            connect:    connected line size. if it is '0', no connected line

    Output: a png plot: outname
    """
#
#--- set line color list
#
    colorList = ('blue', 'red', 'green', 'aqua', 'fuchsia','lime', 'maroon', 'black', 'olive', 'yellow')
#
#--- clean up the plotting device
#
    plt.close('all')
#
#---- set a few parameters
#
    mpl.rcParams['font.size'] = fsize 
    props = font_manager.FontProperties(size=9)
    plt.subplots_adjust(hspace=0.08)

    tot = len(entLabels)
#
#--- start plotting each data
#
    for i in range(0, tot):
        axNam = 'ax' + str(i)
#
#--- setting the panel position
#
        j = i + 1
        if i == 0:
            line = str(tot) + '1' + str(j)
        else:
            line = str(tot) + '1' + str(j) + ', sharex=ax0'
            line = str(tot) + '1' + str(j)

        exec "%s = plt.subplot(%s)"       % (axNam, line)
        exec "%s.set_autoscale_on(False)" % (axNam)      #---- these three may not be needed for the new pylab, but 
        exec "%s.set_xbound(xmin,xmax)"   % (axNam)      #---- they are necessary for the older version to set

        exec "%s.set_xlim(xmin=xmin, xmax=xmax, auto=False)" % (axNam)
        exec "%s.set_ylim(ymin=yMinSets[i], ymax=yMaxSets[i], auto=False)" % (axNam)

        xdata  = xSets[i]
        ydata  = ySets[i]
  
#
#---- actual data plotting
#
        p, = plt.plot(xdata, ydata, color=colorList[pcolor], marker= marker, markersize=psize, lw =connect)

        if yerror != 0:
            p, = plt.errorbar(xdata, ydata, yerr=yerror[i], lw = 0, elinewidth=1)

        if linefit > 0:
            (sint, slope, serr) = robust.robust_fit(xdata, ydata)
            start = sint + slope * xmin
            stop  = sint + slope * xmax
            p, = plt.plot([xmin, xmax],[start,stop], color=colorList[lcolor], lw =lsize)

#
#--- add legend
#
        leg = legend([p],  [entLabels[i]], prop=props, loc=2)
        leg.get_frame().set_alpha(0.5)

        exec "%s.set_ylabel(yname, size=fsize)" % (axNam)

#
#--- add x ticks label only on the last panel
#
    for i in range(0, tot):
        ax = 'ax' + str(i)

        if i != tot-1: 
            exec "line = %s.get_xticklabels()" % (ax)
            for label in  line:
                label.set_visible(False)
        else:
            pass

    xlabel(xname)

#
#--- set the size of the plotting area in inch (width: 10.0in, height 2.08in x number of panels)
#
    fig = matplotlib.pyplot.gcf()
    height = (2.00 + 0.08) * tot
    fig.set_size_inches(10.0, height)
#
#--- save the plot in png format
#
    plt.savefig(outname, format='png', dpi=resolution)






#---------------------------------------------------------------------------------------------------
#--- plot_multi_columns: plots multiple data in separate panels with multiple columns            ---
#---------------------------------------------------------------------------------------------------

def plot_multi_columns(xmin, xmax, yMinSets, yMaxSets, xSets, ySets, xname, yname, entLabels, outname, yerror=0, colnum =1, fsize = 9, psize = 2.0, marker = 'o', pcolor =7, lcolor=7,lsize=0,resolution=100, linefit=0, connect =  0):

    """
    This function plots multiple data in separate panels with multiple columns
    Input:  xmin, xmax  plotting  range of x axis
            xSets:      a list of lists containing x-axis data
            ySets:      a list of lists containing y-axis data
            yMinSets:   a list of ymin 
            yMaxSets:   a list of ymax
            xname:      a label on x
            yname:      a label on y. if it is a list, each y axis is labeled. otherwise only left most ones are labelled. 
            entLabels:  a list of the names of each data
            outname:    a name of plotting file
            yerror:     a list of lists of y error, if it is '0', no error bar, default = 0
            colnum:     a number of columns, default = 1
            fsize:      font size, default = 9
            psize:      plotting point size, default = 2.0
            marker:     marker shape, defalut = 'o'
            pcolor:     color of the point, default= 7 ---> 'black'
            lcolor:     color of the fitted line, default = 7 ---> 'black'
                colorList = ('blue', 'red', 'green', 'aqua', 'fuchsia','lime', 'maroon', 'black', 'olive', 'yellow')
            lsize:      fitted line width, default = 1
            resolution: plotting resolution in dpi, default = 100
            linefit:    if 1, linear line is fitted, default = 0
            connect:    connected line size. if it is '0', no connected line

    Output: a png plot: outname
    """
#
#--- set line color list
#
    colorList = ('blue', 'red', 'green', 'aqua', 'fuchsia','lime', 'maroon', 'black', 'olive', 'yellow')
#
#--- clean up the plotting device
#
    plt.close('all')
#
#---- set a few parameters
#
    mpl.rcParams['font.size'] = fsize
    props = font_manager.FontProperties(size=9)
    plt.subplots_adjust(hspace=0.08)

    tot = len(entLabels)
#
#--- adjust numbers of panels to created if there are not enough data to make n x m shape
#
    pcnt = int(tot/colnum) + 1
#
#---- check yname is a list or a string
#
    if isinstance(yname, list):
        ynshare = 1
    else:
        ynshare = 0

#
#--- start plotting each data
#
    for i in range(0, tot):
        axNam = 'ax' + str(i)
#
#--- setting the panel position
#
        j = i + 1
        if i == 0:
            line = str(pcnt) + str(colnum) + str(j)
        else:
            k = i % colnum
            line = str(pcnt) + str(colnum) + str(j) + ', sharex=ax0'
            line = str(pcnt) + str(colnum) + str(j)

        exec "%s = plt.subplot(%s)"       % (axNam, line)
        exec "%s.set_autoscale_on(False)" % (axNam)      #---- these three may not be needed for the new pylab, but 
        exec "%s.set_xbound(xmin,xmax)"   % (axNam)      #---- they are necessary for the older version to set

        exec "%s.set_xlim(xmin=xmin, xmax=xmax, auto=False)" % (axNam)
        exec "%s.set_ylim(ymin=yMinSets[i], ymax=yMaxSets[i], auto=False)" % (axNam)

        xdata  = xSets[i]
        ydata  = ySets[i]
  
#
#---- actual data plotting
#
        p, = plt.plot(xdata, ydata, color=colorList[pcolor], marker=marker, markersize=psize, lw =connect)

        if yerror != 0:
            p, = plt.errorbar(xdata, ydata, yerr=yerror[i], lw = 0, elinewidth=1)

        if linefit > 0:
            (sint, slope,serror) = robust.robust_fit(xdata, ydata)
            start = sint + slope * xmin
            stop  = sint + slope * xmax
            p, = plt.plot([xmin, xmax],[start,stop], color=colorList[lcolor], lw =lsize)

        if i == tot-2:
            xlabel(xname)
#
#--- add legend
#
        leg = legend([p],  [entLabels[i]], prop=props, loc=2)
        leg.get_frame().set_alpha(0.5)
 
        if ynshare == 0:
            if i % colnum == 0:
                exec "%s.set_ylabel(yname, size=fsize)" % (axNam)
        else:
            exec "%s.set_ylabel(yname[i], size=fsize)" % (axNam)

#
#--- add x ticks label only on the panels of the last row
#
    for i in range(0, tot):
        ax = 'ax' + str(i)

        chk = 0
        for k in range(0, colnum):
            kp = k + 1
            if i == tot-kp: 
                chk += 1

        if chk == 0:
            exec "line = %s.get_xticklabels()" % (ax)
            for label in  line:
                label.set_visible(False)
        else:
            pass


#
#--- set the size of the plotting area in inch (width: 10.0in, height 2.0in x rows of panels)
#
    fig = matplotlib.pyplot.gcf()
    height = (2.5) * int(tot /colnum) 
    fig.set_size_inches(10.0, height)
#
#--- save the plot in png format
#
    plt.savefig(outname, format='png', dpi=resolution)


#-----------------------------------------------------------------------------------------------
#-- plot_multi_entries: plotting multiple data in a single panel                             ---
#-----------------------------------------------------------------------------------------------

def plot_multi_entries(xmin, xmax, ymin, ymax, xSets, ySets, xname, yname, entLabels, outname, yerror = 0,fsize = 9, psize = 2.0,lsize=0, resolution=100, linefit=0, connect=0):

    """
    This function plots multiple data in a single panel.
    Input:  xmin, xmax, ymin, ymax: plotting area
            xSets:      a list of lists containing x-axis data
            ySets:      a list of lists containing y-axis data
            xname:      a name of x-axis
            yname:      a name of y-axis
            entLabels:  a list of the names of each data
            outname:    a name of plotting file
            yerror:     a list of lists of y error, if it is '0', no error bar, default = 0
            fsize:      font size, default = 9
            psize:      plotting point size, default = 2.0
            lsize:      fitted line width, default = 1
            resolution: plotting resolution in dpi
            linefit  --- if it is 1, fit a line estimated by robust method
            connect:    connected line size. if it is '0', no connected line

    Output: a png plot: out.png
    """

    colorList = ('blue', 'green', 'red', 'aqua', 'lime', 'fuchsia', 'maroon', 'black', 'yellow', 'olive')
    markerList = ('o',    '*',     '+',   '^',    's',    'D',       '1',      '2',     '3',      '4')
    plt.close('all')
#
#---- set a few parameters
#
    mpl.rcParams['font.size'] = fsize
    props = font_manager.FontProperties(size=9)
    plt.subplots_adjust(hspace=0.08)

#
#---- set a panel
#
    ax = plt.subplot(111)
    ax.set_autoscale_on(False)      #---- these three may not be needed for the new pylab, but 
    ax.set_xbound(xmin,xmax)        #---- they are necessary for the older version to set

    ax.set_xlim(xmin=xmin, xmax=xmax, auto=False)
    ax.set_ylim(ymin=ymin, ymax=ymax, auto=False)

    tot = len(entLabels)
#
#--- start plotting each data set
#
    lnamList = []
    for i in range(0, tot):
        xdata  = xSets[i]
        ydata  = ySets[i]

        if tot > 1:
            lnam = 'p' + str(i)
            lnamList.append(lnam)
            exec "%s, = plt.plot(xdata, ydata, color=colorList[i], lw =lsize , marker=markerList[i], markersize=psize, label=entLabels[i])" % (lnam)

            if yerror != 0:
                exec "%s, = plt.errorbar(xdata, ydata, yerr=yerror[i], lw = 0, elinewidth=1)" % (lnam)

            if linefit > 0:
                (sint, slope,serror) = robust.robust_fit(xdata, ydata)
                start = sint + slope * xmin
                stop  = sint + slope * xmax
                exec "%s, = plt.plot([xmin, xmax],[start,stop], color=colorList[i], lw =connect)" % (lnam)

        else:
#
#--- if there is only one data set, ignore legend
#
            plt.plot(xdata, ydata, color=colorList[i], lw =connect , marker='o', markersize=psize)

            if yerror != 0:
                p, = plt.errorbar(xdata, ydata, yerr=yerror[i], lw = 0, elinewidth=1)

            if linefit > 0:
                (sint, slope,serror) = robust.robust_fit(xdata, ydata)
                start = sint + slope * xmin
                stop  = sint + slope * xmax
                plt.plot([xmin, xmax],[start,stop], color=colorList[i], lw =lsize )

#
#--- add legend
#
    if tot > 1:
        line = '['
        for ent in lnamList:
            if line == '[':
                line = line + ent
            else:
                line = line +', ' +  ent
        line = line + ']'

        exec "leg = legend(%s,  entLabels, prop=props)" % (line)
        leg.get_frame().set_alpha(0.5)

    ax.set_xlabel(xname, size=fsize)
    ax.set_ylabel(yname, size=fsize)


#
#--- set the size of the plotting area in inch (width: 10.0in, height 5.0in)
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10.0, 5.0)
#
#--- save the plot in png format
#
    plt.savefig(outname, format='png', dpi=resolution)


#---------------------------------------------------------------------------------------------------
#-- plot_moving_average: plotting moving average and upper and lower envelops for a given data   ---
#---------------------------------------------------------------------------------------------------

def plot_moving_average(xmin, xmax, ymin, ymax, x, y, moving_avg, xname, yname,  outname, resolution=100):

    """
     plotting bias data, moving average, top and bottom envelops to the data
     this must use with moving_avg = fmv.find_moving_average(xdata, ydata, 50.0, 5)
     Input:     xmin / xmax
                ymin / ymax
                x          --- independent variable
                y          --- dependent varialbes
                moving_avg --- a list of list containing:
                    [xcent, movavg, sigma, min_sv, max_sv, y_avg, y_min, y_max, y_sig]
                outname    --- output name
                ccd        --- ccd #
                quad       --- quad #
    Output:     png plots named: outname
    """
#
#--- extract moving average etc data from list
#
    mx = moving_avg[0]      #---- moving average x
    my = moving_avg[1]      #---- moving average y
    ma = moving_avg[5]      #---- moving average polinomial fit
    mb = moving_avg[6]      #---- lower envelop estimate
    mt = moving_avg[7]      #---- upper envelop estimate
#
#--- y range is set to the average +/- 4.0 * std
#
    (ymean, ystd) = mcf.avgAndstd(y)

    dist  = 4.0 * ystd
    ymin  = ymean - dist
    ymin  = round(ymin, 2)
    ymax  = ymean + dist
    ymax  = round(ymax, 2)
#
#--- clean up all plotting param
#
    plt.close('all')
#
#---- set a few parameters
#
    mpl.rcParams['font.size'] = 9
    props = font_manager.FontProperties(size=9)
    plt.subplots_adjust(hspace=0.08)
#
#---- set a panel
#
    ax = plt.subplot(111)
    ax.set_autoscale_on(False)      #---- these three may not be needed for the new pylab, but 
    ax.set_xbound(xmin,xmax)        #---- they are necessary for the older version to set

    ax.set_xlim(xmin=xmin, xmax=xmax, auto=False)
    ax.set_ylim(ymin=ymin, ymax=ymax, auto=False)
#
#--- original data
#
    p, = plt.plot(x, y, color='black', lw =0 , marker='.', markersize=0.5)
#
#--- moving average
#
    plt.plot(mx, my, color='blue', lw =1 , marker='.', markersize=0.5)
#
#--- moving averge smoothed
#
    plt.plot(mx, ma, color='red', lw =1.5 )
#
#--- lower envelope
#
    plt.plot(mx, mb, color='green', lw =1.5 )
#
#--- upper envelope
#
    plt.plot(mx, mt, color='green', lw =1.5 )
#
#--- add legend
#
    title = 'CCD' + str(ccd) +'_q' + str(quad)

    leg = legend([p],  [title], prop=props, loc=2)
    leg.get_frame().set_alpha(0.5)

    ax.set_xlabel(xname, size=8)
    ax.set_ylabel(yname, size=8)
#
#--- set the size of the plotting area in inch (width: 10.0in, height 5.0in)
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10.0, 5.0)
#
#--- save the plot in png format
#
    plt.savefig(outname, format='png', dpi=resolution)
#
#--- clean up all plotting param
#
    plt.close('all')


#---------------------------------------------------------------------------------------------------
#-- plot_single_panel: plot a single data set on a single panel                                  ---
#---------------------------------------------------------------------------------------------------

def plot_single_panel(xmin, xmax, ymin, ymax, xdata, ydata, yerror, xname, yname, label, outname, fsize = 9, psize = 2.0, marker = 'o', pcolor =7, lcolor=7,lsize=1, resolution=100, linefit=1, connect=0):

    """
    plot a single data set on a single panel
    Input:  xmin    --- min x
            xmax    --- max x
            ymin    --- min y
            ymax    --- max y
            xdata   --- independent variable
            ydata   --- dependent variable
            yerror  --- error in y axis; if it is '0', no error bar
            xname   --- x axis label
            ynane   --- y axis label
            label   --- a text to indecate what is plotted
            outname --- the name of output file
            fsize   ---  font size, default = 9
            psize   ---  plotting point size, default = 2.0
            marker  ---  marker shape, defalut = 'o'
            pcolor  ---  color of the point, default= 7 ---> 'black'
            lcolor  ---  color of the fitted line, default = 7 ---> 'black'
                colorList = ('blue', 'red', 'green', 'aqua', 'fuchsia','lime', 'maroon', 'black', 'olive', 'yellow')
            lsize:      fitted line width, defalut = 1
            resolution-- the resolution of the plot in dpi
            linefit  --- if it is 1, fit a line estimated by robust method
            connect  --- if it is > 0, lsize data point with a line, the larger the value thinker the line
    Output: png plot named <outname>
    """
    colorList = ('blue', 'green', 'red', 'aqua', 'lime', 'fuchsia', 'maroon', 'black', 'yellow', 'olive')
#
#--- fit line --- use robust method
#
    if linefit == 1:
        (sint, slope, serr) = robust.robust_fit(xdata, ydata)
        lslope = '%2.3f' % (round(slope, 3))
#
#--- close everything opened before
#
    plt.close('all')
#
#--- set font size
#
    mpl.rcParams['font.size'] = fsize
    props = font_manager.FontProperties(size=9)
#
#--- set plotting range
#
    ax  = plt.subplot(111)
    ax.set_autoscale_on(False)
    ax.set_xbound(xmin,xmax)
    ax.set_xlim(xmin=xmin, xmax=xmax, auto=False)
    ax.set_ylim(ymin=ymin, ymax=ymax, auto=False)
#
#--- plot data
#
    plt.plot(xdata, ydata, color=colorList[pcolor], marker=marker, markersize=psize, lw = connect)
#
#--- plot error bar
#
    if yerror != 0:
        plt.errorbar(xdata, ydata, yerr=yerror, lw = 0, elinewidth=1)
#
#--- plot fitted line
#
    if linefit == 1:
        start = sint + slope * xmin
        stop  = sint + slope * xmax
        plt.plot([xmin, xmax], [start, stop], color=colorList[lcolor], lw = lsize)
#
#--- label axes
#
    plt.xlabel(xname, size=fsize)
    plt.ylabel(yname, size=fsize)
#
#--- add what is plotted on this plot
#
    xdiff = xmax - xmin
    xpos  = xmin + 0.5 * xdiff
    ydiff = ymax - ymin
    ypos  = ymax - 0.08 * ydiff

    if linefit == 1:
        label = label + ': Slope:  ' + str(lslope)

    plt.text(xpos, ypos, label, size=fsize)

#
#--- set the size of the plotting area in inch (width: 10.0in, height 5 in)
#
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(10.0, 5.0)
#
#--- save the plot in png format
#
    plt.savefig(outname, format='png', dpi=resolution)


#---------------------------------------------------------------------------------------------------
#-- set_min_max: set plotting range                                                              ---
#---------------------------------------------------------------------------------------------------

def set_min_max(xdata, ydata, xtime = 0, ybot = -999):

    """
    set plotting range
    Input:  xdata   ---- xdata
            ydata   ---- ydata
            xtime   ---- if it is >0, it set the plotting range from 1999 to the current in year
            ybot    ---- if it is == 0, the ymin will be 0, if the ymin computed is smaller than 0
    Output: [xmin, xmax, ymin, ymax]
    """

    xmin  = min(xdata)
    xmax  = max(xdata)
    xdiff = xmax - xmin
    xmin -= 0.1 * xdiff
    xmax += 0.2 * xdiff

    if xtime > 0:
        xmin  = 1999
        tlist = tcnv.currentTime()
        xmax  = tlist[0] + 1

    ymin  = min(ydata)
    ymax  = max(ydata)
    ydiff = ymax - ymin
    ymin -= 0.1 * ydiff
    ymax += 0.2 * ydiff

    if ybot == 0:
        if ymin < 0:
            ymin = 0

    return [xmin, xmax, ymin, ymax]

