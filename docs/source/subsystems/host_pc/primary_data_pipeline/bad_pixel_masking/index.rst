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

**Objective 1:** **Mask verification.** Bad-Pixel Masking shall compare the
mask's detector identity and detector positions with the active frame geometry
before using the mask.

**Rationale:** Comparing detector identity and positions prevents a mask from
altering pixels in a different detector layout.

**Objective 2:** **Pixel disposition.** Bad-Pixel Masking shall mark or exclude
each detector position identified by the mask and shall not interpolate or
replace values until that behavior is defined.

**Rationale:** A defined disposition exposes unreliable samples without
inventing replacement values.

**Objective 3:** **Output and diagnostics.** Bad-Pixel Masking shall retain the
mask identity and affected positions and shall report missing masks, geometry
mismatches, invalid positions, and undefined replacement behavior.

**Rationale:** Retained mask evidence explains which samples were affected and
why a record was prevented from advancing.

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
