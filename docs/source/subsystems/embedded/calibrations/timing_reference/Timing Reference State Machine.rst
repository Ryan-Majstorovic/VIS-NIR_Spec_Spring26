Timing Reference State Machine
==============================

UUID: ``C1D2E3F4-5061-4789-ABCD-0123456789EF``

The timing-reference check follows these states:

1. **Ready:** requirements, configuration, observation points, and evidence
   destination are identified.
2. **Capturing:** fM, SH, ICG, and ADC-trigger behavior are measured during the
   defined acquisition window.
3. **Assessing:** measurements are compared with the approved nominal targets
   and tolerances.
4. **Recorded:** measurements, configuration identity, evidence links, and
   pass/fail disposition are retained.
5. **Open:** if a tolerance, observation point, or evidence rule is missing,
   the result remains unresolved rather than being marked passed.



