#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import cumtrapz
from scipy.interpolate import interp1d

'''
Find inter-quantile range (IQR) or highest posterior density (HPD)
of a probability density function (PDF).
'''

## IQR method
# Find values of PDF using inter-quantile range method (more stable, but biased toward skewed tail)
def IQRpdf(x,px,confidence,outName=None,verbose=False,plot_input=False,plot_output=False):
	'''
	INPUTS
		x is an array of evenly spaced values -- even spacing is important!
		px is an array of probabilities at those values
		confidence is the confidence interval, in percent (e.g., 95, 68)
	OUTPUTS
	'''
	if verbose is True:
		print('Calculating interquantile range at {}% confidence limits'.format(confidence))

	# Determine bounds
	confidence/=100 # percent to fraction
	lower=0.5-confidence/2; upper=0.5+confidence/2

	# Integrate to CDF
	P=np.trapz(px,x) # check that area = 1.0
	px/=P # normalize
	Px=cumtrapz(px,x,initial=0)

	# Interpolate CDF to back-calculate values
	Icdf=interp1d(Px,x,kind='linear')
	lowerValue,upperValue=Icdf([lower,upper])

	# Outputs
	if verbose is True:
		print('\tLower value: {0:5f};\tUpper value: {1:5f}'.format(lowerValue,upperValue))

	if plot_input is True:
		Fcdf,axCDF=plotCDF(x,Px)
		axCDF.plot([lowerValue,lowerValue],[lower,0],color='b',zorder=1)
		axCDF.plot([upperValue,upperValue],[upper,0],color='b',zorder=1)

	if plot_output is True:
		plotNdx=(x>=lowerValue) & (x<=upperValue)
		xIQR=x[plotNdx]; xIQR=np.pad(xIQR,(1,1),'edge')
		pxIQR=px[plotNdx]; pxIQR=np.pad(pxIQR,(1,1),'constant')

		Fpdff,axPDFf=plotPDFfilled(x,px)
		axPDFf.fill(xIQR,pxIQR,color=(0.3,0.3,0.6),zorder=3)
		if outName:
			Fpdff.savefig(outName,dpi=300)

	return lowerValue, upperValue



## HPD method
# Find values of PDF using highest posterior density method (more representative of probable values)
def HPDpdf(x,px,confidence,outName=None,verbose=False,plot_input=False,plot_output=False):
	'''
	INPUTS
		x is an array of evenly spaced values -- even spacing is important!
		px is an array of probabilities at those values
		confidence is the confidence interval, in percent (e.g., 95, 68)
	OUTPUTS
	'''
	if verbose is True:
		print('Calculating highest posterior density at {}% confidence'.format(confidence))

	# Convert confidence bound from percent to fraction
	confidence/=100

	# Confirm area = 1.0
	P=np.trapz(px,x) # total area
	px/=P # normalize

	# Check conditioning - points must be spaced approximately evenly
	xsteps=np.diff(x) # spacing between sample points
	avestep=np.mean(xsteps) # average spacing between sample points
	step_tolerance=1.01 # factor of average step above which assumptions are invalid 
	if np.sum(xsteps>step_tolerance*avestep)>0:
		print('WARNING: Sample spacing must be approximately equal for HPD calculation')

	# Sort from highest-lowest probability
	sortNdx=np.argsort(px) # indices lowest-highest
	sortNdx=sortNdx[::-1] # flip highest-lowest
	
	# Sum probabilities until they reach the specified confidence limit
	xSort=x[sortNdx]; pxSort=px[sortNdx] # place arrays in order
	PxSort=np.cumsum(pxSort) # cumulative probability
	PxSort/=PxSort.max() # normalize sum to 1.0

	# Find values that sum to confidence limit
	sortNdxRelevant=sortNdx[PxSort<=confidence] # relevant index values
	xRelevant=x[sortNdxRelevant] # x values
	pxRelevant=px[sortNdxRelevant] # px values

	# Sort by x value
	sortBack=np.argsort(xRelevant)
	xRelevant=xRelevant[sortBack]
	pxRelevant=pxRelevant[sortBack]

	# Min and Max values
	lowestValue=xRelevant.min()
	highestValue=xRelevant.max()

	# Identify "clusters"
	nRelevant=len(xRelevant) # number of relevant data points
	x_clusters=[]; px_clusters=[] # empty lists
	breakpt=0
	for i in range(1,nRelevant):
		if (xRelevant[i]-xRelevant[i-1])>step_tolerance*avestep:
			x_clusters.append(xRelevant[breakpt:i])
			px_clusters.append(pxRelevant[breakpt:i])
			breakpt=i
	x_clusters.append(xRelevant[breakpt:]) # add final values
	px_clusters.append(pxRelevant[breakpt:]) # add final values

	# Outputs
	if verbose is True:
		nClusters=len(x_clusters)
		print('\tLowest value: {0:5f};\tHighest value: {1:5f}'.format(lowestValue,highestValue))
		print('\tNumber of clusters: {}'.format(nClusters))

	if plot_input is True:
		Fcdf,axCDF=plotCDF(np.arange(len(PxSort)),PxSort)
		axCDF.plot([len(xRelevant),len(xRelevant)],[confidence,0],'b')
		axCDF.set_xticks([])

	if plot_output is True:
		Fpdff,axPDFf=plotPDFfilled(x,px)
		# axPDFf.plot(xRelevant,pxRelevant,'-b.')
		# Plot clusters
		nClusters=len(x_clusters)
		for i in range(nClusters):
			xHPD=x_clusters[i]
			xHPD=np.pad(xHPD,(1,1),'edge')
			pxHPD=px_clusters[i]
			pxHPD=np.pad(pxHPD,(1,1),'constant')
			axPDFf.fill(xHPD,pxHPD,color=(0.3,0.3,0.6),zorder=3)
		if outName:
			Fpdff.savefig(outName,dpi=300)

	return lowestValue, highestValue, x_clusters, px_clusters



#########################
### Support Functions ###
#########################
def plotPDF(x,px,title=None):
	Fpdf=plt.figure()
	axPDF=Fpdf.add_subplot(111)
	axPDF.plot(x,px,color='k',linewidth=2)
	axPDF.set_xlabel('value'); axPDF.set_ylabel('rel prob')
	axPDF.set_title('PDF',title)
	return Fpdf,axPDF

def plotPDFfilled(x,px,title=None):
	xFill=np.pad(x,(1,1),'edge')
	pxFill=np.pad(px,(1,1),'constant')
	Fpdff=plt.figure()
	axPDFf=Fpdff.add_subplot(111)
	axPDFf.fill(xFill,pxFill,color=(0.4,0.4,0.4),zorder=2)
	axPDFf.set_xlabel('value'); axPDFf.set_ylabel('ref prob')
	axPDFf.set_title('PDF',title)
	return Fpdff,axPDFf

def plotCDF(x,Px,title=None):
	Fcdf=plt.figure()
	axCDF=Fcdf.add_subplot(111)
	axCDF.plot(x,Px,color='k',linewidth=2)
	axCDF.set_xlabel('value'); axCDF.set_ylabel('integ\'d prob')
	axCDF.set_title('CDF',title)
	return Fcdf,axCDF