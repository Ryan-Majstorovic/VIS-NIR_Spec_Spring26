Procedure
=========

.. _uuid-72bc2492-c269-4f25-ae8a-9de09e632da8:

Ordered Correction Behavior
---------------------------

UUID: :ref:`72BC2492-C269-4F25-AE8A-9DE09E632DA8 <uuid-72bc2492-c269-4f25-ae8a-9de09e632da8>`

1. Begin with the preserved raw ADC counts.
2. Apply stored bias correction when it is enabled and available.
3. Estimate the configured frame-wise dark reference from approved covered-input data.
4. Apply optional per-pixel dark offsets when enabled and compatible.
5. Preserve raw counts and record every applied or bypassed correction.

.. _uuid-27f1724a-6944-4cab-983b-c92295f40dec:

Correction Decisions
--------------------

UUID: :ref:`27F1724A-6944-4CAB-983B-C92295F40DEC <uuid-27f1724a-6944-4cab-983b-c92295f40dec>`

A requested correction shall not be silently applied with a missing or incompatible reference. Estimator, averaging count, reference selection, clipping, and detailed ordering are Not In Docs.

.. _uuid-8d910afa-ee31-4d4b-b295-dd7d591b9173:

Processing Conditions
---------------------

UUID: :ref:`8D910AFA-EE31-4D4B-B295-DD7D591B9173 <uuid-8d910afa-ee31-4d4b-b295-dd7d591b9173>`

* **requested references available**
* **optional correction bypassed**
* **requested reference unavailable**
