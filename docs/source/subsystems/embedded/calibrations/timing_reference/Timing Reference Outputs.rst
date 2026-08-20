Timing Reference Outputs
========================

UUID: ``E935EEA3-4CC8-4BD6-B128-2B72C10D9352``

Expected outputs:

* fM measured at 2 MHz +/- 0.1% (1.998-2.002 MHz);
* SH measured against its 10 microsecond pulse target and checked for alignment
  that preserves the required ICG off time;
* ICG measured against an 8 ms period and 7.388 ms pulse targets;
* ADC-trigger behavior observed during the capture application boundary, which
  is ``Not In Docs`` until the shared control contract is specified; and
* a pass/fail record linking each capture to the hardware and requirement
  revisions.

The ADC-trigger frequency and all tolerances beyond the stated nominal values
remain ``Not In Docs``.



