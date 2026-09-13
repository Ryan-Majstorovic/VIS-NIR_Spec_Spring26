TIM4 ICG Timing
===============

UUID: ``51D66927-7652-4B5F-A591-22830C5F705F``

The ICG timing function shall delimit each detector integration and readout
frame.  Its nominal target is an 8 ms period with a 7.388 ms pulse.  The
10 microsecond SH pulse shall align with ICG so that the required ICG off time
is preserved; the exact edge relationship and off-time tolerance are ``Not In
Docs``.  Polarity, edge ownership, timer allocation, interrupt behavior, and
the exact capture start/stop relationship are also ``Not In Docs``.

**Expected outcome:** A frame boundary is repeatable, observable at the CCD
interface, and used consistently by acquisition and frame identity.



