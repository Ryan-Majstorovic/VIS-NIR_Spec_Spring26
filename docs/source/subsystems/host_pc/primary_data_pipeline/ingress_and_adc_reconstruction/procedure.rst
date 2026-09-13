Procedure
=========

.. _uuid-717c5b1c-0f29-4284-a60b-8d4e392b9df5:

Ordered Ingress Behavior
------------------------

UUID: :ref:`717C5B1C-0F29-4284-A60B-8D4E392B9DF5 <uuid-717c5b1c-0f29-4284-a60b-8d4e392b9df5>`

1. Accept measurement traffic only while the acquisition interface is available.
2. Accumulate enough content to evaluate whether a complete frame is present.
3. Confirm frame identity, status information, and 3648-effective-pixel geometry.
4. Preserve raw ADC counts and frame context for the next pipeline stage.
5. Reject or hold incomplete content without inventing samples.

.. _uuid-04bd2725-1958-48b5-9f8f-763464241e72:

Qualification Boundaries
------------------------

UUID: :ref:`04BD2725-1958-48B5-9F8F-763464241E72 <uuid-04bd2725-1958-48b5-9f8f-763464241e72>`

Only complete, requirements-conforming measurement content may advance. Total transported geometry, wire parsing, recovery, and resynchronization are Not In Docs and belong to Integration.

.. _uuid-5b6b365c-2fb7-4d70-84f7-0d65134d8be2:

Processing Conditions
---------------------

UUID: :ref:`5B6B365C-2FB7-4D70-84F7-0D65134D8BE2 <uuid-5b6b365c-2fb7-4d70-84f7-0d65134d8be2>`

* **complete frame available**
* **incomplete content retained or rejected**
* **unsupported geometry rejected**
