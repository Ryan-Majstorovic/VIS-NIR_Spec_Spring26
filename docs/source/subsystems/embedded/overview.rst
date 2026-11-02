Embedded System Overview
========================

.. figure:: /_static/diagrams/embedded/system-overview.png
   :alt: High-level Embedded system architecture showing the TCD1304DG sensor boundary, STM32F411 microcontroller timing and digitization subsystems, and host PC USB CDC transport interface.
   :width: 85%
   :align: center

   High-level Embedded system architecture and real-time execution model.

.. _uuid-dd4f5c01-b4f1-4809-ad9e-68b3059bebeb:

System Role
-----------

UUID: :ref:`DD4F5C01-B4F1-4809-AD9E-68B3059BEBEB <uuid-dd4f5c01-b4f1-4809-ad9e-68b3059bebeb>`

The Embedded system manages the hardware-level control, precision optical timing, analog digitization, and wire packetization for the VIS-NIR spectrometer. It executes bare-metal C firmware on an STM32F411CEU6 microcontroller to drive the Toshiba TCD1304DG linear CCD sensor, digitize detector pixel voltages with minimal jitter, and stream complete 3694-sample measurement frames to the Host PC over USB CDC at cadences up to 125 Hz.

.. _uuid-b5095b6c-c6fd-4966-9685-ae6966ceda21:

System Architecture & Real-Time Execution Model
-----------------------------------------------

UUID: :ref:`B5095B6C-C6FD-4966-9685-AE6966CEDA21 <uuid-b5095b6c-c6fd-4966-9685-ae6966ceda21>`

The embedded architecture is organized into synchronized functional layers to ensure microsecond timing determinism and zero frame loss:

1. **Precision Waveform Generation (Timers TIM1, TIM2, TIM3, TIM4):** Generates the continuous 2.0 MHz master clock (fM), electronic shutter shift gate (SH), frame integration clear gate (ICG), and synchronized ADC conversion triggers across exposure times from 10 us to 5 s.
2. **Direct Memory Access (DMA) Acquisition:** Couples ADC1 conversions directly to a circular 4-slot SRAM buffer pool via DMA, ensuring that all 3694 detector line samples are preserved in exact spatial order without CPU intervention.
3. **Command Processing & State Management:** Ingests ASCII command tokens over USB CDC, enforces valid exposure intervals (exact integer divisors of 8000 us for exposures at or below 8 ms), and reloads hardware timer schedules synchronously at physical frame boundaries.
4. **Wire Transport & CDC Stream Packetization:** Packages digitized sample arrays into 7416-byte binary packets (28-byte little-endian header with magic ``CCD1``, protocol version 2) and transmits frames over USB Full-Speed endpoints while multiplexing ASCII diagnostics.
5. **Hardware Calibration & Verification:** Provides benchtop oscilloscope procedures and automated regression suites to qualify waveform timing, spatial pixel geometry, and long-duration capture continuity.

.. _uuid-8e892af2-4ec5-40ac-922b-4e1dce44264a:

Subsystem Relationships
-----------------------

UUID: :ref:`8E892AF2-4EC5-40AC-922B-4E1DCE44264A <uuid-8e892af2-4ec5-40ac-922b-4e1dce44264a>`

.. list-table::
   :header-rows: 1

   * - Subsystem
     - Primary Engineering Responsibility
   * - :doc:`System Control and Hardware Interface <system_control_and_hardware_interface/index>`
     - STM32F411 clocking, NVIC priority arbitration, ASCII command dispatch, state machine transitions, and TCD1304DG driver board interface.
   * - :doc:`Timing and Data Acquisition <timing_and_data_acquisition/index>`
     - Consolidated timer architecture (TIM1-TIM4), electronic shutter exposure scheduling, 12-bit ADC digitization, and 4-slot circular DMA buffer management.
   * - :doc:`USB Transport and Verification <usb_transport_and_verification/index>`
     - 28-byte binary frame serialization, 125 Hz USB CDC transport delivery, oscilloscope timing calibration, and requirements traceability.

.. _uuid-704ce22a-40c3-4f92-ac0a-387165454c5a:

Integration & Boundary Responsibilities
---------------------------------------

UUID: :ref:`704CE22A-40C3-4F92-AC0A-387165454C5A <uuid-704ce22a-40c3-4f92-ac0a-387165454c5a>`

The Embedded system interacts with external entities across strictly delineated boundaries:

* **Detector Hardware Boundary (Optics / Sensor Hardware):** Directs logic-level clock pulses (fM, SH, ICG) to the TCD1304DG sensor and receives the conditioned analog video signal through the driver board front-end. It enforces hardware constraints such as 2.0 MHz clock stability and 6.0 us SH pulse duration.
* **Wire Transport Boundary (Integration):** Populates the shared wire contract defined in :doc:`Integration Interfaces <../integration/interfaces/system_boundaries/Integration Interfaces>`, transmitting 7416-byte binary packets and receiving ASCII commands over USB CDC. The Embedded system does not define host-side photometric corrections or UI display rendering.
* **Measurement Plane Output:** Produces fully qualified, raw 16-bit ADC sample frames containing all 3648 effective detector pixels for consumption by the Host PC Primary Data Pipeline.

Normative System Requirements
-----------------------------

.. _uuid-1c3c578d-65bf-40f8-beac-096c444a4db6:

**Requirement:** The Embedded system shall preserve all 3648 effective detector samples in strict spatial acquisition sequence for every accepted measurement frame under all supported exposure regimes.

   **Rationale:** Preserving sample acquisition order maintains the physical pixel-to-wavelength relationship required for optical dispersion mapping and prevents downstream corrections from being applied to the wrong detector positions.

.. _uuid-a1100223-1001-4001-8001-001122334403:

**Requirement:** The Embedded system shall transmit complete binary measurement frames over USB CDC with a monotonically incrementing 32-bit frame identifier and active integration time metadata at rates up to 125 Hz without silent frame truncation.

   **Rationale:** Unambiguous frame identifiers and explicit metadata permit the Host PC to detect transport loss, align temporal logs, and verify exposure state without guessing frame status.
