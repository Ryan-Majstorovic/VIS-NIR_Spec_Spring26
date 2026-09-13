Procedure
=========

.. _uuid-c65ad49a-2c6b-45d1-8fe8-821b6fc1a21a:

Verification Lifecycle
----------------------

UUID: :ref:`C65AD49A-2C6B-45D1-8FE8-821B6FC1A21A <uuid-c65ad49a-2c6b-45d1-8fe8-821b6fc1a21a>`

1. Select one local traceability item and its defining requirement.
2. Confirm that the planned method and acceptance criterion are documented.
3. Record the instrument setup, configuration versions, reference identities,
   and environmental conditions.
4. Capture the raw observations required by the method.
5. Calculate only the metrics defined by a calculation block on this section.
6. Compare each metric with the documented criterion.
7. Assign a future result disposition of ``Pass``, ``Fail``, or
   ``Inconclusive``; use ``Inconclusive`` when evidence or criterion
   readiness is insufficient.
8. Archive the evidence package and initiate mismatch or regression review when
   required.

**Rationale:** Separating method readiness, raw evidence, calculation, result
disposition, and review prevents an observation from being promoted directly
into a compliance claim.

.. _trace-66d487dd:
.. _uuid-bd53c5b6-b340-46b1-b46e-7458d173321b:

Disposition And Regression Rules
--------------------------------

UUID: :ref:`BD53C5B6-B340-46B1-B46E-7458D173321B <uuid-bd53c5b6-b340-46b1-b46e-7458d173321b>`

**Local Traceability ID:** :ref:`66D487DD <trace-66d487dd>`

* A missing criterion, uncontrolled setup, incomplete evidence package, or
  unsuitable reference requires an ``Inconclusive`` future disposition.
* A result outside a documented criterion requires a mismatch review; it does
  not authorize an automatic requirement or implementation change.
* Changes to frame geometry, interface contract, acquisition timing,
  calibration order, export schema, optical alignment, or acceptance criteria
  shall trigger review of affected planned regression activities.
* Regression scope, evidence retention, reviewer authority, and release gating
  remain ``Not In Docs``.

.. note::

   No verification state machine is defined. The blank state-machine Visio file
   is retained only to satisfy the common section-file contract.
