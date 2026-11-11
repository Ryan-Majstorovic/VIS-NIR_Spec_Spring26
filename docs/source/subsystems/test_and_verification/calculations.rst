Calculations
============

Each number reported by the :doc:`Test Plan <test_plan>` is computed as
defined on this page, from exported CSV data.

.. _uuid-c9755e34-9135-4415-b7c0-c39e287a70d8:

C1 - Complete-Frame Rate
------------------------

UUID: :ref:`C9755E34-9135-4415-B7C0-C39E287A70D8 <uuid-c9755e34-9135-4415-b7c0-c39e287a70d8>`

``R_frame = N_complete / delta_t``, where ``N_complete`` is the number of
complete frames received in the elapsed time ``delta_t``.

**Requirement:** The Test and Verification system shall count only complete
frames containing 3648 effective detector samples when computing
``R_frame``, and shall report it separately from the display update rate.

**Rationale:** Counting partial frames or display redraws would overstate the
rate at which usable spectra reach the Host PC. Used by EMB-2 (pass at
``R_frame >= 10`` frames/s).

.. _uuid-22f91c7c-d310-486a-ac24-bdc8be1b11ac:

C2 - Wavelength Error
---------------------

UUID: :ref:`22F91C7C-D310-486A-AC24-BDC8BE1B11AC <uuid-22f91c7c-d310-486a-ac24-bdc8be1b11ac>`

``e_lambda = lambda_prototype - lambda_reference``, where
``lambda_prototype`` is the peak wavelength reported by the calibrated
prototype and ``lambda_reference`` is the peak wavelength reported by the
reference spectrometer for the same source.

**Requirement:** The Test and Verification system shall report ``e_lambda``
with its sign for each source and shall pass a source when
``|e_lambda| <= 2 nm``.

**Rationale:** The sign shows whether the map is shifted or stretched in one
direction, which tells the team how to correct it. Used by OPT-3 and CMP-1.
The peak-location method (maximum sample or interpolated center) is
``Not In Docs``.

.. _uuid-60b5dbf0-f84f-4fef-8768-ca31ad5d905b:

C3 - Full Width At Half Maximum
-------------------------------

UUID: :ref:`60B5DBF0-F84F-4FEF-8768-CA31AD5D905B <uuid-60b5dbf0-f84f-4fef-8768-ca31ad5d905b>`

``FWHM = lambda_right - lambda_left``, where ``lambda_left`` and
``lambda_right`` are the wavelengths at which the dark-corrected peak crosses
half of its maximum.

**Requirement:** The Test and Verification system shall interpolate linearly
between samples to locate each half-maximum crossing.

**Rationale:** Near 5 nm a line spans only tens of pixels, so rounding each
crossing to the nearest pixel would add an error comparable to the limit
being tested. Used by OPT-4 (pass at ``FWHM <= 5 nm``) and CMP-2.

.. _uuid-22971c51-a176-427e-9509-c552d1b1c6c3:

C4 - Dark Baseline Improvement
------------------------------

UUID: :ref:`22971C51-A176-427E-9509-C552D1B1C6C3 <uuid-22971c51-a176-427e-9509-c552d1b1c6c3>`

``improvement = 1 - RMS_corrected / RMS_raw``, where each RMS is taken over
the effective pixels of a covered-input frame.

**Requirement:** The Test and Verification system shall compute
``RMS_raw`` and ``RMS_corrected`` from the same covered-input frames and
shall pass EMB-3 when ``improvement >= 0.5``.

**Rationale:** Using the same frames isolates the effect of the correction
from frame-to-frame noise.

.. _uuid-97ad92d8-6986-4fa5-9f89-9189331006ba:

C5 - Normalized Spectrum Comparison
-----------------------------------

UUID: :ref:`97AD92D8-6986-4FA5-9F89-9189331006BA <uuid-97ad92d8-6986-4fa5-9f89-9189331006ba>`

``ratio(lambda) = P(lambda) / R(lambda)``, where ``P`` and ``R`` are the
prototype and reference spectra, each dark-corrected and divided by its own
maximum. The largest deviation is ``max |P(lambda) - R(lambda)|``.

**Requirement:** The Test and Verification system shall interpolate the
prototype spectrum onto the reference spectrometer's wavelength points before
computing ``ratio`` or the deviation, and shall report both only where the
reference value is above a minimum signal level. That level is
``Not In Docs``.

**Rationale:** The two instruments sample different wavelengths, so they must
share one wavelength grid before they are compared. Where the reference
signal is near zero, the ratio is dominated by noise and does not describe
the prototype. Used by CMP-3 and CMP-4.

.. _uuid-ed22b205-1bb5-4ea3-9ac2-05890bb529b1:

C6 - Peak Repeatability
-----------------------

UUID: :ref:`ED22B205-1BB5-4EA3-9AC2-05890BB529B1 <uuid-ed22b205-1bb5-4ea3-9ac2-05890bb529b1>`

``s = sqrt(sum((x_i - x_bar)^2) / (n - 1))``, where ``x_i`` are the peak
positions of one source over ``n`` captures and ``x_bar`` is their mean.

**Requirement:** The Test and Verification system shall report ``s`` and the
largest single shift for each calibration source, in pixels and in nm.

**Rationale:** The standard deviation describes ordinary capture-to-capture
scatter, while the largest shift catches a single bad reconnection that an
average would hide. Used by OPT-6. The pass limit is ``Not In Docs``.
