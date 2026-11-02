CCD Timing and Waveform Generation
===================================

The CCD Timing and Waveform Generation system coordinates all microcontroller hardware timers to generate the synchronized driving waveforms required by the Toshiba TCD1304DG linear CCD sensor. It implements an electronic-shutter exposure scheduling engine supporting integration durations from 10 us to 5 s with sub-microsecond determinism.

.. _uuid-83fc581c-bd41-4cf0-8a77-d7f2f42bcd24:

Subsystem Role & Boundary
-------------------------

UUID: :ref:`83FC581C-BD41-4CF0-8A77-D7F2F42BCD24 <uuid-83fc581c-bd41-4cf0-8a77-d7f2f42bcd24>`

The timer engine controls the physical charge-accumulation and readout lifecycle of the spectrometer. By utilizing hardware timers tied to the 96 MHz internal bus, it produces the master clock (fM), shift gate (SH), integration clear gate (ICG), and ADC conversion triggers without relying on software delays.

Inputs and Outputs
------------------

.. list-table::
   :header-rows: 1

   * - Flow
     - Name
     - Type / Units
     - Description
   * - **Input**
     - Integration Request
     - Integer microseconds
     - Host-demanded exposure duration (10 us to 5,000,000 us).
   * - **Input**
     - MCU Internal Clock
     - 96.0 MHz digital
     - High-stability timer bus clock derived from HSE crystal PLL.
   * - **Output**
     - Master Clock (fM)
     - 2.0 MHz square wave (PA8)
     - Symmetrical 50% duty clock driving sensor internal shift registers.
   * - **Output**
     - Shift Gate (SH)
     - 6.0 us pulse (PB0)
     - Precision electronic shutter gate pulse transferring photo-charge.
   * - **Output**
     - Integration Clear Gate (ICG)
     - 7.388 ms high pulse (PB6)
     - Readout gate signal controlling charge transfer to output amplifier.
   * - **Output**
     - ADC Trigger (TRGO)
     - Periodic trigger pulse
     - Hardware trigger initiating ADC conversion for each pixel.

Normative Requirements
----------------------

.. _uuid-2e8241fc-5a5c-4f81-a134-93128e88703e:

**Requirement:** The Embedded timer system shall generate the master clock (fM) on PA8 as a continuous 2.0 MHz +/- 0.1% square wave with a 50% duty cycle under all operational states to drive the TCD1304DG internal shift registers.

   **Rationale:** The TCD1304DG requires a continuous 2.0 MHz driving frequency to maintain stable internal charge transfer efficiency and prevent thermal charge leakage during active line readout.

.. _uuid-b2c3014d-f0cc-4941-81e7-09fb6163d08a:

**Requirement:** The Embedded timer system shall maintain a constant pulse high duration of 6.0 us (12 timer ticks at 2.0 MHz) for every emitted shift-gate (SH) pulse on PB0 under all valid integration times to preserve uniform charge-transfer dynamics.

   **Rationale:** Varying the pulse width of SH rather than its repetition interval distorts the electrostatic barrier beneath the photodiode transfer gates, inducing non-linear charge transfer and non-uniform pixel response.

.. _uuid-74a5107f-b5cb-4448-9b43-b93dadbeacfc:

**Requirement:** The Embedded timer system shall generate the integration clear gate (ICG) on PB6 with a constant high readout interval of 7.388 ms (14,776 timer ticks at 2.0 MHz) for every physical frame readout under both short and long exposure regimes.

   **Rationale:** The 3694 detector line elements require exactly 7.388 ms to read out sequentially at the 2.0 MHz pixel cadence (2 clock cycles per pixel = 1 us/pixel; 3694 us active readout plus analog settling intervals); altering the readout interval disrupts pixel acquisition synchronization.

.. _uuid-f805db53-c28c-4f0f-ba98-548d34a9c887:

**Requirement:** The Embedded timer system shall accept integration time requests from 10 us through 5,000,000 us, requiring that requests at or below 8,000 us be exact integer divisors of 8,000 us, to maintain a synchronous phase relationship between SH and the 125 Hz frame boundary.

   **Rationale:** Enforcing exact integer divisors of 8,000 us ensures that multiple electronic shutter pulses fit into an 8.0 ms frame without phase jitter, preserving the 125 Hz capture cadence.

Timer Peripheral Allocations
----------------------------

The embedded architecture allocates five dedicated timer peripherals to coordinate instrument timing:

.. list-table:: Hardware Timer Allocations and Configurations
   :header-rows: 1

   * - Timer
     - Prescaler (PSC)
     - Clock Rate
     - Channel / Pin
     - Mode & Operational Role
   * - ``TIM1``
     - 47
     - 2.0 MHz
     - CH1 / ``PA8``
     - PWM Mode 1. Generates continuous 2.0 MHz master clock (fM) with ARR = 1 and CCR1 = 1.
   * - ``TIM2``
     - 0
     - 96.0 MHz
     - TRGO Internal
     - High-resolution ADC conversion trigger. Generates TRGO pulse aligned with pixel video settling.
   * - ``TIM3``
     - 47
     - 2.0 MHz
     - CH1 / ``PB0``
     - PWM Mode 1. Generates Shift Gate (SH) with fixed CCR1 = 12 (6.0 us high pulse).
   * - ``TIM4``
     - 47
     - 2.0 MHz
     - CH1 / ``PB6``
     - PWM Mode 2. Generates ICG frame readout pulse with fixed 7.388 ms high time.
   * - ``TIM5``
     - N/A
     - N/A
     - Unassigned
     - 32-bit general purpose timer reserved for future diagnostic or timing capacity.

Integration Time Scheduling Architecture
----------------------------------------

The firmware implements electronic shutter exposure control using the TCD1304DG electronic shutter mechanism. The exposure duration represents the time between the final shift gate (SH) pulse and the subsequent falling edge of ICG:

Short Exposure Regime (:math:`10\,\mu\text{s} \le t_{\text{int}} \le 8000\,\mu\text{s}`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the short exposure regime, the frame repetition rate is fixed at 125 Hz (:math:`8.0\,\text{ms}` period):

* The integration time :math:`t_{\text{int}}` must be an exact integer divisor of :math:`8000\,\mu\text{s}` (e.g., 10, 16, 20, 25, 32, 40, 50, 64, 80, 100, 125, 160, 200, 250, 320, 400, 500, 800, 1000, 1600, 2000, 4000, 8000 us).
* ``TIM3`` (SH) operates with an auto-reload value of :math:`\text{ARR} = 2 \times t_{\text{int}} - 1` ticks.
* During each 8.0 ms frame, multiple SH pulses clear intermediate charge from the photodiodes. The final SH pulse transfers the accumulated optical charge into the analog shift register immediately prior to readout.

Long Exposure Regime (:math:`t_{\text{int}} > 8000\,\mu\text{s}`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For integration times exceeding 8 ms, the overall frame duration expands to match the exposure time:

* Because 16-bit hardware counters overflow at :math:`32.768\,\text{ms}` at a 2.0 MHz tick rate, exposures longer than :math:`32\,\text{ms}` cannot be accommodated in a single timer cycle.
* The exposure engine subdivides the integration duration into :math:`N` uniform segments of at most :math:`32000\,\mu\text{s}`:

  .. math::

     N = \left\lceil \frac{t_{\text{int}}}{32000} \right\rceil

* For a 5.0 s exposure, :math:`N = 157` segments.
* During segments :math:`0` through :math:`N-2`, ``TIM4`` (ICG) remains held low, inhibiting readout while optical photons accumulate.
* In the final segment :math:`N-1`, ``TIM4`` generates the 7.388 ms high readout pulse to transfer the accumulated line charge.

Seamless DMA Shadow Register Reload
-----------------------------------

To guarantee glitch-free multi-segment timing without software interrupt latency:

1. A precomputed schedule array of ``CcdTimingSegment`` structs (containing ``ARR`` and ``CCR`` values) is stored in SRAM.
2. ``DMA1_Stream2`` (mapped to TIM3 update) and ``DMA1_Stream6`` (mapped to TIM4 update) transfer the next segment's parameters directly into timer shadow registers at every timer overflow.
3. The hardware updates occur synchronously within a single clock cycle at counter zero, eliminating CPU latency and phase jitter.
