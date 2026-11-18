Driver Board and Sensor Interface
=================================

The Driver Board and Sensor Interface subsystem connects the digital outputs and analog input of the STM32F411 microcontroller to the Toshiba TCD1304DG linear CCD sensor. It provides clock buffering, analog signal conditioning, power filtering, and grounding isolation required to capture high-resolution optical measurements.

.. _uuid-bb09e6f0-6aae-43da-ac43-33d1f9cb9662:

Subsystem Role & Boundary
-------------------------

UUID: :ref:`BB09E6F0-6AAE-43DA-AC43-33D1F9CB9662 <uuid-bb09e6f0-6aae-43da-ac43-33d1f9cb9662>`

The driver board is a dedicated printed circuit board (PCB) holding the TCD1304DG linear image sensor, level translators, analog buffer amplifiers, and low-dropout (LDO) voltage regulators. It terminates the high-speed digital timing lines from the MCU and converts the raw CCD output signal (OS) into a low-impedance voltage suitable for direct sampling by the STM32 internal ADC.

Inputs and Outputs
------------------

.. list-table::
   :header-rows: 1

   * - Flow
     - Name
     - Type / Electrical Range
     - Description
   * - **Input**
     - Raw DC Power
     - +5.0 V DC (USB or external)
     - Primary power supply input for sensor and analog regulators.
   * - **Input**
     - Digital Driving Pulses
     - 3.3 V CMOS (fM, SH, ICG)
     - High-speed timing signals delivered from STM32 GPIOs.
   * - **Input**
     - Sensor Video Signal (OS)
     - ~1.5 V to 3.5 V analog
     - High-impedance raw video output from pin 4 of the TCD1304DG.
   * - **Output**
     - Conditioned Video Signal
     - 0.0 V to 3.0 V analog to PA0
     - Buffered, low-impedance analog voltage delivered to the MCU ADC.
   * - **Output**
     - Buffered Sensor Clocks
     - 4.0 V to 5.0 V logic
     - Level-shifted, fast-rise driving clocks delivered to sensor pins.

Normative Requirements
----------------------

.. _uuid-d91c13ac-3dac-42fd-86c1-b4718036bdfa:

**Requirement:** The Embedded driver board system shall buffer the 2.0 MHz master clock (fM), shift gate (SH), and integration clear gate (ICG) signals using high-speed logic drivers under full operating temperature to maintain clock edge rise and fall times under 20 ns at the TCD1304DG pins.

   **Rationale:** Slow clock transitions or excessive capacitive loading on the detector control pins causes phase delay and erratic charge transfer along the internal CCD analog shift register, inducing spatial distortion.

.. _uuid-fdcdfc53-48da-4902-86cf-647843e7531a:

**Requirement:** The Embedded driver board system shall condition the high-impedance detector video output signal (OS) with an analog buffer amplifier featuring a bandwidth of at least 10 MHz and an output impedance below 50 ohms under continuous readout to drive the microcontroller ADC sampling capacitor without charge-sharing attenuation.

   **Rationale:** The internal sampling capacitor of the STM32 ADC requires rapid settling within the microsecond conversion window; inadequate drive capability causes ghosting between adjacent pixel voltages and reduces dynamic range.

.. _uuid-b1cd887c-fc7e-4b00-a531-704d86be2a52:

**Requirement:** The Embedded driver board system shall provide independent low-noise linear regulation and star-ground isolation for the analog and digital supply domains under powered operation to maintain peak-to-peak power rail noise below 10 mV.

   **Rationale:** High-frequency digital switching transients from the microcontroller and clock buffers couple into the sensitive analog output signal of the CCD if grounds or power rails are shared, degrading system signal-to-noise ratio (SNR).

Detector Architecture & Pinout
------------------------------

The Toshiba TCD1304DG is a high-sensitivity 3694-element linear CCD image sensor packaged in a 22-pin cerdip DIP:

.. list-table:: TCD1304DG Critical Signal Connections
   :header-rows: 1

   * - Pin Number
     - Symbol
     - Type
     - Function & Interface Routing
   * - ``1``
     - ``Vdd``
     - Power
     - +4.0 V to +5.5 V analog positive supply rail.
   * - ``2``
     - ``Vref``
     - Reference
     - Substrate bias voltage bypass point (decoupled to analog ground).
   * - ``3``
     - ``Vss``
     - Ground
     - Ground reference plane (analog star point).
   * - ``4``
     - ``OS``
     - Analog Output
     - Output video signal; drops downward with increasing light exposure.
   * - ``7``
     - ``fM``
     - Digital Input
     - 2.0 MHz master clock driving internal charge-transfer gates.
   * - ``8``
     - ``SH``
     - Digital Input
     - Shift gate; pulses high to dump photodiode charge into shift register.
   * - ``9``
     - ``ICG``
     - Digital Input
     - Integration clear gate; gates shift-register charge to readout node.

Analog Front-End Conditioning
-----------------------------

The raw CCD output signal operates with negative optical polarity: an unexposed dark pixel presents a high resting voltage (typically ~2.5 V to 3.0 V), while light exposure causes the voltage to drop downward toward ground.

1. **Impedance Transformation:** A high-speed emitter-follower transistor or operational amplifier (such as the AD8021 or OPA350) transforms the high-impedance output of the sensor into a low-impedance source.
2. **Dynamic Range Matching:** The conditioning circuitry references the signal against the STM32 ADC reference voltage (3.3 V), ensuring the full optical swing spans the linear digitization range of the 12-bit ADC.
3. **Pre-Power Verification:** Prior to initial powered testing, bench verification procedures mandate multimeter resistance and continuity checks between power rails, ground, and signal lines to prevent catastrophic sensor damage from reversed polarity or shorted rails.
