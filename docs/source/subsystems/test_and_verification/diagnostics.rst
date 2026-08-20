Diagnostics
===========

.. _uuid-7ffff7ec-0c8c-4c30-a70c-bfd9e821cf4e:

Diagnostics Table
-----------------

UUID: :ref:`7FFFF7EC-0C8C-4C30-A70C-BFD9E821CF4E <uuid-7ffff7ec-0c8c-4c30-a70c-bfd9e821cf4e>`

.. list-table::
   :header-rows: 1

   * - Item
     - Meaning
     - Expected Range Or State
     - Failure Indication
     - User Alert Behavior
     - UUID
   * - Invalid or uncontrolled setup
     - Required setup or environmental control is absent.
     - All method prerequisites documented.
     - Missing, unknown, or uncontrolled prerequisite.
     - Mark the activity inconclusive and identify the prerequisite.
     - :ref:`81C3B891-47CC-432E-9A57-3D4045F8D9FD <uuid-81c3b891-47cc-432e-9a57-3d4045f8d9fd>`
   * - Incomplete evidence
     - Required raw observation or metadata is missing.
     - Complete evidence package.
     - Missing artifact, field, or condition record.
     - Withhold result disposition and list missing evidence.
     - :ref:`32AD228F-188F-454A-948B-D05D06CE8F5A <uuid-32ad228f-188f-454a-948b-d05d06ce8f5a>`
   * - Corrupted or incomplete interface data
     - Interface evidence cannot support the planned check.
     - Complete data conforming to the Integration contract.
     - Structural error, incomplete record, or lost identity.
     - Stop the affected calculation and request interface review.
     - :ref:`1C9B2CDE-675C-42AE-81F7-BFCEEF6D71AD <uuid-1c9b2cde-675c-42ae-81f7-bfceef6d71ad>`
   * - Missing acceptance threshold
     - A method exists without an approved comparison limit.
     - Documented criterion.
     - Criterion state is ``Not In Docs``.
     - Retain observations but classify the activity as inconclusive.
     - :ref:`C984A448-1F43-45CC-BF6F-FC1BA8907B13 <uuid-c984a448-1f43-45cc-bf6f-fc1ba8907b13>`
   * - Requirement result outside criterion
     - A future metric does not meet its documented criterion.
     - Result within criterion.
     - Comparison is outside the allowed rule.
     - Record ``Fail`` and initiate mismatch review.
     - :ref:`79CAF0DB-8B78-48E0-9DE7-E1A4021639BC <uuid-79caf0db-8b78-48e0-9de7-e1a4021639bc>`
   * - Unsuitable reference
     - Reference source or instrument cannot support the method.
     - Valid reference with applicable range and uncertainty.
     - Expired, out-of-range, damaged, or undocumented reference.
     - Mark the activity inconclusive and replace or qualify the reference.
     - :ref:`39237E9E-0EE2-40ED-91F2-E04316661DF0 <uuid-39237e9e-0ee2-40ed-91f2-e04316661df0>`
   * - Calibration or configuration mismatch
     - Evidence and processing context do not use compatible versions.
     - Recorded compatible identities.
     - Missing or conflicting version information.
     - Withhold comparison and identify the mismatch.
     - :ref:`C86F2EDD-686C-4C85-8AC5-6AD1FCD5ABD4 <uuid-c86f2edd-686c-4c85-8ac5-6ad1fcd5abd4>`
   * - Procedure deviation
     - The documented method was not followed.
     - No unexplained deviation.
     - Omitted, reordered, or substituted step.
     - Record the deviation and require reviewer disposition.
     - :ref:`38E9CB92-9022-484A-9F86-3C5C1ACE98D6 <uuid-38e9cb92-9022-484a-9f86-3c5c1ace98d6>`

.. _uuid-81c3b891-47cc-432e-9a57-3d4045f8d9fd:

Diagnostic D0 - Invalid Or Uncontrolled Setup
---------------------------------------------

UUID: :ref:`81C3B891-47CC-432E-9A57-3D4045F8D9FD <uuid-81c3b891-47cc-432e-9a57-3d4045f8d9fd>`

**Required Response:** Identify the uncontrolled prerequisite before additional
evidence is treated as comparable.

.. _uuid-32ad228f-188f-454a-948b-d05d06ce8f5a:

Diagnostic D1 - Incomplete Evidence
-----------------------------------

UUID: :ref:`32AD228F-188F-454A-948B-D05D06CE8F5A <uuid-32ad228f-188f-454a-948b-d05d06ce8f5a>`

**Required Response:** List every missing artifact or metadata field.

.. _uuid-1c9b2cde-675c-42ae-81f7-bfceef6d71ad:

Diagnostic D2 - Interface Evidence Error
----------------------------------------

UUID: :ref:`1C9B2CDE-675C-42AE-81F7-BFCEEF6D71AD <uuid-1c9b2cde-675c-42ae-81f7-bfceef6d71ad>`

**Required Response:** Defer packet-level interpretation to the Integration
contract and preserve the observed structural condition.

.. _uuid-c984a448-1f43-45cc-bf6f-fc1ba8907b13:

Diagnostic D3 - Missing Acceptance Threshold
--------------------------------------------

UUID: :ref:`C984A448-1F43-45CC-BF6F-FC1BA8907B13 <uuid-c984a448-1f43-45cc-bf6f-fc1ba8907b13>`

**Required Response:** Mark the criterion ``Not In Docs``; do not infer a
limit from an observation.

.. _uuid-79caf0db-8b78-48e0-9de7-e1a4021639bc:

Diagnostic D4 - Result Outside Criterion
----------------------------------------

UUID: :ref:`79CAF0DB-8B78-48E0-9DE7-E1A4021639BC <uuid-79caf0db-8b78-48e0-9de7-e1a4021639bc>`

**Required Response:** Preserve the evidence and initiate requirement-versus-
implementation mismatch review.

.. _uuid-39237e9e-0ee2-40ed-91f2-e04316661df0:

Diagnostic D5 - Unsuitable Reference
------------------------------------

UUID: :ref:`39237E9E-0EE2-40ED-91F2-E04316661DF0 <uuid-39237e9e-0ee2-40ed-91f2-e04316661df0>`

**Required Response:** Record why the reference is unsuitable and identify the
replacement or qualification needed.

.. _uuid-c86f2edd-686c-4c85-8ac5-6ad1fcd5abd4:

Diagnostic D6 - Calibration Or Configuration Mismatch
-----------------------------------------------------

UUID: :ref:`C86F2EDD-686C-4C85-8AC5-6AD1FCD5ABD4 <uuid-c86f2edd-686c-4c85-8ac5-6ad1fcd5abd4>`

**Required Response:** Restore compatible identities or classify the activity
as inconclusive.

.. _uuid-38e9cb92-9022-484a-9f86-3c5c1ace98d6:

Diagnostic D7 - Procedure Deviation
-----------------------------------

UUID: :ref:`38E9CB92-9022-484A-9F86-3C5C1ACE98D6 <uuid-38e9cb92-9022-484a-9f86-3c5c1ace98d6>`

**Required Response:** Record the deviation, its effect, and the future reviewer
decision.
