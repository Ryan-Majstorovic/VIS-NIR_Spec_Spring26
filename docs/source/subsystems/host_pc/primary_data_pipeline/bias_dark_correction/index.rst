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

**Objective 1:** The Host PC bias-and-dark-correction system shall receive
preserved raw ADC counts with enabled stored-bias, covered-input dark, and
optional per-pixel terms.

   Rationale: Receiving the raw measurement and applicable references together
   establishes the inputs needed to qualify each requested correction.

**Objective 2:** The Host PC bias-and-dark-correction system shall apply
``C_corr(p) = C_raw(p) - B(p) - D(p)`` only for enabled, available, and
applicable terms.

   Rationale: Applying only applicable terms prevents unavailable or disabled
   correction data from changing the measurement.

**Objective 3:** The Host PC bias-and-dark-correction system shall use approved
covered-input data for the configured frame-wise dark reference without
inventing an estimator.

   Rationale: Restricting the dark reference to approved data protects the
   correction from an undocumented estimation method.

**Objective 4:** The Host PC bias-and-dark-correction system shall apply
optional per-pixel offsets only when they are enabled and compatible.

   Rationale: Compatibility gating prevents offsets from being applied to the
   wrong detector geometry or acquisition context.

**Objective 5:** The Host PC bias-and-dark-correction system shall preserve raw
counts and record every applied or bypassed correction.

   Rationale: Raw-data preservation and correction metadata support recovery
   of the source measurement and reproducibility of the corrected result.

**Objective 6:** The Host PC bias-and-dark-correction system shall identify
missing references, disabled corrections, and non-finite outputs rather than
silently qualifying affected data.

   Rationale: Exposing unavailable or invalid correction states prevents
   affected results from appearing fully qualified.

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
