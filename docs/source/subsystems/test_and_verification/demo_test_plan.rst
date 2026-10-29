Demonstration Test Plan
=======================

.. note::

   **Status: Proposed, under team review.** This plan reflects the project
   scope for the second half of Fall 2026 and may gain or lose tests after
   the team reviews it against the overall lab scope. Until that review is
   complete, every test below has the status ``Proposed`` and no result is
   claimed.

.. _uuid-92348097-c72d-4862-a675-5422f039ff9e:

Scope
-----

UUID: :ref:`92348097-C72D-4862-A675-5422F039FF9E <uuid-92348097-c72d-4862-a675-5422f039ff9e>`

**Summary:** The current project scope is a working demonstration of the
measurement chain built from the laser calibration unit, the fiber
connection, and the B&W Tek optical housing. Light from the calibration unit
enters the housing through the fiber, and the demonstration shows that the
TCD1304DG detector reads the incoming light and that the Host PC software
identifies its spectrum.

The demonstration chain is:

1. Laser calibration unit (405 nm, 520 nm, 650 nm, and 980 nm lasers).
2. Calibration-unit fiber output, joined by a Thorlabs ADASMA mating sleeve
   to a Thorlabs M14L01 low-OH patch cable.
3. B&W Tek compact Czerny-Turner housing with the TCD1304DG driver board at
   its detector port.
4. STM32F411 acquisition firmware streaming frames over USB CDC.
5. Host PC application: wavelength calibration, live display, and export.

An upgraded driver board with a higher-performance microcontroller and the
next steps for the optics are planned as design-only future work. They are
checked by design review (Section F), not by hardware tests.

This plan replaces the full-characterization scope of the
:doc:`Master Requirement-To-Test Matrix <testing>` for the demonstration.
The mapping to the earlier TV tests is given at the end of this page.

.. _uuid-a1f94639-3e18-4fcd-a9ab-7dfb20eb9929:

A. Calibration Source
---------------------

UUID: :ref:`A1F94639-3E18-4FCD-A9AB-7DFB20EB9929 <uuid-a1f94639-3e18-4fcd-a9ab-7dfb20eb9929>`

.. list-table::
   :header-rows: 1
   :widths: 10 30 40 20

   * - ID
     - Test
     - Method And Pass Evidence
     - Status
   * - CAL-1
     - Each laser switches on individually and couples into the fiber.
     - Switch on one laser at a time and observe light at the patch-cable
       end. Check the 980 nm laser with an IR viewer card or a camera.
     - Proposed
   * - CAL-2
     - Reference wavelength of each laser.
     - Measure each laser's center wavelength on a commercial spectrometer
       and record the measured values as the reference wavelengths in place
       of the labeled values. Instrument availability ``Not In Docs``.
     - Proposed
   * - CAL-3
     - Warm-up stability.
     - Record each laser's peak pixel over time after switch-on. Pass when
       the peak stops drifting. Warm-up time and drift limit ``Not In Docs``.
     - Proposed

**Rationale:** Every downstream wavelength result depends on the reference
lines. Low-cost laser diodes can differ from their labeled wavelength and
drift while warming up, so the reference values and a stable operating point
must be established before the detector results are interpreted.

.. _uuid-7e977c52-4672-4457-9c00-f96ae8352356:

B. Fiber Path
-------------

UUID: :ref:`7E977C52-4672-4457-9C00-F96AE8352356 <uuid-7e977c52-4672-4457-9c00-f96ae8352356>`

.. list-table::
   :header-rows: 1
   :widths: 10 30 40 20

   * - ID
     - Test
     - Method And Pass Evidence
     - Status
   * - FIB-1
     - Light passes through the mating sleeve and patch cable into the
       housing.
     - With the calibration unit connected through the ADASMA sleeve and
       M14L01 cable, confirm that peaks appear on the detector. Unplug and
       reconnect the fiber and confirm the peaks return.
     - Proposed

**Rationale:** The fiber connection is the only optical link between the
calibration unit and the housing, so a failed or non-repeatable connection
would block every optical test that follows.

.. _uuid-17aeb1a6-c1a5-4423-be7c-21589e099359:

C. Electronics And Data
-----------------------

UUID: :ref:`17AEB1A6-C1A5-4423-BE7C-21589E099359 <uuid-17aeb1a6-c1a5-4423-be7c-21589e099359>`

.. list-table::
   :header-rows: 1
   :widths: 10 30 40 20

   * - ID
     - Test
     - Method And Pass Evidence
     - Status
   * - EMB-1
     - CCD timing signals.
     - Measure fM, SH, and ICG with an oscilloscope. Pass when fM is 2 MHz,
       the ICG period is 8 ms, and SH matches the firmware configuration.
     - Proposed
   * - EMB-2
     - USB stream integrity.
     - Run the Spectrometer COM Inspector for 60 s. Pass with a steady
       frame rate and zero missed frame IDs. The documented minimum is 10
       complete frames per second.
     - Proposed
   * - EMB-3
     - Dark baseline.
     - Cover the input, capture frames, and apply bias and dark correction.
       Pass when the corrected baseline is near zero. Limit ``Not In Docs``.
     - Proposed
   * - EMB-4
     - No saturation.
     - With each laser on at the demonstration settings, confirm the peak
       stays below ADC full scale.
     - Proposed

**Rationale:** The demonstration depends on complete, correctly timed frames
and an unsaturated signal. A saturated or offset peak shifts its measured
position and width, which would corrupt the wavelength results in Section D.

.. _uuid-f38b3bd2-cd28-44ac-b457-676c1ad86474:

D. Light Detection In The Housing
---------------------------------

UUID: :ref:`F38B3BD2-CD28-44AC-B457-676C1AD86474 <uuid-f38b3bd2-cd28-44ac-b457-676c1ad86474>`

.. list-table::
   :header-rows: 1
   :widths: 10 30 40 20

   * - ID
     - Test
     - Method And Pass Evidence
     - Status
   * - OPT-1
     - Each laser produces one distinct peak.
     - Switch on each laser alone and record the pixel position of its peak.
     - Proposed
   * - OPT-2
     - Dispersion order.
     - Confirm the peak pixels move monotonically in one direction from
       405 nm to 520 nm to 650 nm to 980 nm.
     - Proposed
   * - OPT-3
     - Wavelength coverage.
     - Confirm that the 405 nm and 980 nm peaks both fall on the effective
       array. If either does not, record the covered range.
     - Proposed
   * - OPT-4
     - Wavelength calibration.
     - Fit a pixel-to-wavelength map to the four reference lines and report
       residuals. Leave-one-out check: fit three lines and predict the
       fourth. Fit form and error limit ``Not In Docs``.
     - Proposed
   * - OPT-5
     - Line width.
     - Measure the FWHM of each line in nm and compare it with the
       approximately 5 nm target.
     - Proposed
   * - OPT-6
     - Second-order observation.
     - Switch on only the 405 nm laser and look for a second-order peak near
       810 nm. Record its relative height. Filter mitigation is future work.
     - Proposed
   * - OPT-7
     - Repeatability.
     - Record peak positions over repeated captures and after reconnecting
       the fiber and power-cycling the electronics. Limit ``Not In Docs``.
     - Proposed
   * - OPT-8
     - All lines at once.
     - Switch on all four lasers and confirm four resolved peaks in one
       spectrum.
     - Proposed

**Rationale:** These tests show that the housing disperses light by
wavelength across the detector in a known order and range, that the pixel
axis can be converted to wavelength with measurable error, and that the
result is stable enough to identify a spectrum, which is the demonstration
goal.

.. _uuid-8607f505-397a-4508-a711-a4ad54e46edb:

E. Software And End-To-End Demonstration
----------------------------------------

UUID: :ref:`8607F505-397A-4508-A711-A4AD54E46EDB <uuid-8607f505-397a-4508-a711-a4ad54e46edb>`

.. list-table::
   :header-rows: 1
   :widths: 10 30 40 20

   * - ID
     - Test
     - Method And Pass Evidence
     - Status
   * - SW-1
     - Calibrated live display.
     - After calibration, confirm the GUI shows each peak at its reference
       wavelength on a wavelength axis.
     - Proposed
   * - SW-2
     - Blind identification.
     - A teammate switches on an unknown combination of lasers. The operator
       identifies which lasers are on from the displayed spectrum alone.
     - Proposed
   * - SW-3
     - Export.
     - Export a session to CSV and confirm it holds raw counts and
       wavelengths, and that re-plotting it reproduces the peaks.
     - Proposed
   * - SW-4
     - Demonstration workflow.
     - A team member who did not write the software follows the operation
       manual from setup to export without code or hardware changes.
     - Proposed

**Rationale:** The demonstration must show spectrum identification by a user,
not only correct internal data. Blind identification and an unassisted
workflow test the system the way the audience will see it.

.. _uuid-83440b99-224e-4cc3-a033-08a9328a5682:

F. Future Work Verified By Design Review
----------------------------------------

UUID: :ref:`83440B99-224E-4CC3-A033-08A9328A5682 <uuid-83440b99-224e-4cc3-a033-08a9328a5682>`

.. list-table::
   :header-rows: 1
   :widths: 10 30 40 20

   * - ID
     - Review
     - Method And Pass Evidence
     - Status
   * - DB-1
     - Upgraded driver board design review.
     - Review the schematic and layout against the CCD timing and ADC needs.
       Pass with clean ERC and DRC and a costed BOM. Microcontroller choice
       ``Not In Docs``.
     - Proposed
   * - DB-2
     - Upgraded analog front-end simulation (optional).
     - Simulate the analog front end and confirm signal levels and bandwidth
       suit the ADC.
     - Proposed
   * - OPT-F
     - Optical model check.
     - Compare the 3DOptix model's predicted peak positions with OPT-1 and
       OPT-3 results to decide whether the model can be trusted for future
       optics design.
     - Proposed

**Rationale:** The upgraded board and future optics will not be built this
semester. A design review and a model checked against measured data let the
team present them as credible next steps rather than unverified ideas.

.. _uuid-5d6b240f-389f-46de-a639-ef2fcf6944c8:

Relationship To The Earlier Test Matrix
---------------------------------------

UUID: :ref:`5D6B240F-389F-46DE-A639-EF2FCF6944C8 <uuid-5d6b240f-389f-46de-a639-ef2fcf6944c8>`

.. list-table::
   :header-rows: 1
   :widths: 25 25 50

   * - Earlier Test
     - Demonstration Test
     - Disposition
   * - TV-01 Coverage
     - OPT-3
     - Kept; measured with the 405 nm and 980 nm lines.
   * - TV-02 Detector geometry
     - EMB-2
     - Kept within the stream check.
   * - TV-03 FWHM
     - OPT-5
     - Kept.
   * - TV-04, TV-05 Frame transfer
     - EMB-2
     - Minimum rate kept; the above-100 fps target becomes future work.
   * - TV-06 Bias and dark
     - EMB-3
     - Kept.
   * - TV-07, TV-10 Wavelength map and accuracy
     - OPT-4, SW-1
     - Kept; reference values from CAL-2.
   * - TV-08 Response correction
     - None
     - Future work; needs a broadband source.
   * - TV-09 CSV products
     - SW-3
     - Kept.
   * - TV-11 SNR, TV-12 Linearity
     - None
     - Future work.
   * - TV-13 Repeatability
     - OPT-7
     - Kept.
   * - TV-14 Stray light and second order
     - OPT-6
     - Observation only; filter mitigation is future work.
   * - TV-15 Reference comparison
     - CAL-2
     - Optional; depends on access to a commercial spectrometer.
   * - TV-16 User workflow
     - SW-4
     - Kept.
