# MCMC-FaultSlipRates
This code calculates incremental fault slip rates the assumption that the fault did not slip backwards (i.e., inversely to its overall kinematic history) at any point. Inputs are given as probability density functions (PDFs) describing displacement measurements and the ages of those markers at different epochs in a common fault history. This methodology therefore provides a Bayesian approach to incremental slip rate estimation for which prior data regarding a series of events are modified by explicit assumptions. This type of estimation is especially important in situations for which uncertainties in age or displacement are large, or measurements overlap within uncertainty.

Conditions are enforced using Markov Chain Monte Carlo (MCMC) sampling. Inputs are sampled via the probability inverse transform method. If any of the samples drawn produces a negative slip rate, that set of samples is thrown out. Sampling continues until the desired number of samples is reached. Slip rates are reported first as percentiles of the allowable picks, and then based on analysis of a continous nonparametric function determined from the picks. 

This code is based on an earlier Python2 version developed in Zinke et al., 2017 (GRL) and Zinke et al., 2019 (GRL), and builds on methods described in Gold and Cowgill, 2011 (EPSL). These codes use Python 3.x, and were tested on versions 3.6, 3.7.
If you use these scripts, please cite:
* Zinke, R., Dolan, J.F., Rhodes, E.J., Van Dissen, R., McGuire, C.P. (2017) Highly Variable Latest Pleistocene-Holocene Incremental Slip Rates on the Awatere Fault at Saxton River, South Island, New Zealand, Revealed by Lidar Mapping and Luminescence Dating, Geophyical Research Letters, 44, https://doi.org/10.1002/2017GL075048
* Zinke, R., Dolan, J.F., Rhodes, E.J., Van Dissen, R., McGuire, C.P., Hatem, A.E., Brown, N.D., Langridge, R.M. (2019) Multimillennial Incremental Slip Rate Variability of the Clarence Fault at the Tophouse Road Site, Marlborough Fault System, New Zealand, Geophysical Research Letters, 46, https://doi.org/10.1029/2018GL080688


CONTENTS:
Executable functions:
* calcSlipRates.py - This is the main function for calculating incremental slip rates based on previously developed inputs. Users should run this function as a command, e.g., calcSlipRates.py -a List-of-ages.txt -d List-of-displacements.txt. This function requires two lists of filenames, as described in the INPUTS section below. This function calculates the incremental slip rates by sampling the input data (priors) and rejecting samples based on the condition that no slip rates should be negative at any point in their history. There are many optional parameters for the calcSlipRates function. Use calcSlipRates.py -h for help.

* makePDF.py - Use this to create a probability density function (PDF) as a text file. A distribution is specified, as well as the "parameters" or specific points in that distribution: For a gaussian distribution, two numbers are required 'mean stddev'; for a triangular distribution, three numbers are required 'min preferred max'; for a trapezoidal function, four numbers are required 'min shoulder1 shoulder2 max'. Supported types currently are Gaussian, tringular, and trapezoidal shapes. Gaussian distributions are printed out to 4-sigma. Uniform (boxcar) sampling distributions are specified using the trapezoidal function, with steeply sloping sides (e.g., closely approximates a boxcar). Users should run this function as a command, e.g., makePDF.py -d 'triangular' -v '3 5 6' -o Offset1.txt.


Support scripts:
* MCresampling.py - Used for sampling the input data and calculating the slip rates by enforcing the no-negative-rates condition. Other conditions can be specified and applied, though this is not recommended. Additionally, a maximum physically reasonable slip rate to be considered can be specified based on the user's judgement to avoid statistically implausible calculations.
* array2pdf.py - Converts an unordered array of sample picks into a continuous PDF. Two options are available. Kernel density estimation (KDE) gives a weight to data points using an automatic bandwidth determination scheme-- this tends to overweight slow slip rates and overweight fast slip rates due to inherently uneven sampling. A most reliable, alternative method is to bin the samples in a histogram using the 'hist' option. If sampling is uneven, this may lead to artificially spiky, poorly conditioned results. To overcome this limitation, smoothing methods are available. All these parameters can be specified in the calcSlipRates call.
* PDFanalysis - The range of possible slip rates can be quite large; it is often useful to report a range representing the most probable slip rates based on the data. To do this, two functions are provided within PDFanalysis: IQR reports the requested inter-quantile range of the PDF. This is more stable than HPD, but can be skewed, especially toward larger values. HPD reports the highest posterior density (most probable values) of a PDF. This method can give more meaningful results than IQR, but can result in anomalous values in spiky, non-smooth functions. For HPD, multiple value ranges are reported, depending on the continuity of probable values in the PDF.


INPUTS:
The calcSlipRates function requires two text files: (1) A list of age filenames, written out from youngest at the top, to oldest at the bottom; and (2) a list of displacement names, similarly written out from yougest (least offset) at the top, to oldest (most offset) at the bottom. Note that these lists do not contain any data; they simply list the files in which the data are contained. 

Each "data file" consists of a two-column list describing a single measurement of displacement or age. In each, the first column is the value measured (i.e., age or displacement), and the second column is the relative probability of that value. If a measurement can be described as parametric function, a properly formatted PDF can be generated using makePDF.py, described above. Any arbitrary, pseudo-continuous PDF can be used as an input.  


Two examples are provided. The data files are named, e.g., T1T2age.txt, T3T4dsp.txt, etc.


NOTE!
This is research code. The author(s) assumes no responsibility for any errors in the methods or scripts, or any damages resulting from the code's use.
Do not use this code without citing Zinke et al., 2017; 2019. Please contact Robert Zinke with any questions or comments.