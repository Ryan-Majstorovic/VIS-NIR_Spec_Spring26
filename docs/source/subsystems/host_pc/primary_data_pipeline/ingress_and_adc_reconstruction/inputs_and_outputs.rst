Inputs and Outputs
==================

This page defines the requirements-backed Host PC boundary after device traffic
has crossed the Integration interface. The normative wire contract remains
owned by Integration.

.. _uuid-a21fdaa0-9bcf-4fa5-bff4-bb0bb98c3419:

Inputs
------

UUID: :ref:`A21FDAA0-9BCF-4FA5-BFF4-BB0BB98C3419 <uuid-a21fdaa0-9bcf-4fa5-bff4-bb0bb98c3419>`

* **Complete binary frame packet:** Device measurement content delivered over
  USB CDC with frame identity and status flags.
* **Effective detector geometry:** 3648 effective detector pixels.
* **Acquisition context:** The connection and acquisition-session state needed
  to decide whether received measurement content is eligible for processing.

.. _uuid-782b5cbe-1220-4f95-add4-4ed377911e35:

Outputs
-------

UUID: :ref:`782B5CBE-1220-4F95-ADD4-4ED377911E35 <uuid-782b5cbe-1220-4f95-add4-4ed377911e35>`

* **Raw ADC counts:** Ordered detector-domain values preserved before host-side
  calibration or correction.
* **Frame context:** Frame identity and status information retained with the
  raw measurement.
* **Ingress qualification:** An accepted-complete or rejected/incomplete
  condition that prevents unusable content from entering later stages.

.. _uuid-56aa8564-f48c-49db-b2f2-a98be7bcd7cf:

Wire Contract Ownership
-----------------------

UUID: :ref:`56AA8564-F48C-49DB-B2F2-A98BE7BCD7CF <uuid-56aa8564-f48c-49db-b2f2-a98be7bcd7cf>`

**Alignment State:** Not In Docs

Integration shall define the header, encoding, field ranges, framing,
resynchronization, and malformed-input behavior. Host PC documentation shall
consume that contract without duplicating it.

.. _uuid-50f12fd8-8d81-4cd7-87a7-f23a3c315f39:

Detector Geometry Boundary
--------------------------

UUID: :ref:`50F12FD8-8D81-4CD7-87A7-F23A3C315F39 <uuid-50f12fd8-8d81-4cd7-87a7-f23a3c315f39>`

The requirements define 3648 effective detector pixels. The total transported
sample count, placement of non-effective samples, and payload-size relationship
are **Not In Docs** and shall be supplied by the Integration wire contract.

.. _uuid-b0ba5251-52af-4f84-a378-0634d7b76da3:

Non-Measurement Traffic Boundary
--------------------------------

UUID: :ref:`B0BA5251-52AF-4F84-A378-0634D7B76DA3 <uuid-b0ba5251-52af-4f84-a378-0634d7b76da3>`

Non-measurement traffic shall not be emitted as a usable spectrum frame. Exact
text classification, buffering, and presentation behavior are **Not In Docs**
and remain part of the Integration and command/status contracts.
