CCD Timing
==========

UUID: ``0B79E0A3-6CEE-4957-A820-C4B119B6FF9E``

The firmware uses hardware timers for repeatable CCD timing:

.. list-table::
   :header-rows: 1

   * - Signal / Role
     - Timer
     - Current Setting
   * - fM master clock
     - TIM1 CH1
     - 2 MHz, period 47, pulse 24, about 50 percent duty.
   * - ADC trigger clock
     - TIM2 TRGO / CH1
     - 500 kHz, period 191, pulse 96.
   * - SH timing
     - TIM3 CH1
     - Period 959, pulse 576.
   * - ICG frame timing
     - TIM4 CH1 plus interrupts
     - 8.000 ms period, period 7999, pulse 7388, low polarity.

TIM4 update starts capture at the ICG edge. TIM4 compare marks the ICG end edge
and disables TIM2. Oscilloscope validation should confirm these timing values at
the driver-board and CCD interface pins, not only at firmware configuration.



