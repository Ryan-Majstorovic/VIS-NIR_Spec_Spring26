Requirements And Metrics
========================

UUID: ``5E8ED5F1-69FA-4A37-89FE-71060AB22F0A``

These are the instrument-level targets for the current project stage and the
tests that check them. Limits come from the team design document (Sections
2.1, 3.3, and 5) and the team's reference-spectrometer comparison plan. Test
IDs refer to the :doc:`Test Plan <subsystems/test_and_verification/test_plan>`.

.. list-table::
   :header-rows: 1
   :widths: 20 45 15 20

   * - Area
     - Target
     - Tests
     - Status
   * - Wavelength range
     - Approximately 400 nm to 800 nm, client-approved. The original 400 nm
       to 1000 nm target is future work.
     - OPT-2
     - Planned
   * - Wavelength accuracy
     - Peak wavelength within 2 nm of the reference spectrometer.
     - OPT-3, CMP-1
     - Planned
   * - Spectral resolution
     - FWHM of 5 nm or less for narrow calibration lines.
     - OPT-4
     - Planned
   * - Signal level
     - No peak at ADC full scale during measurement.
     - EMB-4
     - Planned
   * - Detector geometry
     - 3648 effective TCD1304DG pixels per frame.
     - EMB-2
     - Planned
   * - CCD timing
     - fM 2 MHz ±0.1%; ICG period 8 ms with a 7.388 ms pulse; SH 10 µs,
       aligned to the ICG off time.
     - EMB-1
     - Planned
   * - Frame transfer
     - At least 10 complete frames per second with no missed frame IDs. The
       above-100 fps design target is future work.
     - EMB-2
     - Planned
   * - Dark correction
     - Corrected RMS noise floor at least 50% below uncorrected.
     - EMB-3
     - Planned
   * - Repeatability
     - Calibration peaks return to the same position after reconnection and
       power cycling. Limit ``Not In Docs``.
     - OPT-6
     - Planned
   * - Export
     - CSV rows hold raw ADC counts, processed counts, wavelengths, volts,
       and processed intensity.
     - SW-1
     - Planned
   * - Usability
     - Routine measurement without code or hardware changes.
     - SW-3
     - Planned

**Requirement:** The spectrometer shall be reported as meeting a target only
when the listed test has a ``Pass`` disposition from a complete test record.

**Rationale:** Early bench observations are useful for debugging but were not
taken under the matched conditions of the comparison procedure, so they cannot
stand in for an acceptance result.
