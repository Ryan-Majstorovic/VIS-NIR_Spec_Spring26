Embedded Validation
===================

UUID: ``542C4175-30A6-4498-8BE9-2DDDE4A65002``

Embedded validation shall include:

* detector-interface timing checks for fM, SH, ICG, and the ADC-trigger
  function against the approved timing requirements;
* ADC/DMA capture checks confirming all 3648 effective pixels are acquired in
  order without an unreported incomplete frame;
* minimum-rate checks confirming complete 3648-effective-sample frames are
  acquired and transferred at least 10 frames per second at the minimum
  integration time; this subsystem minimum is distinct from the system design
  target above 100 frames per second;
* USB CDC checks confirming that complete frames carry identity and status
  information as defined by Integration;
* control checks confirming that start, stop, and integration-time requests are
  received and handled according to the shared control contract.  The
  application boundary at which a request takes effect is ``Not In Docs``; and
* regression checks after changes to timing, acquisition, transport, or frame
  ownership responsibilities.

Stress duration, repetition count, packet-field checks, timeout semantics,
dropped-frame criteria, evidence retention, and the independent stream-inspector
procedure are ``Not In Docs`` and are owned by the shared verification plan.

Each check shall record its requirement identifier, hardware/configuration
revision, evidence artifact, and pass/fail or unresolved disposition.



