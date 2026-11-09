Optics Verification
===================

UUID: ``C24197B9-33DD-43EB-BC3E-CF6D7C461C93``

This page shows how the design criteria in the :doc:`Optics System Overview
<../overview>` are tested. The tests come from the :doc:`Demonstration Test
Plan <../../test_and_verification/demo_test_plan>`, which remains the
authoritative source for each test's method and pass evidence. Like that plan,
every test here is ``Proposed`` and no result is claimed.

.. _uuid-4931ef01-7cdb-4090-a97b-eabb8f17647d:

Optics Tests
------------

UUID: :ref:`4931EF01-7CDB-4090-A97B-EABB8F17647D <uuid-4931ef01-7cdb-4090-a97b-eabb8f17647d>`

**Summary:** The demonstration uses the laser calibration unit (405 nm,
520 nm, 650 nm, and 980 nm) as the light source, delivered to the bench
through the fiber. The tests below are the ones that verify the optics, in
the order they should be run. Calibration-source tests come first because
every optical result is measured against the laser reference wavelengths.

.. list-table::
   :header-rows: 1
   :widths: 10 22 40 15 13

   * - ID
     - Test
     - What It Shows About The Optics
     - Criterion
     - Status
   * - CAL-2
     - Reference wavelength of each laser
     - Supplies measured reference wavelengths for every optical result.
       Low-cost lasers can differ from their labeled wavelength.
     - Prerequisite
     - Proposed
   * - CAL-3
     - Warm-up stability
     - Separates laser drift from optical drift, so a moving peak is not
       mistaken for a bench problem.
     - Prerequisite
     - Proposed
   * - FIB-1
     - Light passes through the sleeve and patch cable into the housing
     - The fiber delivers light to the slit, and the connection is
       repeatable after unplugging.
     - OPT-R4
     - Proposed
   * - OPT-1
     - Each laser produces one distinct peak
     - The bench forms a single, focused slit image for each wavelength.
     - OPT-R5
     - Proposed
   * - OPT-2
     - Dispersion order
     - The grating spreads wavelengths in one direction across the array.
     - OPT-R1, OPT-R5
     - Proposed
   * - OPT-3
     - Wavelength coverage
     - The 405 nm and 980 nm lines both land on the effective array, which
       bounds the covered band.
     - OPT-R1
     - Proposed
   * - OPT-4
     - Wavelength calibration
     - Pixel position can be mapped to wavelength with a measurable error,
       checked by a leave-one-out fit.
     - OPT-R5
     - Proposed
   * - OPT-5
     - Line width
     - Measured FWHM at each laser line against the approximately 5 nm
       target; differences between lines show focus error across the band.
     - OPT-R2, OPT-R3
     - Proposed
   * - OPT-6
     - Second-order observation
     - Size of the second-order 405 nm peak near 810 nm, which sets the
       future filter requirement.
     - OPT-R6
     - Proposed
   * - OPT-7
     - Repeatability
     - Peaks return to the same pixels after repeated captures, fiber
       reconnection, and power cycling.
     - OPT-R5
     - Proposed
   * - OPT-8
     - All lines at once
     - Four lines are resolved together in one spectrum without blending.
     - OPT-R2, OPT-R5
     - Proposed
   * - EMB-3
     - Dark baseline
     - With the input covered and the lid closed, no ambient light reaches
       the detector.
     - OPT-R7
     - Proposed
   * - OPT-F
     - Optical model check (design review)
     - Compares the 3DOptix model's predicted peak positions with OPT-1 and
       OPT-3 to decide whether the model can be trusted for future optics
       design.
     - Future design
     - Proposed

EMB-4 (no saturation) must pass before OPT-4 and OPT-5 are trusted, because
a clipped peak has a shifted center and a widened FWHM.

.. _uuid-8d8313d8-a65b-4c40-b0a4-5f88b8e8e662:

Wavelength Coverage And Resolution
----------------------------------

UUID: :ref:`8D8313D8-A65B-4C40-B0A4-5F88B8E8E662 <uuid-8d8313d8-a65b-4c40-b0a4-5f88b8e8e662>`

**Summary:** Coverage is verified with the 405 nm and 980 nm lines, which sit
near the two ends of the 400 nm to 1000 nm target band. The 520 nm and 650 nm
lines provide the intermediate points for the wavelength map. A map fitted only
to lines near the center of the detector is not considered complete, because
it cannot show whether the ends of the band are placed correctly.

Resolution is tracked as the FWHM of each laser line. FWHM is measured after
alignment and wavelength calibration, and at every line rather than one, to
catch grating-angle, focus, and slit effects that only appear away from the
center of the array. The wavelength-map fit form and the allowed fit error are
``Not In Docs``.

.. _uuid-f66d66dc-23e9-42ec-a635-1d8be9832c16:

Test Record Contents
--------------------

UUID: :ref:`F66D66DC-23E9-42EC-A635-1D8BE9832C16 <uuid-f66d66dc-23e9-42ec-a635-1d8be9832c16>`

**Requirement:** The Optics system shall record the slit, grating, mirror,
filter, and detector-port configuration of the test bench with every
characterization record to identify the optical geometry that produced each
result.

**Rationale:** A change to any bench element alters wavelength coverage,
resolution, and throughput. Without the recorded configuration, we cannot
separate a change in measured performance caused by the optics from one caused
by acquisition or host-side processing.

Each optics test record should also include the lasers switched on, their
reference wavelengths from CAL-2, integration time, calibration version, and
the path to the raw exported data.

.. _uuid-677cd5cb-7b3b-4ed6-b646-85dd50c6309f:

Deferred Characterization
-------------------------

UUID: :ref:`677CD5CB-7B3B-4ED6-B646-85DD50C6309F <uuid-677cd5cb-7b3b-4ed6-b646-85dd50c6309f>`

**Summary:** The earlier full-characterization scope in the
:doc:`Master Requirement-To-Test Matrix <../../test_and_verification/testing>`
included optics measurements that the demonstration does not cover. They
remain part of the long-term design and are deferred, not dropped.

.. list-table::
   :header-rows: 1
   :widths: 35 20 45

   * - Measurement
     - Earlier Test
     - Why Deferred
   * - Spectral response correction
     - TV-08
     - Needs a broadband source with a known spectrum.
   * - SNR at visible and near-infrared wavelengths
     - TV-11
     - Not needed to identify laser lines in the demonstration.
   * - Linearity versus intensity and integration time
     - TV-12
     - Not needed to identify laser lines in the demonstration.
   * - Stray light and filtered second-order suppression
     - TV-14
     - Only the unfiltered second-order peak is observed now (OPT-6); the
       order-sorting filter is future work.
   * - Comparison with a commercial spectrometer
     - TV-15
     - Optional; depends on access to an instrument. Partly covered by
       CAL-2.
