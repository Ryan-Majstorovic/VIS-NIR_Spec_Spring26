Frame Geometry State Machine
============================

UUID: ``D2E3F405-6172-489A-BCDE-1234567890F1``

The frame-geometry check follows these states:

1. **Ready:** the approved effective-pixel requirement and capture conditions
   are identified.
2. **Captured:** a complete frame and associated identity/status information are
   available.
3. **Assessing:** effective-pixel count, ordering, and approved boundaries are
   compared with the capture.
4. **Recorded:** evidence, configuration identity, and pass/fail or unresolved
   disposition are retained.
5. **Open:** if total geometry or transport semantics are unspecified, the
   result remains ``Not In Docs``.



