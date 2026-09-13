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

**Objective 1:** **Export entry.** Export Initiation and Session Retention shall
accept an export request only for a retained session containing raw counts,
processed counts, wavelength, volts, and processed intensity associated with
the same measurement.

**Rationale:** Requiring the five products from one measurement prevents
incomplete or cross-session data from entering the CSV.

**Objective 2:** **CSV creation.** Export Initiation and Session Retention shall
create one CSV row per detector position while preserving correspondence among
the five data products.

**Rationale:** Row-level correspondence keeps every raw and derived value tied
to the same detector position.

**Objective 3:** **Outcome and retention.** Export Initiation and Session
Retention shall report success, failure, or incomplete output and shall
preserve the retained session when CSV creation fails.

**Rationale:** Preserving the session supports review or another export attempt
without reacquiring the measurement.

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
