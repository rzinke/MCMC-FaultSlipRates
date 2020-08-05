'''
    ** MCMC Incremental Slip Rate Calculator **
    Plotting functions for use with RISeR data structures.

    Rob Zinke 2019, 2020
'''

### IMPORT MODULES ---
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


### STATISTICS ---
## Find outer limits of data for plotting
def findPlotLimits(DspAgeData):
    '''
        Loop through the available data to find the maximum ages and
         displacements to plot.
    '''
    # Initial values
    maxAge = 0
    maxDsp = 0

    # Loop through to find limits
    for datumName in DspAgeData.keys():
        Age = DspAgeData[datumName]['Age']
        Dsp = DspAgeData[datumName]['Dsp']
        # Update max age/displacement
        if Age.ages.max() > maxAge: maxAge = Age.ages.max()
        if Dsp.dsps.max() > maxDsp: maxDsp = Dsp.dsps.max()

    return maxAge, maxDsp


### PLOTTING FUNCTIONS ---
## Whisker plot
def plotWhiskers(DspAgeData,label=False):
    '''
        Plot data as points and whiskers representing the 95 % confidence
         intervals.
    '''
    # Establish plot
    Fig = plt.figure()
    ax = Fig.add_subplot(111)

    # Plot whiskers
    for datumName in DspAgeData:
        datum = DspAgeData[datumName]
        Age = datum['Age']
        Dsp = datum['Dsp']

        # Datum whiskers
        ageMid = Age.median
        ageErr = np.array([[ageMid-Age.lowerLimit],
            [Age.upperLimit-ageMid]])
        dspMid = Dsp.median
        dspErr = np.array([[dspMid-Dsp.lowerLimit],
            [Dsp.upperLimit-dspMid]])

        # Plot datum
        ax.errorbar(ageMid, dspMid, xerr=ageErr,yerr=dspErr,
            color=(0.3,0.3,0.6),marker='o')

        # Label if requested
        if label == True:
            ax.text(ageMid*1.01, dspMid*1.01, datumName)

    return Fig, ax


## Plot rectangles
def plotRectangles(DspAgeData,label=False):
    '''
        Draw rectangular patches representing the 95 % confidence intervals.
    '''
    # Establish plot
    Fig = plt.figure()
    ax = Fig.add_subplot(111)

    # Plot rectangles
    for datumName in DspAgeData:
        datum = DspAgeData[datumName]
        Age = datum['Age']
        Dsp = datum['Dsp']

        # Plot
        ageLower=Age.lowerLimit # load bottom
        dspLower=Dsp.lowerLimit # load left
        boxWidth=Age.upperLimit-ageLower
        boxHeight=Dsp.upperLimit-dspLower
        ax.add_patch(Rectangle((ageLower,dspLower), # LL corner
            boxWidth,boxHeight, # dimensions
            edgecolor=(0.3,0.3,0.6),fill=False,zorder=3))

    return Fig, ax


## Plot raw data (whisker plot)
def plotRawData(DspAgeData,label=False,outName=None):
    '''
        Plot raw data as whisker plot. Whiskers represent 95 % intervals.
    '''
    # Establish figure
    Fig, ax = plotWhiskers(DspAgeData,label=label)

    # Format figure
    maxAge,maxDsp = findPlotLimits(DspAgeData)
    ax.set_xlim([0,1.1*maxAge]) # x-limits
    ax.set_ylim([0,1.1*maxDsp]) # y-limits
    ax.set_xlabel('age'); ax.set_ylabel('displacement')
    ax.set_title('Raw data (95 %% limits)')
    Fig.tight_layout()

    # Save figure
    if outName:
        Fig.savefig('{}_Fig1_RawData.pdf'.format(outName),type='pdf')

    # Return values
    return Fig, ax


## Plot MC results
def plotMCresults(DspAgeData,AgePicks,DspPicks,maxPicks=500,outName=None):
    '''
        Plot valid MC picks in displacement-time space. Draw rectangles representing the 95 %
         confidence bounds using the plotRectangles function.
    '''

    # Parameters
    n = AgePicks.shape[1] # number of picks

    # Plot rectangles
    Fig, ax = plotRectangles(DspAgeData)

    # Plot picks
    if n <= maxPicks:
        ax.plot(AgePicks,DspPicks,color=(0,0,0),alpha=0.1,zorder=1)
        ax.plot(AgePicks,DspPicks,color=(0,0,1),marker='.',linewidth=0,alpha=0.5,zorder=2)
    else:
        ax.plot(AgePicks[:,:maxPicks],DspPicks[:,:maxPicks],
            color=(0,0,0),alpha=0.1,zorder=1)
        ax.plot(AgePicks[:,:maxPicks],DspPicks[:,:maxPicks],
            color=(0,0,1),marker='.',linewidth=0,alpha=0.4,zorder=2)

    # Format figure
    maxAge,maxDsp = findPlotLimits(DspAgeData) # plot limits
    ax.set_xlim([0,1.1*maxAge]); ax.set_ylim([0,1.1*maxDsp])
    ax.set_xlabel('age'); ax.set_ylabel('displacement')
    ax.set_title('MC Picks (N = {})'.format(n))
    Fig.tight_layout()

    # Save figure
    if outName:
        Fig.savefig('{}_Fig2_MCpicks.pdf'.format(outName),type='pdf')

    # Return values
    return Fig, ax


## Plot incremental slip rate results
def plotIncSlipRates(Rates,analysisMethod,plotMax=None,outName=None):
    '''
        Plot PDFs of incremental slip rates.
         Rates is a dictionary with slip rate objects, where each entry
          is the name of the interval.
         Analysis method is IQR or HPD.
    '''
    intervalNames = list(Rates.keys())
    m = len(intervalNames)

    # Setup figure
    Fig = plt.figure()
    ax = Fig.add_subplot(111)

    # Loop through each rate
    k=0
    for intvl in intervalNames:
        Rate = Rates[intvl]
        # Plot full PDF
        scaleVal=Rate.probs.max()
        ax.fill(Rate.rates, 0.9*Rate.probs/scaleVal+k,
            color=(0.4,0.4,0.4),zorder=2)
        # Plot confidence bounds
        if analysisMethod=='IQR':
            ax.fill(Rates[intvl].xIQR,
                0.9*Rates[intvl].pxIQR/scaleVal+k,
                color=(0.3,0.3,0.6),zorder=3)
        elif analysisMethod=='HPD':
            for j in range(Rate.Nclusters):
                xHPD=Rate.x_clusters[j]
                xHPD=np.pad(xHPD,(1,1),'edge')
                pxHPD=Rate.px_clusters[j]
                pxHPD=np.pad(pxHPD,(1,1),'constant')
                ax.fill(xHPD,0.9*pxHPD/scaleVal+k,
                    color=(0.3,0.3,0.6),zorder=3)
        k+=1

    # Format plot
    ylabels = ['{0}-\n{1}'.format(*intvl.split('-')) for intvl in intervalNames]
    ax.set_yticks(np.arange(0.5,m))
    ax.set_yticklabels(ylabels,rotation='vertical')
    ax.set_ylim([0,m])
    if plotMax: ax.set_xlim([0,plotMax])
    ax.set_xlabel('slip rate')
    ax.set_title('Incremental slip rates')
    Fig.tight_layout()

    # Save figure
    if outName:
        Fig.savefig('{}_Fig3_Incremental_slip_rates.pdf'.format(outName),type='pdf')

    return Fig, ax