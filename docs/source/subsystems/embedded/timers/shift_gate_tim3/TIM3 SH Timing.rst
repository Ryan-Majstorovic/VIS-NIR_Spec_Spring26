TIM3 SH Timing
==============

UUID: ``33D75617-7935-43B7-B7CC-303211704FEC``

**Requirement:** The Embedded SH timing system shall generate 6 us high pulses at the selected integration interval, independently of ICG, to preserve fixed shift-gate pulse shape.

**Rationale:** Changing pulse spacing instead of pulse high time controls exposure without introducing arbitrary transfer-pulse distortion.

The supported settings, common phase reference, application boundary, protocol,
and physical qualification checks are defined in :doc:`../CCD Timing`.
