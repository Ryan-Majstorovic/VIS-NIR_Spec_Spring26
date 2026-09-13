Inputs and Outputs
==================

.. _uuid-b65ebb2f-81c9-4caa-ae21-a9ded740eaf6:

Verification Inputs
-------------------

UUID: :ref:`B65EBB2F-81C9-4CAA-AE21-A9DED740EAF6 <uuid-b65ebb2f-81c9-4caa-ae21-a9ded740eaf6>`

.. list-table::
   :header-rows: 1

   * - Item
     - Expected Values
     - Structure
     - Purpose
   * - Requirement or intended-behavior claim
     - A documented, uniquely identifiable technical claim
     - Requirement text and local traceability ID
     - Define what the verification activity evaluates.
   * - Acceptance criterion
     - Documented threshold or explicit ``Not In Docs`` state
     - Criterion, units, comparison rule, and source
     - Prevent an undefined threshold from being treated as a result.
   * - Verification method
     - Planned procedure appropriate to the claim
     - Ordered steps, calculation references, and disposition rule
     - Define how evidence will be produced.
   * - Configuration and conditions
     - Instrument configuration and controlled environmental conditions
     - Versioned setup record
     - Make future evidence interpretable and repeatable.
   * - Reference information
     - Known source values and suitable reference-instrument information
     - Reference identity, validity, uncertainty, and conditions
     - Support wavelength, response, and comparison methods.
   * - Calibration information
     - Calibration and user-configuration versions active for the activity
     - Version or immutable identity
     - Connect evidence to the processing context.

.. _uuid-37f711dd-de31-45e6-ae8e-7cb31d076ba5:

Evidence Outputs
----------------

UUID: :ref:`37F711DD-DE31-45E6-AE8E-7CB31D076BA5 <uuid-37f711dd-de31-45e6-ae8e-7cb31d076ba5>`

.. list-table::
   :header-rows: 1

   * - Item
     - Expected Values
     - Structure
     - Purpose
   * - Raw observations
     - Unmodified observations needed to reproduce the analysis
     - Timestamped evidence artifact
     - Preserve the basis for future review.
   * - Derived metrics
     - Values produced only by documented calculations
     - Value, units, calculation ID, and uncertainty
     - Support comparison with the criterion.
   * - Evidence location
     - Stable location or identifier for each artifact
     - Path or repository-managed reference
     - Make the evidence package retrievable.
   * - Planned result disposition
     - ``Pass``, ``Fail``, or ``Inconclusive``
     - Disposition plus criterion and rationale
     - Record the future comparison outcome without changing the requirement.
   * - Review record
     - Reviewer identity, review date, and review disposition
     - Review metadata
     - Distinguish captured evidence from reviewed evidence.

.. note::

   Evidence retention duration, naming convention, storage location, and
   reviewer authority are ``Not In Docs``.
