Frame Geometry Procedure
========================

UUID: ``53FEB0B0-95AB-405B-827D-B255FE50D192``

1. Capture at least one valid ``CCD1`` frame.
2. Record ``sample_count``, ``effective_start``, and ``effective_count`` from
   the frame header.
3. Compare those values with firmware constants and host ``DeviceConfig``.
4. Compute trailing dummy count as ``sample_count - effective_start -
   effective_count``.
5. Update firmware, host config, and documentation together if any value
   changes.



