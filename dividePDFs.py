#!/usr/bin/env python3
'''
** RISeR Incremental Slip Rate Calculator **
This function applies a form convolution to analytically find the
 quotient two PDFs.

Rob Zinke 2019-2021
'''

### IMPORT MODULES ---
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from resultSaving import confirmOutputDir


### PARSER ---
Description = '''Find the quotient of two PDFs.'''

Examples='''EXAMPLES
# Divide Marker1 displacement by Marker1 age
dividePDFs.py Marker1_dsp.txt Marker1_age -o Marker1_slipRate -v -p'''

def createParser():
    parser = argparse.ArgumentParser(description=Description,
        formatter_class=argparse.RawTextHelpFormatter, epilog=Examples)
    parser.add_argument(dest='numerPDFname', type=str,
        help='PDF to be used as the numerator')
    parser.add_argument(dest='denomPDFname', type=str,
        help='PDF to be used as the denominator')
    parser.add_argument('-o', '--output', dest='outName', type=str, required=True,
        help='Output file path/name')
    parser.add_argument('--step-size', dest='stepSize', type=float, default=None,
        help='Step size of quotient axis, in units of <numerator units>/<denominator units>. [Default sets this value to result in 1000 data points].')
    parser.add_argument('--max-quotient', dest='Qmax', type=float, default=None,
        help='Maximum quotient value to be computed.')
    parser.add_argument('-v','--verbose', dest='verbose', action='store_true',
        help='Print outputs to command line')
    parser.add_argument('-p', '--plot', dest='plot', action='store_true',
        help='Show plot of output')
    return parser

def cmdParser(inpt_args=None):
    parser = createParser()
    return parser.parse_args(args=inpt_args)



### PDF DIFFERENCE CLASS ---
class PDFquotient:
    def __init__(self, Xnumer, pXnumer, Xdenom, pXdenom, stepSize=None, Qmax=None, verbose=False):
        '''
        Analytically compute the quotient of two quantities described by two PDFs.
        '''
        # Record data
        self.verbose = verbose

        # Format data
        self.Xnumer, self.pXnumer = self.__formatPDF__(Xnumer, pXnumer)
        self.Xdenom, self.pXdenom = self.__formatPDF__(Xdenom, pXdenom)

        # Establish quotient axis
        self.__estbQuotientAxis__(Xnumer, Xdenom, stepSize, Qmax)

        # Compute quotient
        self.__dividePDFs__()

    def __formatPDF__(self, X, pX):
        '''
        Format an n x 2 array into separate parts and ensure unit mass.
        '''
        # Normalize area to 1.0
        pX = pX/np.trapz(pX,X)

        # Ensure no zero values
        w = (X > 0)
        X = X[w]
        pX = pX[w]

        # Toss out zero probability values
        w = (pX > 0)
        X = X[w]
        pX = pX[w]

        return X, pX

    def __estbQuotientAxis__(self, Xnumer, Xdenom, stepSize, Qmax):
        '''
        Format axis along which the quotient is to be computed.
        '''
        # Axis limits
        Qmin = self.Xnumer.min()/self.Xdenom.max()
        if Qmax is None:
            Qmax = self.Xnumer.max()/self.Xdenom.min()
        else:
            Qmax = np.min([self.Xnumer.max()/self.Xdenom.min(), Qmax])

        # Determine step size
        if stepSize is None:
            stepSize = (Qmax - Qmin)/1000

        # Establish quotient axis, Q
        self.Q = np.arange(Qmin, Qmax+stepSize, stepSize)

        # Report if requested
        if self.verbose == True:
            print('Quotient parameters:')
            print('\tquotient min {:f}'.format(Qmin))
            print('\tquotient max {:f}'.format(Qmax))
            print('\tquotient step {:f}'.format(stepSize))
            print('\tquotient len {:d}'.format(len(self.Q)))

    def __dividePDFs__(self):
        '''
        Compute quotient Q, as probability function pQ.
        '''
        # Establish interpolation function for numerator
        Inumer = interp1d(self.Xnumer, self.pXnumer, kind='linear', bounds_error=False, fill_value=0)

        # Compute convolution
        self.pQ = []
        for q in self.Q:
            # Equivalent numerator at each Q * denominator
            Pnumer = Inumer(q*self.Xdenom)
            pQ = np.sum(self.pXdenom * Pnumer * self.Xdenom)
            self.pQ.append(pQ)
        self.pQ = np.array(self.pQ)

        # Normalize area to unit mass
        self.pQ = self.pQ/np.trapz(self.pQ, self.Q)

    def plot(self, title=None):
        '''
        Plot raw data and difference PDF.
        '''
        # Establish figure
        self.fig = plt.figure()

        # Plot raw data
        self.axNumer = self.fig.add_subplot(311)
        self.axNumer.plot(self.Xnumer, self.pXnumer, color='b', linewidth=2, label='Numerator PDF')
        self.axNumer.legend()

        self.axDenom = self.fig.add_subplot(312)
        self.axDenom.plot(self.Xdenom, self.pXdenom, color='g', linewidth=2, label='Denominator PDF')
        self.axDenom.legend()

        # Plot quotient
        self.axQuot = self.fig.add_subplot(313)
        self.axQuot.plot(self.Q, self.pQ, color = 'k', linewidth=3, label='Quotient')
        self.axQuot.legend()

        # Format plot
        if title: self.fig.suptitle(title)

    def savePDF(self, outName):
        '''
        Save to file as n x 2 array.
        '''
        outName += '.txt'
        with open(outName, 'w') as outFile:
            outFile.write('# Value,\tProbability\n')
            for i in range(len(self.Q)):
                outFile.write('{0:f}\t{1:f}\n'.format(self.Q[i], self.pQ[i]))
            outFile.close()



### MAIN ---
if __name__ == '__main__':
    inps = cmdParser()  # gather inputs

    # Confirm output directory exists
    confirmOutputDir(inps.outName)

    # Load PDFs from file
    numerPDF = np.loadtxt(inps.numerPDFname)
    denomPDF = np.loadtxt(inps.denomPDFname)

    Xnumer = numerPDF[:,0]; pXnumer = numerPDF[:,1]
    Xdenom = denomPDF[:,0]; pXdenom = denomPDF[:,1]


    # Difference PDFs
    quot = PDFquotient(Xnumer, pXnumer, Xdenom, pXdenom, inps.stepSize, Qmax=inps.Qmax,
        verbose=inps.verbose)

    # Save to file
    if inps.outName:
        quot.savePDF(inps.outName)

    # Plot if requested
    if inps.plot == True:
        quot.plot()

    plt.show()