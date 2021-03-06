'''
** MCMC Incremental Slip Rate Calculator **
Covert an array of numbers into a probability density function (PDF).

Rob Zinke 2019-2021
'''

### IMPORT MODULES ---
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from slipRateObjects import gauss_kernel



### CONVERSION FUNCTIONS ---
## Histogram method
def arrayHist(V, stepsize, smoothingKernel=None, kernelWidth=2, verbose=False, plot=False):
    '''
    Convert to PDF using histogram (more stable over fast intervals)
    INPUTS:
        V is an array of values
        stepsize is the sample spacing of the output function
        smoothingKernel (optional) is the type of kernel with which the raw
         output function will be convolved to reduce undersampling artifacts
        kernelWidth is the width of the smoothing kernel
    OUTPUTS:
        x is the values
        px is the probability of occurrence
    '''

    # Report basic stats if requested
    if verbose == True:
        print('Converting array to histogram')

        # Compute raw statistics
        pct=np.percentile(V, [50-95.45/2, 50-68.27/2, 50,50+68.27/2, 50+95.45/2])
        print('Raw statistics:')
        print('\tmedian: {0:.3f}'.format(pct[2]))
        print('\t68.27% range: {0:.3f}-{1:.3f}'.format(pct[1], pct[3]))
        print('\t95.45% range: {0:.3f}-{1:.3f}'.format(pct[0], pct[4]))
        print('\tmin: {0:.3f}; max: {1:.3f}'.format(V.min(), V.max()))

    # Histogram bin edges/independent axis
    bins = np.arange(V.min(), V.max()+stepsize, stepsize)

    # Compute histogram
    H,Hedges = np.histogram(V, bins=bins)
    Hcntrs = (Hedges[:-1]+Hedges[1:])/2  # centers of bins

    # Taper histogram edges
    Hcntrs = np.pad(Hcntrs, (1,1), 'constant', constant_values=(Hedges[0], Hedges[-1]))
    H = np.pad(H, (1,1), 'constant')

    # Smooth if requested
    if smoothingKernel:
        if verbose == True:
            print('Applying smoothing kernel:\n\ttype: {}\twidth: {}'.format(smoothingKernel, kernelWidth))

        # Moving mean smoothing
        if smoothingKernel.lower() in ['mean']:
            K=np.ones(kernelWidth)  # boxcar kernel

        # Gaussian window smoothing
        elif smoothingKernel.lower() in ['gauss', 'gaussian']:
            K=gauss_kernel(kernelWidth)  # Gaussian kernel

        # Apply smoothing
        H=np.convolve(H,K,'same')  # apply via convolution
        H[0] = 0; H[-1] = 0  # set ends back to zero

    # Normalize area to 1.0
    Area = np.trapz(H, Hcntrs)  # find area
    H = H/Area  # normalize area

    # Format outputs
    x = Hcntrs
    px = H

    # Plot if requested
    if plot == True:
        fig, ax = plt.subplots()
        ax.plot(x, px, 'k', linewidth=1)

    return x, px


## KDE method
# Convert to PDF using kernel density estimation (inherently smoother)
def arrayKDE(V, stepsize, smoothingKernel=None, kernelWidth=2, verbose=False, plot=False):
    '''
    INPUTS:
        V is an array of values
        stepsize is the sample spacing of the output function
        smoothingKernel (optional) is the type of kernel with which the raw
         output function will be convolved to reduce undersampling artifacts
        kernelWidth is the width of the smoothing kernel
    OUTPUTS:
        x is the values
        px is the probability of occurrence
    '''

    # Report basic stats if requested
    if verbose == True:
        print('Converting array to histogram')

        # Compute raw statistics
        pct = np.percentile(V, [50-95.45/2, 50-68.27/2, 50, 50+68.27/2, 50+95.45/2])
        print('Raw statistics:')
        print('\tmedian: {0:.3f}'.format(pct[2]))
        print('\t68.27% range: {0:.3f}-{1:.3f}'.format(pct[1], pct[3]))
        print('\t95.45% range: {0:.3f}-{1:.3f}'.format(pct[0], pct[4]))
        print('\tmin: {0:.3f}; max: {1:.3f}'.format(V.min(), V.max()))

    # Independent axis
    x = np.arange(V.min(), V.max()+stepsize, stepsize)

    # Compute KDE
    Fkde = gaussian_kde(V) # compute kde function
    Kde = Fkde(x) # evaluate at axis values

    # Set to zero at edges
    Kde[0] = 0; Kde[-1] = 0

    # Smooth if requested
    if smoothingKernel:
        if verbose == True:
            print('Applying smoothing kernel:\n\ttype: {}\twidth: {}'.format(smoothingKernel, kernelWidth))

        # Moving mean smoothing
        if smoothingKernel.lower() in ['mean']:
            K=np.ones(kernelWidth)  # boxcar kernel

        # Gaussian window smoothing
        elif smoothingKernel.lower() in ['gauss','gaussian']:
            K=gauss_kernel(kernelWidth)  # Gaussian kernal

        # Apply smoothing
        Kde=np.convolve(Kde, K, 'same')  # apply via convolution
        Kde[0] = 0; Kde[-1]= 0  # set ends back to zero

    # Normalize area to 1.0
    Area = np.trapz(Kde, x)  # find area
    Kde = Kde/Area  # normalize area

    # Format outputs
    x = x
    px = Kde

    # Plot if requested
    if plot == True:
        fig, ax = plt.subplots()
        ax.plot(x, px, 'k', linewidth=1)

    return x, px