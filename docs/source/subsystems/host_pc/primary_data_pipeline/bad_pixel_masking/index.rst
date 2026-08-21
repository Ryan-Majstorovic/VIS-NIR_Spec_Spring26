Bad Pixel Masking
=================

.. note::

   Insert the user-provided I/O diagram here after the Visio source and image
   are available.

.. _uuid-3f21efce-bc97-43e0-9186-7ef999385ba0:

System Role
-----------

UUID: :ref:`3F21EFCE-BC97-43E0-9186-7EF999385BA0 <uuid-3f21efce-bc97-43e0-9186-7ef999385ba0>`

**Summary:** The Host PC bad-pixel-masking system qualifies known unreliable
detector positions using a geometry-compatible mask and carries mask identity
and affected positions with the processed record.

.. _uuid-7210ef46-9e87-4ff5-a0b0-67e6bdea3920:

System Objectives
-----------------

UUID: :ref:`7210EF46-9E87-4FF5-A0B0-67E6BDEA3920 <uuid-7210ef46-9e87-4ff5-a0b0-67e6bdea3920>`

**Objective 1:** The Host PC bad-pixel-masking system shall receive corrected
counts with the applicable mask and detector-geometry identity.

   Rationale: Associating the mask with corrected data and geometry establishes
   the context required to qualify detector positions.

**Objective 2:** The Host PC bad-pixel-masking system shall confirm mask
compatibility with the active detector geometry before applying the mask.

   Rationale: Geometry compatibility prevents mask entries from being assigned
   to the wrong detector positions.

**Objective 3:** The Host PC bad-pixel-masking system shall mark or exclude
known-bad positions before wavelength or spectral use.

   Rationale: Early qualification prevents unreliable detector positions from
   silently becoming valid downstream values.

**Objective 4:** The Host PC bad-pixel-masking system shall carry mask identity
and affected detector positions with the processed record.

   Rationale: Mask provenance supports interpretation and reproduction of the
   qualified result.

**Objective 5:** The Host PC bad-pixel-masking system shall surface missing,
mismatched, or invalid-propagation conditions rather than silently applying the
mask.

   Rationale: Failure visibility prevents an unavailable or incompatible mask
   from appearing to have qualified the measurement.

**Objective 6:** The Host PC bad-pixel-masking system shall prevent unresolved
invalid-value, interpolation, replacement, or edge behavior from being applied
as an accepted masking result.

   Rationale: Blocking undefined treatment prevents invented replacement values
   from entering downstream processing.

.. _uuid-32527a47-60c8-41ae-b446-9e3e5118ae17:

Documentation Relationship
--------------------------

UUID: :ref:`32527A47-60C8-41AE-B446-9E3E5118AE17 <uuid-32527a47-60c8-41ae-b446-9e3e5118ae17>`

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

.. _uuid-67efd8d9-a1d1-47df-a28a-2fb1f94fa06a:

Pipeline Boundary
-----------------

UUID: :ref:`67EFD8D9-A1D1-47DF-A28A-2FB1F94FA06A <uuid-67efd8d9-a1d1-47df-a28a-2fb1f94fa06a>`

**Summary:** The Host PC bad-pixel-masking system receives corrected counts
after bias and dark correction and supplies geometry-qualified detector data
before wavelength mapping and spectral correction. Invalid-value
representation, interpolation, replacement method, and edge behavior remain
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
