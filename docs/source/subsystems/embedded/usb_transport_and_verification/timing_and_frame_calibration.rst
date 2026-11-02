Timing and Frame Calibration
==============================

The Timing and Frame Calibration subsystem establishes the laboratory procedures, measurement tolerances, and verification evidence required to qualify the embedded controller waveforms and physical pixel geometry before high-level optical calibrations are conducted on the Host PC.

.. _uuid-aeb786de-6370-47b3-92bf-b7cb39f1d2c2:

Subsystem Role & Boundary
-------------------------

UUID: :ref:`AEB786DE-6370-47B3-92BF-B7CB39F1D2C2 <uuid-aeb786de-6370-47b3-92bf-b7cb39f1d2c2>`

This subsystem operates at the hardware verification interface. It does not perform software-level photometric flat-fielding, dark baseline subtraction, or wavelength polynomial mapping—those functions reside in the Host PC Primary Data Pipeline. Instead, it qualifies the physical signals produced by the STM32F411 and confirms that acquired raw data frames accurately map to the physical geometry of the Toshiba TCD1304DG sensor.

Inputs and Outputs
------------------

.. list-table::
   :header-rows: 1

   * - Flow
     - Name
     - Type / Units
     - Description
   * - **Input**
     - Oscilloscope Timing Probes
     - Physical test points
     - Probing points on driver board for fM (PA8), SH (PB0), and ICG (PB6).
   * - **Input**
     - Dark Frame Ingestion Stream
     - Raw binary frames
     - Captured frame data with the optical detector entrance aperture capped.
   * - **Output**
     - Timing Calibration Record
     - Laboratory evidence log
     - Quantitative measurements of clock frequency, pulse widths, and rise times.
   * - **Output**
     - Geometry Qualification Disposition
     - Pass / Fail record
     - Formal confirmation of 3648 effective pixel preservation and baseline stability.

Normative Requirements
----------------------

.. _uuid-0c19e046-af76-4b46-a595-ec5987fc0243:

**Requirement:** The Embedded calibration system shall verify that the master clock (fM) frequency measures within 2.000 MHz +/- 0.1% (1.998 MHz to 2.002 MHz) using a calibrated oscilloscope under standard laboratory temperature conditions before approving hardware for data acquisition.

   **Rationale:** The TCD1304DG charge transfer efficiency and the ADC sampling synchronization are calibrated assuming a nominal 2.0 MHz master timebase; exceeding a 0.1% frequency tolerance introduces timing skew across line readouts.

.. _uuid-8f6e3d36-b24c-42b8-8466-d5e00c683c7d:

**Requirement:** The Embedded calibration system shall verify that the captured raw frame preserves all 3648 effective detector pixels in strict monotonic spatial sequence with stable optical black baseline values across samples [16:28] under dark illumination conditions.

   **Rationale:** Spatial continuity and an uncorrupted optical black reference region are mandatory for the Host PC pipeline to calculate dynamic dark corrections and assign accurate spectral wavelengths.

.. _uuid-35904598-12ed-4eec-b319-c40361031432:

**Requirement:** The Embedded calibration system shall record the hardware serial number, firmware git commit hash, measurement instrument calibration IDs, and quantitative test outcomes for every calibration check to provide end-to-end evidence traceability.

   **Rationale:** Comprehensive configuration and instrument records ensure that spectrometer hardware revisions and firmware releases remain traceable to verifiable physical performance benchmarks.

Oscilloscope Timing Reference Procedure
---------------------------------------

To qualify detector driving waveforms, connect an oscilloscope with a bandwidth of at least 100 MHz to the designated test pads on the custom CCD driver board:

1. **Master Clock (fM) Qualification:**
   * Probe test point ``TP_FM`` (connected to PA8).
   * Measure frequency across a minimum of 10,000 cycles. Confirm frequency is :math:`2.000\,\text{MHz} \pm 2\,\text{kHz}`.
   * Measure pulse duty cycle. Confirm symmetry is :math:`50\% \pm 2\%`.
   * Measure 10%-to-90% rise and fall times. Confirm both are under :math:`20\,\text{ns}`.
2. **Shift Gate (SH) Pulse Qualification:**
   * Probe test point ``TP_SH`` (connected to PB0).
   * Measure the positive pulse width at 50% voltage threshold. Confirm pulse width is :math:`6.00\,\mu\text{s} \pm 50\,\text{ns}`.
   * Verify that pulse duration remains invariant across different integration time settings.
3. **Integration Clear Gate (ICG) Qualification:**
   * Probe test point ``TP_ICG`` (connected to PB6).
   * Measure the positive readout pulse width. Confirm width is :math:`7.388\,\text{ms} \pm 2\,\mu\text{s}`.
   * Verify that the SH pulse falls to ground before the falling edge of ICG to maintain valid charge transfer timing.

Frame Geometry and Baseline Verification Procedure
--------------------------------------------------

1. **Aperture Isolation:** Fit the spectrometer optical entrance aperture with an opaque metal cap to prevent stray photon leakage.
2. **Raw Stream Inspection:** Launch the ``spectrometer_com_inspector.py`` utility to record 500 contiguous raw binary frames.
3. **Array Dimension Validation:** Verify that every frame packet reports ``total_samples = 3694``, ``effective_start = 32``, and ``effective_count = 3648``.
4. **Optical Black Baseline Assessment:** Extract samples ``[16:28]`` across all 500 frames. Calculate the median dark baseline :math:`\beta_f` and standard deviation :math:`\sigma_f`:
   * Confirm that the optical black region shows no clipping at 0 or 4095 ADC counts.
   * Confirm that frame-to-frame baseline standard deviation does not exceed 5 ADC counts in a thermally stabilized environment.
5. **Effective Region Continuity:** Verify that no dead, stuck, or wrapped sample values appear across the active region ``[32:3679]``.
