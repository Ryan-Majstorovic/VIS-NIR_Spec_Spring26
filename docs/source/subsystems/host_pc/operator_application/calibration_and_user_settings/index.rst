Calibration And User Settings
=============================

.. note::

   Insert the user-provided I/O diagram here after the Visio source and image
   are available.

.. _uuid-99d3b5e7-275e-4b3b-b833-6d73656602b1:

System Role
-----------

UUID: :ref:`99D3B5E7-275E-4B3B-B833-6D73656602B1 <uuid-99d3b5e7-275e-4b3b-b833-6d73656602b1>`

**Summary:** The Host PC calibration-and-user-settings system shall let the
operator select calibration inputs and save or recall user settings, validate
requested selections, activate only accepted configuration, and report
outcomes without defining calibration mathematics or storage formats.

.. _uuid-88effb81-07da-4b40-acda-d750932c774f:

System Objectives
-----------------

UUID: :ref:`88EFFB81-07DA-4B40-ACDA-D750932C774F <uuid-88effb81-07da-4b40-acda-d750932c774f>`

**Objective 1:** The Host PC calibration-and-user-settings system shall present
bias or dark, wavelength, flat-field or PRNU, and spectral-response or QE
selection categories.

   Rationale: Visible configuration categories allow each supported calibration
   input to be selected independently.

**Objective 2:** The Host PC calibration-and-user-settings system shall validate
requested selections against the active detector and processing context.

   Rationale: Compatibility validation prevents configuration intended for a
   different detector or processing context from being activated.

**Objective 3:** The Host PC calibration-and-user-settings system shall activate
accepted selections for subsequent processing.

   Rationale: Activation establishes the accepted configuration that governs
   later processing.

**Objective 4:** The Host PC calibration-and-user-settings system shall prevent
missing or incompatible selections from being silently activated.

   Rationale: Explicit rejection prevents an unavailable selection or silent
   substitution from changing later processing.

**Objective 5:** The Host PC calibration-and-user-settings system shall save or
recall user settings and report the outcome.

   Rationale: Outcome reporting confirms whether the requested configuration
   change became available.

**Objective 6:** The Host PC calibration-and-user-settings system shall preserve
the current active configuration when selection, save, or recall fails.

   Rationale: Preserving a known active configuration prevents a failed request
   from leaving the governing settings ambiguous.

.. _uuid-15ed5613-3a5a-4d14-bb75-0785f7ef044e:

System Relationship
-------------------

UUID: :ref:`15ED5613-3A5A-4D14-BB75-0785F7EF044E <uuid-15ed5613-3a5a-4d14-bb75-0785f7ef044e>`

.. list-table::
   :header-rows: 1

   * - Documentation
     - Responsibility
   * - :doc:`Inputs and Outputs <inputs_and_outputs>`
     - Configuration inputs, active configuration, and outcome boundaries.
   * - :doc:`Procedure <procedure>`
     - Selection, validation, activation, save, and recall workflow.
   * - :doc:`Diagnostics <diagnostics>`
     - Missing, incompatible, and failed-save conditions.
   * - :doc:`Testing <testing>`
     - Requirements-based configuration behavior tests.
   * - :doc:`Calculations <calculations>`
     - Absence of calibration mathematics and open configuration requirements.
   * - :doc:`Validation <validation>`
     - Local behavior claim, traceability state, and validation method.

.. _uuid-3ec98c16-6167-4966-875e-cb37d9e537b9:

Integration Boundary
--------------------

UUID: :ref:`3EC98C16-6167-4966-875E-CB37D9E537B9 <uuid-3ec98c16-6167-4966-875e-cb37d9e537b9>`

**Summary:** The Host PC calibration-and-user-settings system manages operator
selection and configuration outcomes, while the Primary Data Pipeline owns
calibration calculations and application order. Formats, versions, defaults,
persistence locations, compatibility rules, and startup self-test behavior
remain ``Not In Docs``.

.. toctree::
   :maxdepth: 1
   :hidden:

   inputs_and_outputs
   procedure
   diagnostics
   testing
   calculations
   validation
