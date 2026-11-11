Test Plan
=========

This is the final test plan for the Fall 2026 prototype. It verifies the
measurement chain from the calibration sources through the fiber, the B&W Tek
bench, the TCD1304DG, the STM32 firmware, and the Host PC application, and it
judges the calibrated prototype against a commercial reference spectrometer.
The run order, setup rules, and record contents are in
:doc:`Comparison Procedure <procedure>`, and every derived number is computed
as defined in :doc:`Calculations <calculations>`. Every test below is
``Planned``; no result is claimed until a reviewed test record exists.

.. _uuid-92348097-c72d-4862-a675-5422f039ff9e:

Scope
-----

UUID: :ref:`92348097-C72D-4862-A675-5422F039FF9E <uuid-92348097-c72d-4862-a675-5422f039ff9e>`

**Summary:** Testing is organized around the team's reference-spectrometer
comparison plan. Bring-up checks confirm that the electronics, fiber, and
sources work. Phase 1 uses the commercial reference spectrometer to establish
the true center wavelengths of the 405 nm, 520 nm, and 650 nm calibration
sources and calibrates the prototype's pixel-to-wavelength map against them.
Phase 2 measures a separate LED source on both instruments to check the
calibrated prototype on light it was not calibrated with. Phase 3 overlays a
broadband source on both instruments to locate response differences across the
band. The demonstration and design-review checks close the plan.

The operating band is the client-approved range of approximately 400 nm to
800 nm observed with the B&W Tek bench. The upgraded driver board is design
work only and is checked by review, not by hardware tests.

**Requirement:** The Test and Verification system shall judge the prototype's
wavelength accuracy and spectral resolution against the documented limits of
2 nm peak-wavelength error and 5 nm FWHM, using a commercial reference
spectrometer's measurement of the same sources under the same conditions as
the reference value.

**Rationale:** Low-cost calibration sources can differ from their labeled
wavelengths by several nanometers, which is larger than the 2 nm limit. Only a
reference instrument measuring the same light can separate prototype error from
source error.

.. _uuid-a1f94639-3e18-4fcd-a9ab-7dfb20eb9929:

A. Bring-Up Checks
------------------

UUID: :ref:`A1F94639-3E18-4FCD-A9AB-7DFB20EB9929 <uuid-a1f94639-3e18-4fcd-a9ab-7dfb20eb9929>`

.. list-table::
   :header-rows: 1
   :widths: 10 22 52 16

   * - ID
     - Test
     - Method And Pass Criterion
     - Status
   * - EMB-1
     - CCD timing
     - Measure fM, SH, and ICG with an oscilloscope. Pass when fM is
       2 MHz ±0.1%, the ICG period is 8 ms with a 7.388 ms pulse width, and
       SH has a 10 µs set time with its pulse aligned to the ICG off time.
     - Planned
   * - EMB-2
     - USB stream integrity
     - Stream for 60 s with the Spectrometer COM Inspector. Pass with zero
       missed frame IDs and at least 10 complete frames per second
       (:ref:`C1 <uuid-c9755e34-9135-4415-b7c0-c39e287a70d8>`).
     - Planned
   * - EMB-3
     - Dark baseline
     - Cover the input with the lid closed, capture frames, and apply bias
       and dark correction. Pass when the corrected RMS noise floor is at
       least 50% lower than the uncorrected floor
       (:ref:`C4 <uuid-22971c51-a176-427e-9509-c552d1b1c6c3>`).
     - Planned
   * - SW-1
     - CSV export
     - Export a capture. Pass when the file holds raw ADC counts and
       wavelengths in matching rows and re-plotting it reproduces the
       displayed spectrum.
     - Planned
   * - CAL-1
     - Source coupling
     - Switch on each calibration source alone and confirm light at the
       patch-cable end (use an IR viewer card for the 980 nm laser).
     - Planned
   * - CAL-2
     - Source warm-up
     - Track each source's peak pixel after switch-on. Pass when the peak
       stops moving. Warm-up time and drift limit ``Not In Docs``.
     - Planned
   * - FIB-1
     - Fiber path
     - With the source connected through the ADASMA sleeve and M14L01
       cable, confirm a peak appears on the detector.
     - Planned

**Requirement:** The Test and Verification system shall complete the bring-up
checks before any Phase 1 capture to confirm that frames are complete, the
dark baseline is corrected, exported data is usable, and light reaches the
detector through the fiber.

**Rationale:** Every comparison result is computed from exported frames.
Missing frames, an uncorrected baseline, or an unstable source would appear as
wavelength or width error and be blamed on the optics.

.. _uuid-f38b3bd2-cd28-44ac-b457-676c1ad86474:

B. Phase 1: Calibration And Mapping
-----------------------------------

UUID: :ref:`F38B3BD2-CD28-44AC-B457-676C1AD86474 <uuid-f38b3bd2-cd28-44ac-b457-676c1ad86474>`

.. list-table::
   :header-rows: 1
   :widths: 10 22 52 16

   * - ID
     - Test
     - Method And Pass Criterion
     - Status
   * - CAL-3
     - Reference wavelengths
     - Measure the 405 nm, 520 nm, and 650 nm sources on the reference
       spectrometer and record each center wavelength. These measured values
       replace the labeled values everywhere in this plan.
     - Planned
   * - EMB-4
     - No saturation
     - At the capture settings, confirm each peak stays below ADC full scale
       on the prototype and below saturation on the reference.
     - Planned
   * - OPT-1
     - Distinct, ordered peaks
     - Switch on each source alone. Pass when each produces one peak and the
       peak pixels move in one direction from 405 nm to 520 nm to 650 nm.
     - Planned
   * - OPT-2
     - Wavelength coverage
     - Confirm the 405 nm and 650 nm peaks lie on the effective array and
       record the shortest and longest wavelengths the array covers. The
       980 nm laser is outside the client-approved band; record only whether
       it reaches the array.
     - Planned
   * - OPT-3
     - Wavelength map
     - Fit the pixel-to-wavelength map to the three CAL-3 values and load it
       in the Host PC application. Pass when each calibration peak is
       displayed within 2 nm of its CAL-3 value
       (:ref:`C2 <uuid-22f91c7c-d310-486a-ac24-bdc8be1b11ac>`). Fit form
       ``Not In Docs``.
     - Planned
   * - OPT-4
     - Spectral resolution
     - Measure the FWHM of each calibration line on the prototype
       (:ref:`C3 <uuid-60b5dbf0-f84f-4fef-8768-ca31ad5d905b>`). Pass when
       every line is 5 nm or less.
     - Planned

**Requirement:** The Test and Verification system shall calibrate the
prototype's wavelength map only with reference wavelengths measured by the
reference spectrometer, and shall judge spectral resolution only with the
narrow calibration lines.

**Rationale:** A map fitted to labeled wavelengths inherits each source's
labeling error. Resolution must be judged on lines narrower than the 5 nm
limit; a broader source would report its own width, not the prototype's.

.. _uuid-8607f505-397a-4508-a711-a4ad54e46edb:

C. Phase 2: LED Source Comparison
---------------------------------

UUID: :ref:`8607F505-397A-4508-A711-A4AD54E46EDB <uuid-8607f505-397a-4508-a711-a4ad54e46edb>`

.. list-table::
   :header-rows: 1
   :widths: 10 22 52 16

   * - ID
     - Test
     - Method And Pass Criterion
     - Status
   * - CMP-1
     - Peak wavelength
     - Measure the secondary LED on both instruments under identical
       conditions and export both spectra to CSV. Pass when the prototype's
       peak wavelength is within 2 nm of the reference's
       (:ref:`C2 <uuid-22f91c7c-d310-486a-ac24-bdc8be1b11ac>`).
     - Planned
   * - CMP-2
     - Peak width
     - From the same CSVs, compute the LED's FWHM on each instrument and
       report the difference. Limit ``Not In Docs``.
     - Planned
   * - CMP-3
     - Relative intensity
     - Normalize each LED spectrum to its own peak and compare them across
       the LED band (:ref:`C5 <uuid-97ad92d8-6986-4fa5-9f89-9189331006ba>`).
       Report the largest deviation. Limit ``Not In Docs``.
     - Planned

**Requirement:** The Test and Verification system shall verify the calibrated
wavelength map with a source that was not used to build it.

**Rationale:** A map always fits its own calibration points closely, so
residuals at those points cannot show how well it predicts other wavelengths.
The secondary LED is an independent check. The LED's own width is several
times the 5 nm limit, so CMP-2 compares the instruments with each other
rather than testing resolution; resolution is judged in OPT-4.

.. _uuid-d646150d-6e9f-4e52-bae8-e03d60cec04a:

D. Phase 3: Broadband Spectrum Evaluation
-----------------------------------------

UUID: :ref:`D646150D-6E9F-4E52-BAE8-E03D60CEC04A <uuid-d646150d-6e9f-4e52-bae8-e03d60cec04a>`

.. list-table::
   :header-rows: 1
   :widths: 10 22 52 16

   * - ID
     - Test
     - Method And Pass Criterion
     - Status
   * - CMP-4
     - Broadband shape
     - Measure a white LED on both instruments under identical conditions,
       normalize both spectra, and overlay them
       (:ref:`C5 <uuid-97ad92d8-6986-4fa5-9f89-9189331006ba>`). Record the
       prototype-to-reference ratio across the covered band. Observation; no
       pass limit.
     - Planned

**Requirement:** The Test and Verification system shall record the ratio of
the prototype's normalized broadband spectrum to the reference's across the
covered band to define the input for a future spectral response correction.

**Rationale:** Grating efficiency, mirror coatings, and detector response all
vary with wavelength, so the prototype's broadband curve differs from the
reference's even when the wavelength map is correct. The measured ratio shows
where and by how much, which is what a response correction needs.

.. _uuid-f0ad14ec-8c9a-49bc-9ea0-45765f98e05e:

E. Tracking Checks
------------------

UUID: :ref:`F0AD14EC-8C9A-49BC-9EA0-45765F98E05E <uuid-f0ad14ec-8c9a-49bc-9ea0-45765f98e05e>`

.. list-table::
   :header-rows: 1
   :widths: 10 22 52 16

   * - ID
     - Test
     - Method And Pass Criterion
     - Status
   * - OPT-5
     - Second-order light
     - Switch on only the 405 nm source and look for a second-order peak near
       810 nm. Record its height relative to the first-order peak, or record
       that 810 nm falls outside the covered band.
     - Planned
   * - OPT-6
     - Connection repeatability
     - Record the calibration peak positions over repeated captures, after
       unplugging and reconnecting the fiber, and after power-cycling the
       electronics (:ref:`C6 <uuid-ed22b205-1bb5-4ea3-9ac2-05890bb529b1>`).
       Limit ``Not In Docs``.
     - Planned

**Requirement:** The Test and Verification system shall record second-order
height and peak-position repeatability alongside every Phase 1 and Phase 2
result set.

**Rationale:** A second-order peak can be mistaken for real long-wavelength
signal, and a connection that shifts peaks between captures would make a
single passing comparison unrepeatable.

.. _uuid-db0f211b-a3f8-4e81-9730-184a20337855:

F. Demonstration
----------------

UUID: :ref:`DB0F211B-A3F8-4E81-9730-184A20337855 <uuid-db0f211b-a3f8-4e81-9730-184a20337855>`

.. list-table::
   :header-rows: 1
   :widths: 10 22 52 16

   * - ID
     - Test
     - Method And Pass Criterion
     - Status
   * - SW-2
     - Blind identification
     - A teammate switches on an unknown combination of calibration sources.
       Pass when the operator names the sources that are on from the
       displayed spectrum alone.
     - Planned
   * - SW-3
     - Operator workflow
     - A team member who did not write the software connects the device,
       starts acquisition, adjusts integration time, applies the stored
       calibration, and exports a CSV by following the operation manual.
       Pass with no code or hardware changes.
     - Planned

**Requirement:** The Test and Verification system shall verify the
demonstration with an operator who identifies sources from the displayed
spectrum and completes the routine workflow without code or hardware changes.

**Rationale:** The client will use the instrument through the application,
not through exported data, so the demonstration must show that a user can
reach a correct identification on their own.

.. _uuid-83440b99-224e-4cc3-a033-08a9328a5682:

G. Design Review
----------------

UUID: :ref:`83440B99-224E-4CC3-A033-08A9328A5682 <uuid-83440b99-224e-4cc3-a033-08a9328a5682>`

.. list-table::
   :header-rows: 1
   :widths: 10 22 52 16

   * - ID
     - Review
     - Method And Pass Criterion
     - Status
   * - DB-1
     - Upgraded driver board
     - Review the schematic and layout against the CCD timing and ADC needs.
       Pass with clean ERC and DRC and a costed BOM. Microcontroller choice
       ``Not In Docs``.
     - Planned
   * - DB-2
     - Analog front-end simulation (optional)
     - Simulate the analog front end and confirm its signal levels and
       bandwidth suit the ADC.
     - Planned

**Requirement:** The Test and Verification system shall verify the upgraded
driver board by design review only.

**Rationale:** The board will not be built this semester, so a reviewed design
and simulation are the evidence that it is a credible next step.

.. _uuid-5d6b240f-389f-46de-a639-ef2fcf6944c8:

Deferred Characterization
-------------------------

UUID: :ref:`5D6B240F-389F-46DE-A639-EF2FCF6944C8 <uuid-5d6b240f-389f-46de-a639-ef2fcf6944c8>`

**Summary:** The following measurements belong to full instrument
characterization and are outside this semester's plan:

* Spectral response correction applied and verified. CMP-4 supplies its input.
* Signal-to-noise ratio and linearity versus input level and integration time.
* Order-sorting filter and stray-light suppression. OPT-5 sizes the problem.
* Frame-rate testing against the above-100 fps design target. EMB-2 checks
  only the 10 frames per second minimum.
* Uncertainty budgets for the comparison results.
