CCD Timing
==========

UUID: ``0B79E0A3-6CEE-4957-A820-C4B119B6FF9E``

The embedded controller shall generate repeatable CCD timing signals.  The
nominal values below are requirements-level targets and are not timer-register
settings.

.. list-table::
   :header-rows: 1

   * - Signal / role
     - Nominal requirement
   * - fM master clock
     - 2 MHz +/- 0.1% acceptance target.
   * - ICG frame timing
     - 8 ms period target with a 7.388 ms pulse target.
   * - SH shift gate
     - 10 microsecond pulse target.
   * - ADC conversion trigger
     - Required to support the detector readout cadence; exact frequency and phase are ``Not In Docs``.

The timing relationship between configurable integration time and SH/ICG is
also ``Not In Docs``.  The application boundary at which a requested setting
takes effect is likewise ``Not In Docs`` and remains an open shared contract.
Validation shall measure the signals at
the driver-board or CCD interface, not only at a configuration boundary.



