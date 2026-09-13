Optics System Overview
======================

.. note::

   Insert the user-provided Optics architecture diagram here after the Visio
   source and image are available.

.. _uuid-48fc9581-eaff-4e34-9b0c-0d1bf006e71f:

System Role
-----------

UUID: :ref:`48FC9581-EAFF-4E34-9B0C-0D1BF006E71F <uuid-48fc9581-eaff-4e34-9b0c-0d1bf006e71f>`

**Summary:** The Optics system shall accept input light and coordinate
collimation, wavelength dispersion, focusing, filtering, alignment, enclosure,
and performance characterization to image a VIS-NIR spectrum onto the
TCD1304DG effective detector array.

**Expected Outcome:** The Optics system shall provide usable wavelength
coverage from 400 nm to 1000 nm and approximately 5 nm FWHM for narrow sources.

**Rationale:** Coordinating the optical path, filtering, and mechanical
alignment preserves the wavelength-dependent image needed for detector capture
and allows measured optical performance to be attributed to a repeatable
configuration.

.. _uuid-3a113e98-e52c-4b54-8624-4939610e4ed2:

System Objectives
-----------------

UUID: :ref:`3A113E98-E52C-4B54-8624-4939610E4ED2 <uuid-3a113e98-e52c-4b54-8624-4939610e4ed2>`

**Objective 1:** **Optical transformation.** The Optics system shall accept
incident light, collimate it, disperse it by wavelength, and focus the spectrum
across the detector.

**Rationale:** Preserving this sequence establishes the detector-position
relationship required for wavelength measurement.

**Objective 2:** **Component and filtering decisions.** The Optics system shall
record how the grating, slit, mirrors, and filters affect wavelength coverage,
resolution, throughput, second-order overlap, stray light, and alignment.

**Rationale:** Recording each tradeoff prevents a component choice from changing
instrument performance without reviewable evidence.

**Objective 3:** **Physical verification.** The Optics system shall provide
alignment, enclosure, and characterization evidence for wavelength coverage,
FWHM, wavelength accuracy, SNR, linearity, repeatability, stray light, and
reference comparison.

**Rationale:** Physical evidence is needed to distinguish predicted optical
performance from measured instrument performance.

.. _uuid-e19ea297-0d3d-4bb1-b420-629bde897454:

System Relationship
-------------------

UUID: :ref:`E19EA297-0D3D-4BB1-B420-629BDE897454 <uuid-e19ea297-0d3d-4bb1-b420-629bde897454>`

.. list-table::
   :header-rows: 1

   * - System
     - Primary Responsibility
     - Downstream Or Adjacent Relationship
   * - Optical Path
     - The Optics optical-path system shall define the slit, collimation, dispersion, focusing, and detector-imaging sequence.
     - The Optics optical-path system shall establish wavelength-dependent illumination on the TCD1304DG effective array.
   * - Tradeoffs
     - The Optics tradeoff system shall record component and geometry choices with their optical consequences.
     - The Optics tradeoff system shall relate each choice to alignment, throughput, coverage, and resolution.
   * - Filtering
     - The Optics filtering system shall limit second-order overlap and other unwanted wavelength content before detector capture.
     - The Optics filtering system shall control the optical content presented to the detector and downstream Host PC processing.
   * - Alignment And Enclosure
     - The Optics alignment-and-enclosure system shall establish repeatable placement, light exclusion, and mechanical stability.
     - The Optics alignment-and-enclosure system shall preserve the optical configuration used for characterization and measurement.
   * - Performance Characterization
     - The Optics performance-characterization system shall define coverage, FWHM, accuracy, SNR, linearity, repeatability, stray-light, and comparison checks.
     - The Optics performance-characterization system shall provide optical evidence to Test and Verification and Host PC calibration workflows.

.. _uuid-14a977b2-a1cd-404e-9500-1eacbf249040:

Integration Boundary
--------------------

UUID: :ref:`14A977B2-A1CD-404E-9500-1EACBF249040 <uuid-14a977b2-a1cd-404e-9500-1eacbf249040>`

**Summary:** The Optics system shall provide wavelength-dependent illumination
at the detector boundary. The Embedded system shall control detector timing and
digitization after that optical handoff. The Host PC system shall perform
pixel-to-wavelength association, correction, visualization, retention, and
export. The Test and Verification system shall provide canonical pass/fail
disposition.

Component placement tolerances, final slit width, grating angle, focus
tolerance, filter cutoff profile, enclosure limits, and most quantitative
characterization acceptance thresholds remain ``Not In Docs`` until approved
requirements and methods are available.

**Expected Outcome:** The Optics system shall remain independently reviewable
without duplicating Embedded acquisition, Host PC processing, or Integration
transport behavior.

**Rationale:** Separating optical formation, detector acquisition, host-side
processing, and pass/fail disposition prevents multiple subsystems from
defining or evaluating the same boundary behavior differently.

Related Pages
-------------

* :doc:`Optical Path <optical_path/Optical Path>`
* :doc:`Tradeoffs <tradeoffs/Tradeoffs>`
* :doc:`Filtering <filtering/Filtering>`
* :doc:`Alignment And Enclosure <alignment_enclosure/Alignment And Enclosure>`
* :doc:`Performance Characterization <performance_characterization/Performance Characterization>`
