Spectral Corrections
====================

.. note::

   Insert the user-provided I/O diagram here after the Visio source and image
   are available.

.. _uuid-84d8a9f5-623c-4394-b3dd-128259f5babf:

System Role
-----------

UUID: :ref:`84D8A9F5-623C-4394-B3DD-128259F5BABF <uuid-84d8a9f5-623c-4394-b3dd-128259f5babf>`

**Summary:** The Host PC spectral-corrections system applies separately
configured flat-field or PRNU, spectral-response or QE, and normalization
operations to wavelength-associated qualified data when their required inputs
are defined and compatible.

.. _uuid-f46a89e2-57af-4f66-a6c3-581cca0a2cfa:

System Objectives
-----------------

UUID: :ref:`F46A89E2-57AF-4F66-A6C3-581CCA0A2CFA <uuid-f46a89e2-57af-4f66-a6c3-581cca0a2cfa>`

**Objective 1:** **Correction entry.** Spectral Corrections shall apply
flat-field or PRNU, spectral-response or QE, and normalization operations only
when the selected factor and its pixel or wavelength association are present.

**Rationale:** Requiring both the factor and its axis association prevents a
correction from being applied to unrelated detector positions or wavelengths.

**Objective 2:** **Correction record.** Spectral Corrections shall apply each
configured operation separately and record the input, factor, basis, and result
of each applied or bypassed operation.

**Rationale:** Separate records preserve the effect and provenance of each
spectral transformation.

**Objective 3:** **Output and diagnostics.** Spectral Corrections shall report
missing factors, saturation, undefined normalization bases, and non-finite
results and shall prevent affected records from advancing.

**Rationale:** Explicit fault handling prevents invalid numerical results from
being presented or retained as usable spectra.

.. _uuid-367106a7-1f63-45f4-a2c6-40249f5d88ae:

Documentation Relationship
--------------------------

UUID: :ref:`367106A7-1F63-45F4-A2C6-40249F5D88AE <uuid-367106a7-1f63-45f4-a2c6-40249f5d88ae>`

.. list-table::
   :header-rows: 1

   * - Documentation
     - Responsibility
   * - :doc:`Inputs and Outputs <inputs_and_outputs>`
     - Accepted inputs, produced outputs, metadata, and unavailable or incompatible conditions.
   * - :doc:`Procedure <procedure>`
     - Ordered behavior, decisions, and processing conditions.
   * - :doc:`Diagnostics <diagnostics>`
     - Observable failure or qualification conditions and operator gating.
   * - :doc:`Testing <testing>`
     - Behavior-local scenarios and the current acceptance basis.
   * - :doc:`Calculations <calculations>`
     - Supported calculation or explicit absence of one, plus open requirements.
   * - :doc:`Validation <validation>`
     - Behavior claim, local traceability state, open decisions, and evidence method.

.. _uuid-b2b90870-82ad-44e0-979f-fee99d2947b7:

Pipeline Boundary
-----------------

UUID: :ref:`B2B90870-82AD-44E0-979F-FEE99D2947B7 <uuid-b2b90870-82ad-44e0-979f-fee99d2947b7>`

**Summary:** The Host PC spectral-corrections system receives qualified,
wavelength-associated data and supplies configured corrected intensity and
operation metadata for processed-record assembly. Factor convention,
equations, operation order, normalization basis, and tolerances remain
``Not In Docs``.

.. toctree::
   :maxdepth: 1
   :hidden:

   inputs_and_outputs
   procedure
   diagnostics
   testing
   calculations
   validation
