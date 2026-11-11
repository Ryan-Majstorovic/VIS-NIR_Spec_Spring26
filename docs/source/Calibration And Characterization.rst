Calibration And Characterization
================================

UUID: ``B8B41A65-2C29-4D60-A101-7072DA9F7646``

Calibration converts raw CCD counts into a spectrum on a wavelength axis.
Characterization measures how closely that spectrum matches a known
reference; its tests are in the :doc:`Test Plan
<subsystems/test_and_verification/test_plan>`. CIE 233:2019 and ASTM E275 are
the technical references for both.

Calibration Pipeline
--------------------

The Host PC applies calibration in this order:

1. Convert raw ADC counts to floating-point values.
2. Remove the stored master bias ``B_p`` when configured.
3. Estimate a frame-wise dark reference from shielded pixels 16 through 28
   when dark subtraction is enabled.
4. Invert the CCD readout into light-tracking counts.
5. Apply stored master-dark offsets when configured.
6. Apply flat-field or PRNU correction when enabled.
7. Apply wavelength-dependent response correction when enabled.
8. Build wavelengths from the stored polynomial coefficients.
9. Normalize the display to the saturation reference or the per-frame peak.

.. _uuid-c2aaf1f1-4b20-4d93-92c4-40b86483492c:

Calibration Sources
-------------------

UUID: :ref:`C2AAF1F1-4B20-4D93-92C4-40B86483492C <uuid-c2aaf1f1-4b20-4d93-92c4-40b86483492c>`

**Requirement:** The Host PC wavelength map shall be fitted to the 405 nm,
520 nm, and 650 nm calibration sources using center wavelengths measured on
the reference spectrometer, not the sources' labeled wavelengths.

**Rationale:** Low-cost sources can differ from their labels by several
nanometers, which exceeds the 2 nm accuracy target. A map fitted to labeled
values would build that error into every displayed wavelength.

The intensity corrections in steps 6 and 7 have no verified inputs yet. The
Phase 3 broadband comparison (test CMP-4) produces the first measured input
for the response correction.

**Reference:** CIE 233:2019,
`Calibration, Characterization and Use of Array Spectroradiometers
<https://doi.org/10.25039/TR.233.2019>`_, Section 5.5.3, pp. 36-37: baseline
characterization, pixel-wise dark measurement, and verification of automatic
baseline subtraction.
