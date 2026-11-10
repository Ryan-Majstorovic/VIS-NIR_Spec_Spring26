Firmware Validation and Traceability
======================================

The Firmware Validation and Traceability subsystem provides the testing methodologies, automated regression suites, and requirements traceability matrix necessary to prove that the embedded firmware and hardware interfaces meet all normative system specifications.

.. _uuid-7a48e96f-ca96-41df-bd14-f4cc8f85791e:

Subsystem Role & Boundary
-------------------------

UUID: :ref:`7A48E96F-CA96-41DF-BD14-F4CC8F85791E <uuid-7a48e96f-ca96-41df-bd14-f4cc8f85791e>`

This subsystem bridges planned engineering requirements and verifiable implementation evidence. It manages both host-side automated software simulation tests and physical bench inspection procedures to confirm that timing schedules, DMA transfers, USB packet formatting, and error recovery behave deterministically.

Inputs and Outputs
------------------

.. list-table::
   :header-rows: 1

   * - Flow
     - Name
     - Type / Format
     - Description
   * - **Input**
     - Firmware Source Code
     - C source / headers
     - STM32 firmware files (``main.c``, ``ccd_timing.h``, ``usbd_cdc_if.c``).
   * - **Input**
     - Automated Test Runner
     - Python ``pytest`` suite
     - Host-side simulation tests validating schedule generation and timing math.
   * - **Output**
     - Test Execution Logs
     - Automated test output
     - Pass/fail verdicts for schedule generation, register bounds, and protocol packing.
   * - **Output**
     - Traceability Matrix
     - Traceability register
     - Formal mapping between system requirement IDs and implementation evidence.

Normative Requirements
----------------------

.. _uuid-08045c78-d973-4c2f-a247-f58f22e80f6f:

**Requirement:** The Embedded validation system shall execute automated regression tests verifying that the timer schedule generator calculates valid ARR and CCR register values across all short exposure divisors and long exposure intervals up to 5,000,000 us without numeric overflow before firmware images are approved for deployment.

   **Rationale:** Erroneous timer register calculations could generate out-of-range PWM values that violate sensor physical ratings or crash the microcontroller hardware timers during exposure adjustments.

.. _uuid-13631f48-c35c-4201-8a5d-57212e603bb4:

**Requirement:** The Embedded validation system shall confirm zero frame loss over continuous 10-minute acquisition runs under nominal 125 Hz capture conditions using an independent hardware or software stream inspector.

   **Rationale:** Proving continuous, zero-loss acquisition over extended intervals confirms that memory buffer rotation, USB DMA transfers, and host thread scheduling maintain adequate timing margin without buffer exhaustion.

.. _uuid-e7b83cd7-cc78-4db0-a21f-fe31ed8cce03:

**Requirement:** The Embedded validation system shall maintain an explicit traceability register linking every normative requirement ID to its defining documentation page, primary firmware code file, and verification test case.

   **Rationale:** Direct bi-directional traceability ensures that future code modifications or documentation revisions preserve intended instrument behavior and maintain test auditability.

Automated Verification Suite
----------------------------

The embedded timing and communication logic is verified through automated test suites:

1. **Timer Schedule Generation Tests (``PythonGUI/tests/test_ccd_timer_schedule.py``):**
   * Validates ``CcdIntegrationValid()`` across boundary conditions (9 us rejected, 10 us accepted, 8000 us accepted, 8001 us accepted, 5,000,000 us accepted, 5,000,001 us rejected).
   * Verifies that all integer divisors of 8000 us generate single-segment schedules with constant 6.0 us SH pulses.
   * Confirms multi-segment partitioning for exposures exceeding 32,000 us, ensuring each segment ARR does not exceed 16-bit limits (64,000 ticks).
2. **Integration Timing Controller Tests (``PythonGUI/tests/test_integration_timing.py``):**
   * Verifies state machine transitions between ``STOPPED``, ``RUNNING``, and ``RECONFIGURING``.
   * Verifies that the initial frame following an exposure change is discarded.
3. **Independent Stream Inspector (``Spectrometer-COM-Inspector/spectrometer_com_inspector.py``):**
   * Intercepts raw USB serial streams, verifies 32-byte binary packet headers, validates sequence counter monotonicity, and logs frame inter-arrival jitter.

Embedded Requirements Traceability Matrix
-----------------------------------------

.. list-table:: System Requirements Traceability Register
   :header-rows: 1

   * - Requirement ID
     - Core Intended Behavior
     - Primary Defining Page
     - Implementation Code File
     - Verification Test Case
   * - ``E1000001``
     - STM32F411CEU6 coordinates detector timing, acquisition, and USB handoff.
     - :doc:`../system_control_and_hardware_interface/microcontroller_and_firmware_architecture`
     - ``Core/Src/main.c``
     - Firmware compilation & boot verification.
   * - ``E1000002``
     - Generation of fM (2 MHz), SH (6 us pulse), and ICG (8 us low per frame) across 10 us to 5 s exposures.
     - :doc:`../timing_and_data_acquisition/ccd_timing_and_waveform_generation`
     - ``Core/Inc/ccd_timing.h``
     - ``test_ccd_timer_schedule.py`` & oscilloscope inspection.
   * - ``E1000003``
     - ADC DMA capture preserving all 3648 effective detector pixels in order.
     - :doc:`../timing_and_data_acquisition/adc_and_dma_acquisition`
     - ``Core/Src/main.c`` (``hadc1`` / ``hdma_adc1``)
     - ``test_integration_timing.py`` & dark frame verification.
   * - ``E1000004``
     - Complete binary measurement frames with 32-byte header and frame ID streamed over USB CDC.
     - :doc:`usb_cdc_stream_and_packetization`
     - ``USB_DEVICE/App/usbd_cdc_if.c``
     - ``spectrometer_com_inspector.py`` stream validation.
   * - ``E1000005``
     - Driver board routes timing, buffers analog video, and provides power isolation.
     - :doc:`../system_control_and_hardware_interface/driver_board_and_sensor_interface`
     - Hardware PCB Layout
     - Pre-power continuity check & bench signal inspection.
   * - ``E1000006``
     - Timing reference and frame geometry checks produce linked evidence.
     - :doc:`timing_and_frame_calibration`
     - Test register logs
     - Quantitative laboratory calibration records.
