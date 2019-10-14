from astropy.io import fits
from astropy.stats import LombScargle
import matplotlib.pyplot as plt

# PDC (1) or SAP (2)
lc_type = 1
# Choose campaign number
campaign_num = 5
# Specifies path directory.
use_remote = True

def get_hdul(use_remote):
	path_to_dir=""
	if (use_remote):
		path_to_dir = "/storage/astro2/phujzc/k2sc_data/campaign_{}".format(campaign_num)
	else:
		path_to_dir = "~/dev/machine_learning/px402/k2sc_data/campaign_{}".format(campaign_num)
	return fits.open('{}/hlsp_k2sc_k2_llc_211923232-c05_kepler_v2_lc.fits'.format(path_to_dir))

# Open hdul object
hdul = get_hdul(use_remote)

### The seven columns of data per lightcurve:
# - quality  : Original K2 photometry pipeline quality flags
# - cadence  : observation cadences
# - time     : observation times
# - flux     : K2SC-detrended flux 
# - trend_p  : k2sc-estimated position-dependent trend
# - trend_t  : k2sc-estimated time-dependent trend
# - mflags   : k2sc outlier flags
# The PDC-MAP and SAP extensions are identical, the only difference being
# the flux for which the detrending was applied to.

# The trend_t and trend_p columns contain the time- and
# position-depedent trends, respectively. Their baseline levels are the
# same as those of the original (input) and detrended fluxes. To compute
# the full K2SC model including both time- and position-dependent
# trends, one must first subtract the median from one of them:

# trend_tot = trend_t + trend_p - median(trend_p)

# The detrended flux was obtained by subtracting the full K2SC model,
# including both systematics and stellar variability, from the input flux,
# but ensuring the median is unchanged:
 
# flux = input_flux - trend_tot + np.median(trend_tot).

# This detrended flux could in principle be used to perform a transit
# search. However, please be warned that the stellar variability model
# used by K2SC is intended to help model and remove the systematics as
# well as possible, it is not optimized for subsequent transit searches.
#
# Instead, we encourage users to compute the systematics-only corrected
# flux, which preserves the astrophysical variability, by adding the
# time-dependent trend back on (after correcting the median):
#
# flux_c = flux + trend_t - median(trend_t)

# This preserves stellar variability, and is useful for a wide range of
# astrophysical studies. A separate variability filtering step can then
# be used to detrend the data with a view to performing a transit
# search.
#
# The mflags columns is used to flag outliers and data points which
# should be treated with caution or were excluded from the fit for any
# reason. It is a 16-bit integer, with each bit having a specific
# meaning:
#
# - 2**0 : one of the K2 quality flags on
# - 2**1 : flare (reserved but not currently used)
# - 2**2 : transit (reserved but not currently used)
# - 2**3 : upwards outlier
# - 2**4 : downwards outlier
# - 2**5 : nonfinite flux
# - 2**6 : a periodic mask applied manually by k2sc (not used in this version)
#
# The primary header is a direct copy of the original MAST primary
# header. The following header keywords are stored by K2SC in each
# extension:
#
# - SPLITS: time(s) of reversal of the direction of roll angle
#   variations (corresponds to break-points in the systematics model)
# - CDPP1R: our estimate of the 6.5h Combined Differential Photometric
#   Precision (CDPP) in the raw data. CDPP estimates are computed
#   following Gilliland et al. (2011).
# - CDPP1T: our estimate of the 6.5h Combined Differential Photometric
#   Precision (CDPP) in the systematics-corrected data
# - CDPP1C: our estimate of the 6.5h Combined Differential Photometric
#   Precision (CDPP) in the systematics-corrected and detrended data
# - KER_NAME: name of GP covariance function used for variability
#   component
# - KER_PARS: names of parameters of GP convariance function
# - KER_EQN: equation of covariance function
# - KER_HPS1: best-fit value of the parameters of GP covariance function.

flux = hdul[lc_type].data['flux']
times = hdul[lc_type].data['time']

def plot_lightcurve(times, flux, title, filename):
	plt.scatter(times, flux, s=0.1)
	plt.xlabel("Flux")
	plt.ylabel("Time")
	plt.title("{}_lc".format(title))
	plt.savefig("{}_lc.png".format(filename))
	plt.close()

def plot_pow_spectrum(frequency, power, title, filename):
	plt.plot(frequency, power, linewidth=5)
	plt.xlabel("Frequency")
	plt.ylabel("Power")
	plt.title("{}_ps".format(title))
	plt.savefig("{}_ps.png".format(filename))
	plt.close()

plot_lightcurve(times, flux, "title", "filename1")

# Lomb Scargle Work

print(times)
print(flux)

frequency, power =  LombScargle(times, flux, 0.1).autopower()
plot_pow_spectrum(frequency, power, "Title", "filename2")
print(frequency)
print(power)

