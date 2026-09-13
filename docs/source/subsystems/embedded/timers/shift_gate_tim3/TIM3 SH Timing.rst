TIM3 SH Timing
==============

UUID: ``33D75617-7935-43B7-B7CC-303211704FEC``

The SH timing function shall generate the CCD shift-gate waveform with a
10 microsecond pulse target.  The SH pulse shall align with the ICG timing so
that the required ICG off time is preserved; the exact edge relationship and
off-time tolerance are ``Not In Docs``.  The relationship between SH and the
configurable integration-time request, period outside the pulse, polarity,
timer allocation, and output routing are also ``Not In Docs``.

**Expected outcome:** SH shifts the acquired line at the defined frame boundary
without changing the required effective-pixel ordering.



