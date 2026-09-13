Bias And Dark Correction
========================

.. note::

   Insert the user-provided I/O diagram here after the Visio source and image
   are available.

.. _uuid-cae75bde-39ec-404b-b6d3-8730182e9e2f:

System Role
-----------

UUID: :ref:`CAE75BDE-39EC-404B-B6D3-8730182E9E2F <uuid-cae75bde-39ec-404b-b6d3-8730182e9e2f>`

**Summary:** The Host PC bias-and-dark-correction system applies enabled,
available, and compatible bias and dark terms to preserved raw ADC counts,
while retaining the raw counts and correction metadata for downstream use.

.. _uuid-0498c724-6d5b-4e8f-8e55-3b0ca76cc9b0:

System Objectives
-----------------

UUID: :ref:`0498C724-6D5B-4E8F-8E55-3B0CA76CC9B0 <uuid-0498c724-6d5b-4e8f-8e55-3b0ca76cc9b0>`

**Objective 1:** **Correction calculation.** Bias and Dark Correction shall
calculate ``C_corr(p) = C_raw(p) - B(p) - D(p)`` using only correction terms
that are enabled and present.

**Rationale:** Applying only present and enabled terms prevents an absent
reference from silently changing the measurement.

**Objective 2:** **Reference use.** Bias and Dark Correction shall derive the
frame-wise dark term from the configured covered-input samples and shall apply
per-pixel offsets only when each offset is associated with a detector position.

**Rationale:** Defined sample sources and detector-position association prevent
baseline terms from being applied to the wrong pixels.

**Objective 3:** **Output and diagnostics.** Bias and Dark Correction shall
preserve raw counts, record each applied or bypassed term, and prevent records
containing missing references or non-finite corrected values from advancing.

**Rationale:** Raw-data preservation and explicit diagnostics make the
correction reproducible and keep invalid results out of later stages.

.. _uuid-72023a0d-3ea2-4c32-b64f-7186bedf58c7:

Documentation Relationship
--------------------------

UUID: :ref:`72023A0D-3EA2-4C32-B64F-7186BEDF58C7 <uuid-72023a0d-3ea2-4c32-b64f-7186bedf58c7>`

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

.. _uuid-36fafdc0-690b-42af-98b7-dc22c31e8965:

Pipeline Boundary
-----------------

UUID: :ref:`36FAFDC0-690B-42AF-98B7-DC22C31E8965 <uuid-36fafdc0-690b-42af-98b7-dc22c31e8965>`

**Summary:** The Host PC bias-and-dark-correction system receives preserved raw
ADC counts after ingress qualification and supplies corrected counts and
correction metadata before bad-pixel and wavelength processing. Estimator,
averaging count, reference selection, clipping, and optional-term ordering are
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
