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
     - 6.0 us detector pulse (PA6 before board inversion)
     - Precision electronic shutter gate pulse transferring photo-charge.
   * - **Output**
     - Integration Clear Gate (ICG)
     - 8 us detector-low interval per frame (PB6 before board inversion)
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

**Requirement:** The Embedded timer system shall maintain a constant pulse high duration of 6.0 us (12 timer ticks at 2.0 MHz) for every emitted shift-gate (SH) detector pulse driven through PA6 under all valid integration times to preserve uniform charge-transfer dynamics.

   **Rationale:** Varying the pulse width of SH rather than its repetition interval distorts the electrostatic barrier beneath the photodiode transfer gates, inducing non-linear charge transfer and non-uniform pixel response.

.. _uuid-74a5107f-b5cb-4448-9b43-b93dadbeacfc:

**Requirement:** The Embedded timer system shall drive detector-polarity ICG low
for 8 us at the start of every physical frame and high for the remainder of the
frame, including continuation timer segments, to transfer the line after SH falls.

**Rationale:** The former 612 us low interval overlapped the next SH pulse at
short exposure settings; a fixed 8 us interval separates ICG rise from the
6 us SH pulse and still leaves at least 7992 us for the 7388 us readout.

**Requirement:** The Embedded timer system shall place the first detector SH
rise 0.5 us after ICG falls and its fall 6 us later during every physical frame
to provide nominal t2 = 0.5 us and t1 = 1.5 us.

**Rationale:** These separations support the datasheet t2 interval of 0.1 to
1 us, t3 minimum of 1 us, and t1 minimum of 1 us without changing SH width.

**Requirement:** The Embedded acquisition system shall start with 100 us
integration following reset to provide the measured corrected-timing starting profile.

**Rationale:** Dim-input trials resolved more useful contrast at 100 us than
at the 10 us minimum; startup exposure remains adjustable for actual illumination.

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
     - 0
     - 96.0 MHz
     - CH1 / ``PA8``
     - PWM Mode 1. ARR = 47 and CCR1 = 24 produce a 2 MHz master clock.
   * - ``TIM2``
     - 0
     - 96.0 MHz
     - TRGO Internal
     - High-resolution ADC conversion trigger. Generates TRGO pulse aligned with pixel video settling.
   * - ``TIM3``
     - 47
     - 2.0 MHz
     - CH1 / ``PA6``
     - PWM Mode 1. Generates Shift Gate (SH) with fixed CCR1 = 12 (6.0 us high pulse).
   * - ``TIM4``
     - 47
     - 2.0 MHz
     - CH1 / ``PB6``
     - PWM Mode 2. CCR1 = 16 in segment zero and zero thereafter; output inversion compensates board inversion.
   * - ``TIM5``
     - N/A
     - N/A
     - Unassigned
     - 32-bit general purpose timer reserved for future diagnostic or timing capacity.

Integration Time Scheduling Architecture
----------------------------------------

The firmware implements electronic shutter exposure control using the TCD1304DG electronic shutter mechanism. The requested exposure duration defines the SH repetition interval. Absolute optical exposure and sensor-side propagation require characterization:

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
* Segment zero contains the 8 us ICG-low interval and the SH transfer pulse.
* All subsequent segments keep ICG high and SH low until the next physical frame.

Seamless DMA Shadow Register Reload
-----------------------------------

To guarantee glitch-free multi-segment timing without software interrupt latency:

1. A precomputed schedule array of ``CcdTimingSegment`` structs (containing ``ARR`` and ``CCR`` values) is stored in SRAM.
2. ``DMA1_Stream2`` (mapped to TIM3 update) and ``DMA1_Stream6`` (mapped to TIM4 update) transfer the next segment's parameters directly into timer shadow registers at every timer overflow.
3. The hardware updates occur synchronously within a single clock cycle at counter zero, eliminating CPU latency and phase jitter.

Verification boundary
---------------------

**Requirement:** The scope validation system shall distinguish MCU-pad
observations from sensor-pin timing and optical pixel identification for each
capture to prevent software projections from being reported as physical validation.

**Rationale:** USB/SWD access cannot measure inverter propagation, sensor-pin
t4, ADC input settling, or identify an exact dummy element from a brightness threshold.

**Source evidence:** Toshiba TCD1304DG Rev. 1.5, pp. 5-8; user-approved production
timing correction, 2026-11-09. Captures and results are implementation evidence
in ``.scratch/production-timing/``, separate from these intended behaviors.
