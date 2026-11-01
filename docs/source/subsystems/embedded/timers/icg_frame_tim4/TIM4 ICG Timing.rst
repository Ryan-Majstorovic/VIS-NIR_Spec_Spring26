TIM4 ICG Timing
===============

UUID: ``51D66927-7652-4B5F-A591-22830C5F705F``

**Requirement:** The Embedded ICG timing system shall retain a 7.388 ms high readout interval and extend its low interval when integration exceeds 8 ms to provide complete detector readout at the reduced frame cadence.

**Rationale:** Keeping the readout interval constant preserves the sampling cadence while the extended low interval accommodates the requested exposure.

The supported settings, common phase reference, application boundary, protocol,
and physical qualification checks are defined in :doc:`../CCD Timing`.
