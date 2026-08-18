Testing
=======

This page captures the current ingress-stage verification paths, including
mixed-stream manual checks, isolated throughput checks with the COM Inspector,
and the current gaps in automated coverage.

.. _uuid-4526a5fc-0cc6-4e64-b5db-e106297f9cb9:

Testing Matrix
--------------

UUID: :ref:`4526A5FC-0CC6-4E64-B5DB-E106297F9CB9 <uuid-4526a5fc-0cc6-4e64-b5db-e106297f9cb9>`

.. list-table::
   :header-rows: 1

   * - ID
     - Type
     - Name
     - Summary
     - UUID
   * - TEST-MAN-0
     - manual
     - Mixed Stream Receive Check
     - Confirm that the Host PC receives both binary ``CCD1`` frame traffic and
       newline-delimited ASCII firmware text without collapsing the stream into
       one packet type.
     - :ref:`C802C95B-13BA-47DE-B92E-7D68B32C3C46 <uuid-c802c95b-13ba-47de-b92e-7d68b32c3c46>`
   * - TEST-ACC-0
     - acceptance
     - COM Inspector 125 fps Check
     - Use the standalone COM Inspector to validate full-frame-rate reception
       without GUI overhead.
     - :ref:`9E1EBA19-AC5E-4677-A26A-B17FD30EE5D8 <uuid-9e1eba19-ac5e-4677-a26a-b17fd30ee5d8>`
   * - TEST-UNIT-TODO
     - unit
     - Automated Parser Unit Test
     - Placeholder for a future automated test that feeds known byte patterns
       into the ingress path and asserts the expected reconstructed outputs.
     - :ref:`35F1D383-D31E-4B02-867D-C0EF874BDF79 <uuid-35f1d383-d31e-4b02-867d-c0ef874bdf79>`
   * - TEST-REG-TODO
     - regression
     - Automated Receive Regression Harness
     - Placeholder for a future regression path that replays captured mixed
       binary-plus-text receive traces after parser or protocol changes.
     - :ref:`9FDC190F-B46D-4CBE-B8E2-C7AE9C84592C <uuid-9fdc190f-b46d-4cbe-b8e2-c7ae9c84592c>`

.. _uuid-c802c95b-13ba-47de-b92e-7d68b32c3c46:

Test TEST-MAN-0 - Mixed Stream Receive Check
--------------------------------------------

UUID: :ref:`C802C95B-13BA-47DE-B92E-7D68B32C3C46 <uuid-c802c95b-13ba-47de-b92e-7d68b32c3c46>`

Type: manual

Summary: Confirm that the live Host PC ingress path reconstructs frame content
and also logs ASCII banner or diagnostic lines when present.

[TODO] Add setup, execution, and acceptance details.

.. _uuid-9e1eba19-ac5e-4677-a26a-b17fd30ee5d8:

Test TEST-ACC-0 - COM Inspector 125 fps Check
---------------------------------------------

UUID: :ref:`9E1EBA19-AC5E-4677-A26A-B17FD30EE5D8 <uuid-9e1eba19-ac5e-4677-a26a-b17fd30ee5d8>`

Type: acceptance

Summary: Run
``python Spectrometer-COM-Inspector/spectrometer_com_inspector.py --port COMx --duration 60 --require-125fps``
with the GUI closed to isolate receive throughput. The acceptance path passes
only when the inspector reports at least ``124 fps``, ``0`` missed frame IDs,
``0`` bad sync bytes, ``sample_count=3694``, and ``flags=0x0001``.

[TODO] Add captured run evidence once an accepted inspection log is curated.

.. _uuid-35f1d383-d31e-4b02-867d-c0ef874bdf79:

Test TEST-UNIT-TODO - Automated Parser Unit Test
------------------------------------------------

UUID: :ref:`35F1D383-D31E-4B02-867D-C0EF874BDF79 <uuid-35f1d383-d31e-4b02-867d-c0ef874bdf79>`

Type: unit

Summary: Placeholder for a future automated test that feeds known byte patterns
into the receive parser and asserts the expected packet outputs and
retained-buffer behavior.

[TODO] Add setup, execution, and acceptance details.

.. _uuid-9fdc190f-b46d-4cbe-b8e2-c7ae9c84592c:

Test TEST-REG-TODO - Automated Receive Regression Harness
---------------------------------------------------------

UUID: :ref:`9FDC190F-B46D-4CBE-B8E2-C7AE9C84592C <uuid-9fdc190f-b46d-4cbe-b8e2-c7ae9c84592c>`

Type: regression

Summary: Placeholder for a future regression path that replays captured mixed
binary-plus-text receive traces after parser or protocol changes.

[TODO] Add setup, execution, and acceptance details.
