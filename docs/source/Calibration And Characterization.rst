Calibration And Characterization
================================

UUID: ``B8B41A65-2C29-4D60-A101-7072DA9F7646``

Calibration converts the raw CCD/ADC stream into a more useful spectrum.
Characterization measures how well that calibrated result matches known optical
inputs. The project uses CIE 233:2019 and ASTM E275 as technical references for
array spectroradiometer calibration and UV-Vis spectrometer performance
measurement.

Calibration Pipeline
--------------------

The host app's processing order is:

1. Convert raw ADC counts to floating-point values.
2. Remove stored master bias ``B_p`` when configured.
3. Estimate a frame-wise dark reference from shielded pixels 16 through 28 when
   dark subtraction is enabled.
4. Convert the inverted CCD readout into light-tracking counts.
5. Apply stored master-dark offsets if configured.
6. Apply flat-field or PRNU multiplicative correction when enabled.
7. Apply wavelength-dependent QE/response correction when enabled.
8. Build wavelengths from stored polynomial coefficients.
9. Normalize the display by absolute saturation reference or per-frame peak.

Characterization Tests
----------------------

The characterization plan should record:

* Wavelength-map fit residuals using laser diodes or known emission lines.
* FWHM of narrow lines at multiple wavelengths.
* SNR versus wavelength, especially near 850-1000 nm where detector response is
  expected to be lower.
* Linearity versus input level and integration time.
* Repeatability over repeated acquisitions without realignment.
* Stray-light and second-order diffraction behavior with and without filtering.
* Comparison against a reference source or commercial spectrometer.

Calibration and characterization are coupled. Wavelength error depends on
optical alignment, grating angle, CCD placement, and the pixel-to-wavelength
curve. Intensity error depends on the CCD response, mirror and grating
efficiency, filter transmission, analog acquisition chain, integration time,
and the software correction factors.



