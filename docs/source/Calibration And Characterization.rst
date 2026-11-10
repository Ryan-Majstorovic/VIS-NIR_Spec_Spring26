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

.. _uuid-c2aaf1f1-4b20-4d93-92c4-40b86483492c:

Verification Methods And Evidence
---------------------------------

UUID: :ref:`C2AAF1F1-4B20-4D93-92C4-40B86483492C <uuid-c2aaf1f1-4b20-4d93-92c4-40b86483492c>`

Calibration and characterization results remain planned until their method,
criterion, measurement conditions, uncertainty context, evidence artifacts,
and review disposition are recorded. The requirements-linked methods and
evidence-package rules are defined in
:doc:`Test and Verification <subsystems/test_and_verification/index>`.

**Reference:** CIE 233:2019,
`Calibration, Characterization and Use of Array Spectroradiometers
<https://doi.org/10.25039/TR.233.2019>`_,
Section 5.5.3, pp. 36-37: baseline characterization, pixel-wise dark
measurement, and verification of automatic baseline subtraction.




Production timing-profile compatibility
---------------------------------------

**Requirement:** The Host PC calibration system shall apply stored bias only
when its timing-profile identity matches the incoming frame and stored dark
offsets only when both timing profile and integration duration match to prevent
old-waveform calibrations from altering corrected-timing measurements.

**Rationale:** The previous ICG waveform produced a substantially different
light response at the same nominal exposure; duration alone cannot establish compatibility.

**Requirement:** The Host PC visualization system shall provide raw full-frame
ADC display and nominal shielded-reference statistics alongside processed display
to expose a collapsed or shifted reference even when subtraction produces near-zero output.

**Rationale:** Frame normalization can hide whether low processed signal arose
from genuinely low light or a displaced reference level.

**Requirement:** The Host PC recording system shall preserve raw counts and
per-frame timing-profile identity in HDF5 and shall preserve their association
through the frame CSV and timing ranges in the session ZIP for later calibration
compatibility review.

**Rationale:** Retained derived intensity alone cannot reconstruct a bypassed
or incompatible correction.

**Context:** Reference-shift screening in the desktop app is a heuristic, not
a calibrated overload limit. A sensor-specific acceptance threshold is ``Not In Docs``.
