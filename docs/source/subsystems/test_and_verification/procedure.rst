Comparison Procedure
====================

This page gives the run order for the :doc:`Test Plan <test_plan>`, the rules
that keep the prototype and reference measurements comparable, and what each
test record must contain. It follows the team's reference-spectrometer
comparison plan.

.. _uuid-c65ad49a-2c6b-45d1-8fe8-821b6fc1a21a:

Run Order
---------

UUID: :ref:`C65AD49A-2C6B-45D1-8FE8-821B6FC1A21A <uuid-c65ad49a-2c6b-45d1-8fe8-821b6fc1a21a>`

1. **Bring-up.** Run EMB-1 to EMB-3, SW-1, CAL-1, CAL-2, and FIB-1. Let each
   source warm up for the CAL-2 time before any capture.
2. **Phase 1: calibration and mapping.** Measure the 405 nm, 520 nm, and
   650 nm sources on the reference spectrometer (CAL-3). Move the fiber to the
   prototype, confirm no saturation (EMB-4), and capture each source alone
   (OPT-1, OPT-2). Fit and load the wavelength map (OPT-3), then measure the
   line widths (OPT-4).
3. **Phase 2: LED source comparison.** Measure the secondary LED on the
   reference and on the calibrated prototype and export both spectra to CSV
   (CMP-1 to CMP-3).
4. **Phase 3: broadband evaluation.** Measure the white LED on both
   instruments, export both spectra, and overlay the normalized curves
   (CMP-4).
5. **Tracking.** Capture the 405 nm source alone for second order (OPT-5) and
   repeat the calibration captures after reconnecting the fiber and
   power-cycling the electronics (OPT-6).
6. **Demonstration.** Run SW-2 and SW-3 with the stored calibration.

.. _uuid-1c9d38dd-1449-4243-8591-4cd8717a9a29:

Matched Conditions
------------------

UUID: :ref:`1C9D38DD-1449-4243-8591-4CD8717A9A29 <uuid-1c9d38dd-1449-4243-8591-4cd8717a9a29>`

**Requirement:** The Test and Verification system shall measure each
comparison source on the prototype and the reference spectrometer through the
same fiber, with the source unchanged and only the fiber's instrument end
moved between them, so that both instruments receive the same light.

**Rationale:** Moving or re-aiming the source between instruments changes how
much light, and which part of the source's emission, enters the fiber. That
change would appear as a wavelength, width, or intensity difference that the
prototype did not cause.

**Requirement:** The Test and Verification system shall capture prototype data
with the housing lid closed and the input dark-corrected, and with each peak
below ADC full scale.

**Rationale:** Ambient light adds a background the dark frame does not remove,
and a clipped peak has a shifted center and a widened FWHM.

Reference spectrometer identity, its integration settings, and how its
averaging is matched to the prototype's are ``Not In Docs``. The identity of
the secondary LED and white LED sources is ``Not In Docs``.

.. _uuid-b65ebb2f-81c9-4caa-ae21-a9ded740eaf6:

Test Records
------------

UUID: :ref:`B65EBB2F-81C9-4CAA-AE21-A9DED740EAF6 <uuid-b65ebb2f-81c9-4caa-ae21-a9ded740eaf6>`

**Requirement:** The Test and Verification system shall store, with every
test result, the test ID, date, operator, sources switched on, reference
wavelengths from CAL-3, prototype integration time, calibration-map version,
bench configuration, and the paths to the raw CSV files from both instruments.

**Rationale:** A result can only be rechecked or compared with a later run if
the light, settings, calibration, and raw data that produced it are known.
Any change to the slit, mirrors, grating, or detector position changes
coverage and resolution, so the bench configuration must travel with the
number.

Storage location, file naming, and retention period are ``Not In Docs``.

.. _uuid-bd53c5b6-b340-46b1-b46e-7458d173321b:

Result Disposition
------------------

UUID: :ref:`BD53C5B6-B340-46B1-B46E-7458D173321B <uuid-bd53c5b6-b340-46b1-b46e-7458d173321b>`

**Requirement:** The Test and Verification system shall assign each test
``Pass``, ``Fail``, or ``Inconclusive`` only from a complete test record, and
shall assign ``Inconclusive`` when the test's limit is ``Not In Docs`` or a
matched-condition rule was not met.

**Rationale:** Marking a test passed without a limit or under unmatched
conditions would report a result the data does not support.

**Requirement:** The Test and Verification system shall repeat CAL-3, OPT-1
to OPT-4, and CMP-1 after any change to the bench optics, detector position,
fiber, or wavelength map.

**Rationale:** Each of those changes moves where wavelengths land on the
detector, which invalidates the stored map and every result computed with it.
