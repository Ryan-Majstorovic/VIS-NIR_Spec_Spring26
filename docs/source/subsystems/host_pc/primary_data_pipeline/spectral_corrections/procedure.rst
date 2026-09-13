Procedure
=========

.. _uuid-b0fc279f-bb23-469d-83b1-d77c09db16ff:

Ordered Correction Behavior
---------------------------

UUID: :ref:`B0FC279F-BB23-469D-83B1-D77C09DB16FF <uuid-b0fc279f-bb23-469d-83b1-d77c09db16ff>`

1. Receive wavelength-associated, bias/dark-corrected, bad-pixel-qualified data.
2. Select compatible flat-field or PRNU correction data when enabled.
3. Select compatible spectral-response or QE correction data when enabled.
4. Apply an approved normalization only when its basis is defined.
5. Preserve the inputs and record every applied or bypassed correction.

.. _uuid-0284b912-528d-4e5f-96a4-543b287f85a4:

Correction Decisions
--------------------

UUID: :ref:`0284B912-528D-4E5F-96A4-543B287F85A4 <uuid-0284b912-528d-4e5f-96a4-543b287f85a4>`

Factor convention, mathematical form, operation order, normalization basis, and tolerances are Not In Docs. This first-run specification does not prescribe an equation.

.. _uuid-b64aaaab-03ee-4993-a094-2d49c5061c1e:

Processing Conditions
---------------------

UUID: :ref:`B64AAAAB-03EE-4993-A094-2D49C5061C1E <uuid-b64aaaab-03ee-4993-a094-2d49c5061c1e>`

* **configured corrections available**
* **optional correction bypassed**
* **requested correction unavailable or invalid**
