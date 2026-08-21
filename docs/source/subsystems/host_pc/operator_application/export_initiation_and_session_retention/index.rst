Export Initiation And Session Retention
=======================================

.. note::

   Insert the user-provided I/O diagram here after the Visio source and image
   are available.

.. _uuid-4718cc11-20b8-4ab0-bf7a-398be00e1c99:

System Role
-----------

UUID: :ref:`4718CC11-20B8-4AB0-BF7A-398BE00E1C99 <uuid-4718cc11-20b8-4ab0-bf7a-398be00e1c99>`

**Summary:** The Host PC export-initiation-and-session-retention system shall
accept export requests for eligible retained sessions, preserve correspondence
among required raw and processed products, create required CSV output, report
the result, and retain reviewable session data according to the approved
policy.

.. _uuid-f3449780-965f-4c92-bc90-6cc21f8ef0b0:

System Objectives
-----------------

UUID: :ref:`F3449780-965F-4C92-BC90-6CC21F8EF0B0 <uuid-f3449780-965f-4c92-bc90-6cc21f8ef0b0>`

**Objective 1:** The Host PC export-initiation-and-session-retention system
shall accept export requests only for retained acquisition sessions.

   Rationale: Retained-session eligibility preserves the acquisition context of
   the requested export.

**Objective 2:** The Host PC export-initiation-and-session-retention system
shall confirm aligned raw ADC counts, processed counts, wavelength, volts, and
processed intensity before export.

   Rationale: Product alignment preserves row and value correspondence across
   raw and derived data.

**Objective 3:** The Host PC export-initiation-and-session-retention system
shall create CSV output containing the five required data products.

   Rationale: Including raw and derived products makes the required measurement
   data available to downstream review workflows.

**Objective 4:** The Host PC export-initiation-and-session-retention system
shall report successful, failed, or incomplete export outcomes.

   Rationale: Explicit outcome reporting prevents an unsuccessful or partial
   export from appearing successful.

**Objective 5:** The Host PC export-initiation-and-session-retention system
shall preserve retained data needed for review when export fails.

   Rationale: Preserving retained data supports recovery and review after a
   write failure.

**Objective 6:** The Host PC export-initiation-and-session-retention system
shall keep the session available according to the approved retention policy.

   Rationale: Policy-controlled availability supports later export or review
   without inventing a retention duration or storage mechanism.

.. _uuid-86047674-7d5d-411c-b6c5-929214569601:

System Relationship
-------------------

UUID: :ref:`86047674-7D5D-411C-B6C5-929214569601 <uuid-86047674-7d5d-411c-b6c5-929214569601>`

.. list-table::
   :header-rows: 1

   * - Documentation
     - Responsibility
   * - :doc:`Inputs and Outputs <inputs_and_outputs>`
     - Retained-session inputs, required CSV outputs, and outcome boundaries.
   * - :doc:`Procedure <procedure>`
     - Export eligibility, product checks, output creation, and retention workflow.
   * - :doc:`Diagnostics <diagnostics>`
     - Incomplete-data, write-failure, and schema-mismatch conditions.
   * - :doc:`Testing <testing>`
     - Requirements-based export behavior tests.
   * - :doc:`Calculations <calculations>`
     - Five-product correspondence and absence of a new measurement calculation.
   * - :doc:`Validation <validation>`
     - Local behavior claim, traceability state, and validation method.

.. _uuid-42e50d11-54c5-4644-83d7-b20c3b3d47ff:

Integration Boundary
--------------------

UUID: :ref:`42E50D11-54C5-4644-83D7-B20C3B3D47FF <uuid-42e50d11-54c5-4644-83d7-b20c3b3d47ff>`

**Summary:** The Host PC export-initiation-and-session-retention system consumes
eligible retained products from the Primary Data Pipeline and session context
from Session Control, and it produces required CSV content and outcome status
without adding measurement calculations. Filename, destination, overwrite
behavior, numeric precision, metadata, retention duration, and storage and
incomplete-session policies remain ``Not In Docs``.

.. toctree::
   :maxdepth: 1
   :hidden:

   inputs_and_outputs
   procedure
   diagnostics
   testing
   calculations
   validation
