Microcontroller and Firmware Architecture
===========================================

The Microcontroller and Firmware Architecture defines the hardware foundation and core execution environment of the embedded spectrometer. It governs clock generation, peripheral configuration, interrupt priority arbitration, and fault mitigation on the STM32F411CEU6 microcontroller.

.. _uuid-055460dd-92ac-463b-a4c9-0bc07ee74333:

Subsystem Role & Boundary
-------------------------

UUID: :ref:`055460DD-92AC-463B-A4C9-0BC07EE74333 <uuid-055460dd-92ac-463b-a4c9-0bc07ee74333>`

The microcontroller acts as the central real-time coordinator between the physical detector electronics and the host computer. It runs bare-metal C firmware using the ST Microelectronics Hardware Abstraction Layer (HAL). It owns peripheral register initialization, timer synchronization, DMA stream arbitration, and atomic state updates while delegating analytical calibration and spectrum visualization to the Host PC.

Inputs and Outputs
------------------

.. list-table::
   :header-rows: 1

   * - Flow
     - Name
     - Type / Electrical Range
     - Description
   * - **Input**
     - External Crystal Oscillator
     - 25.0 MHz CMOS clock
     - High-speed external (HSE) clock source driving the system PLL.
   * - **Input**
     - Host USB VBUS & Control
     - 5.0 V / USB D+/D- lines
     - Enumeration power and USB CDC packet transport.
   * - **Input**
     - CCD Video Analog Input
     - 0.0 V to 3.3 V on PA0
     - Conditioned detector video output connected to ADC1 Channel 0.
   * - **Output**
     - Detector Master Clock (fM)
     - 2.0 MHz 3.3 V PWM on PA8
     - Continuous master driving clock routed to the CCD driver board.
   * - **Output**
     - Shift Gate (SH)
     - 3.3 V pulse on PB0
     - Line transfer gate pulse controlling exposure interval.
   * - **Output**
     - Integration Clear Gate (ICG)
     - 3.3 V pulse on PB6
     - Readout gate pulse defining frame boundaries.
   * - **Output**
     - USB CDC Stream
     - Full-Speed 12 Mbps differential
     - Interleaved binary frame packets and ASCII status responses.

Normative Requirements
----------------------

.. _uuid-25a8523c-d3df-4cb0-8b88-fa340ac5105a:

**Requirement:** The Embedded microcontroller system shall configure the Phase-Locked Loop (PLL) from a 25.0 MHz high-speed external crystal to produce a stable 96.0 MHz system clock (SYSCLK) with an APB1 peripheral clock of 48.0 MHz and an APB2 peripheral clock of 96.0 MHz under normal operating conditions to maintain deterministic timer timebases.

   **Rationale:** Microcontroller timer frequencies directly govern CCD master clock stability, shift-gate pulse widths, and ADC trigger cadences; drifting clock frequencies distort optical integration times and corrupt wavelength repeatability.

.. _uuid-cca27ba8-11cc-4a99-9d5b-1580d5d3b0a3:

**Requirement:** The Embedded microcontroller system shall configure peripheral interrupt preemption priorities such that ADC DMA conversion-complete and Timer update events preempt communication and background tasks under high-rate streaming to prevent ADC buffer overrun and sample desynchronization.

   **Rationale:** Digitization and buffer arming operate on strict microsecond deadlines; prioritizing acquisition interrupts over USB transmission prevents lost samples and broken frame phase relationships.

.. _uuid-fe67059f-543c-411c-94be-bc1d01edd4b2:

**Requirement:** The Embedded microcontroller system shall halt all active waveform timers (TIM1, TIM2, TIM3, TIM4) and disable ADC DMA streams under detected timing fault conditions to produce a safe instrument shutdown state.

   **Rationale:** Abrupt or unsynchronized timer updates can violate the minimum low/high pulse specifications of the TCD1304DG CCD, risking sensor latchup or distorted electronic readout.

Hardware Architecture & Pin Allocation
--------------------------------------

The embedded platform employs an STM32F411CEU6 microcontroller (ARM Cortex-M4 with single-precision FPU, 512 KB Flash, 128 KB SRAM, operating up to 100 MHz):

.. list-table:: Microcontroller Pin and Peripheral Assignment
   :header-rows: 1

   * - Pin
     - Peripheral Function
     - Direction
     - Description / Connection
   * - ``PA0``
     - ``ADC1_IN0``
     - Input (Analog)
     - Conditioned analog video output from CCD driver board buffer.
   * - ``PA8``
     - ``TIM1_CH1``
     - Output (Alternate Function AF1)
     - Detector master clock (fM) running at 2.0 MHz square wave.
   * - ``PB0``
     - ``TIM3_CH1``
     - Output (Alternate Function AF2)
     - CCD Shift Gate (SH) pulse output.
   * - ``PB6``
     - ``TIM4_CH1``
     - Output (Alternate Function AF2)
     - CCD Integration Clear Gate (ICG) pulse output.
   * - ``PA11``
     - ``USB_OTG_FS_DM``
     - Bidirectional
     - Full-Speed USB data minus line.
   * - ``PA12``
     - ``USB_OTG_FS_DP``
     - Bidirectional
     - Full-Speed USB data plus line.
   * - ``PC13``
     - ``GPIO_Output``
     - Output
     - Onboard diagnostic indicator LED.

Execution Model and Concurrency
-------------------------------

The firmware executes a hybrid foreground/background interrupt-driven architecture:

1. **Hardware Interrupt Service Routines (ISRs):**
   * **TIM4 Period Elapsed ISR:** Signals frame boundaries and triggers state reconfigurations or next-frame arming.
   * **ADC DMA Complete ISR (``DMA2_Stream0``):** Signals that all 3694 line samples have been transferred into the active SRAM frame buffer, increments frame counters, and flags the slot as ready for USB dispatch.
   * **Timer Burst DMA ISRs (``DMA1_Stream2`` / ``DMA1_Stream6``):** Service TIM3 and TIM4 shadow register updates during multi-segment long integration schedules without CPU intervention.
2. **Main Application Loop:**
   * Scans the circular frame buffer pool for completed frame packets ready for USB CDC transmission.
   * Processes incoming host command bytes from the ring buffer.
   * Dispatches periodic ASCII status lines and manages transition timeouts.
