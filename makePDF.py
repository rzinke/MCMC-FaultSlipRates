#!/usr/bin/env python3
'''
** RISeR Incremental Slip Rate Calculator **
Use this to create a probability density function (PDF) as a text file.

Rob Zinke 2019-2021
'''

### IMPORT MODULES ---
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate as intrp
from slipRateObjects import gauss
from resultSaving import confirmOutputDir


### PARSER ---
Description = '''Create a probability density function (PDF) given reference points and a specified,
parametric distribution. Ages are in (kilo)years B.P.'''

Examples='''EXAMPLES

# Create a uniform (a.k.a. "boxcar") distribution between 3.0 and 5.5
makePDF.py -d boxcar -v 3.0 5.0 -o PDFx1

# Create a Gaussian distribution with mean 5.0 and standard deviation 0.3
makePDF.py -d gauss -v 5.0 0.3 -o PDFx2

# Create a triangular distribution with minimum 3.8, preferred 5.0, maximum 5.6, composed of 1000 data points
makePDF.py -d tri -v 3.8 5.0 5.6 -o PDFx3 -n 1000

# Create a trapezoidal distribution with a boxcar shape bewteen 5 and 6, and plot the results
makePDF.py -d trap -v 4.0 5.0 6.0 7.5 -o PDFx4 -p

'''

def createParser():
    parser = argparse.ArgumentParser(description=Description,
        formatter_class=argparse.RawTextHelpFormatter, epilog=Examples)
    parser.add_argument('-d', '--distribution', dest='dstrb', type=str, required=True,
        help='Distribution type [\'gauss\'/\'triangle\'/\'trapezoid\']]')
    parser.add_argument('-v', '--values', dest='values', type=float, nargs='+', required=True,
        help='Values to specify distribution, separated by spaces.\nTwo values for gaussian ([mean] +/- [1 std dev])\nThree values for triangle ([min], [pref], [max])\nFour values for trapezoid.')
    parser.add_argument('-o', '--output', dest='outName', type=str, required=True,
        help='Output file path/name')
    parser.add_argument('-n', '--nDataPts', dest='nDataPts', type=int, default=100,
        help='Number of data points. Default = 100')
    parser.add_argument('--verbose', dest='verbose', action='store_true',
        help='Print outputs to command line')
    parser.add_argument('-p', '--plot', dest='plot', action='store_true',
        help='Show plot of output')
    return parser

def cmdParser(inpt_args=None):
    parser = createParser()
    return parser.parse_args(args=inpt_args)



### ANCILLARY FUNCTIONS ---
def checkInputs(dstrb, values):
    '''
    Check that the specified distribution is valid, and that the proper number
     of inputs are given to describe that distribution.
    '''
    # Format distribution
    dstrb = dstrb.lower()

    # Treatment based on distribution
    if dstrb in ['gaussian', 'gauss']:
        dstrb = 'gaussian'

        # Assert correct number of values
        assert len(values) == 2, 'Gaussian distribution requires the mean and standard deviation, e.g., 5.0 0.3.'

    elif dstrb in ['uniform', 'boxcar']:
        dstrb = 'uniform'
        values.sort()  # sort smallest to largest

        # Assert correct number of values
        assert len(values) == 2, 'Uniform distribution requires the minimum and maximum values, e.g., 3.0 5.0'

        # Assert nonzero distance between values
        assert (values[1]-values[0]) > 0, 'Must provide nonzero distance between specified values. (Use an arbitrarily small difference to approximate zero-width).'

    elif dstrb in ['tri', 'triangle', 'triangular']:
        dstrb = 'triangular'
        values.sort()  # sort smallest to largest

        # Assert correct number of values
        assert len(values) == 3, 'Triangular distribution requires the minimum, preferred, and maximum values, e.g., 4.4 5.0 5.6'

        # Assert nonzero distance between values
        assert np.sum(np.diff(values)) > 0, 'Must provide nonzero distance between at least two of the specified values. (Use an arbitrarily small difference to approximate zero-distance).'

    elif dstrb in ['trap', 'trapezoid', 'trapezoidal']:
        dstrb = 'trapezoidal'
        values.sort()  # sort smallest to largest

        # Assert correct number of values
        assert len(values) == 4, 'Trapezoidal distribution requires the minimum, boxcar bounds, and maximum values, e.g., 4.4 4.6 5.4 5.6'

    else:
        print('{:s} not a valid distribution. Choose from [Gaussian, triangular, trapezoidal]'.format(dstrb))
        exit()

    return dstrb, values


def buildDistribution(dstrb, values, nDataPts, verbose = False):
    '''
    Build a probability density function based on the specified distribution and values.
    '''
    # Continue by distribution type
    if dstrb == 'gaussian':
        # Gaussian
        mu = values[0]  # mean
        sd = values[1]  # std deviation
        x = np.linspace(mu-4*sd, mu+4*sd, nDataPts)
        px = gauss(x, mu, sd)

    elif dstrb == 'uniform':
        # Uniform
        x = np.linspace(values[0], values[1], nDataPts)
        px = np.ones(nDataPts)

    elif dstrb == 'triangular':
        # Triangular
        x = np.linspace(values[0], values[2], nDataPts)
        Ix = intrp.interp1d(values, [0,1,0], kind='linear')
        px = Ix(x)  # interpolate

    elif dstrb == 'trapezoidal':
        # Trapezoidal
        x = np.linspace(values[0], values[3], nDataPts)
        Ix = intrp.interp1d(values, [0,1,1,0], kind='linear')
        px = Ix(x)  # interpolate

    # Normalize to area = 1.0
    P = np.trapz(px, x)  # integrated area
    px /= P  # normalize
    P = np.trapz(px, x)  # normalized area (should be 1.0)

    if verbose == True:
        print('{:s} distribution with {:d} points'.format(dstrb, nDataPts))
        print('Final probability mass {:f}'.format(P))

    return x, px


def saveOutputs(x, px, outName, verbose = False):
    '''
    Save outputs to text file.
    '''
    fname = outName+'.txt'
    with open(fname, 'w') as outFile:
        outFile.write('# Value,\tProbability\n')
        for i in range(len(x)):
            outFile.write('{0:f}\t{1:f}\n'.format(x[i], px[i]))
        outFile.close()

    if verbose == True:
        print('Saved data to {:s}'.format(fname))


def plotPDF(x, px, outName, verbose = False):
    '''
        Plot PDF and save file for visual check.
    '''
    # Plot
    Fig = plt.figure()
    ax = Fig.add_subplot(111)
    ax.plot(x, px, color = 'b', linewidth = 2)
    ax.set_title('Probability Density Function -- {:s}'.format(os.path.basename(outName)))
    ax.set_xlabel('values'); ax.set_ylabel('rel prob')

    # Save to figure
    figName = outName+'.png'
    Fig.savefig(figName)
    if verbose == True:
        print('Saved figure to {}'.format(figName))

    plt.show()



### CREATE PDF ---
def makePDF(dstrb, values, outName, nDataPts=100, verbose=False, plot=False):
    '''
        Create a PDF based on the given parameters.
    '''
    # Check inputs are valid
    dstrb, values = checkInputs(dstrb, values)

    # Build distribution
    x, px = buildDistribution(dstrb, values, nDataPts)

    # Save to text file
    saveOutputs(x, px, outName, verbose)

    # Plot and save if specified
    if plot == True:
        plotPDF(x, px, outName, verbose)


### MAIN ---
if __name__ == '__main__':
    # Gather inputs
    inps = cmdParser()

    # Confirm output directory exists
    confirmOutputDir(inps.outName)

    # Create PDF
    makePDF(dstrb=inps.dstrb, values=inps.values, outName=inps.outName,
        nDataPts=inps.nDataPts,
        verbose=inps.verbose, plot=inps.plot)  # create PDF
