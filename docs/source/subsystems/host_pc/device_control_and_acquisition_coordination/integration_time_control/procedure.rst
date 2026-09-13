Procedure
=========

.. _uuid-74841d46-f365-4521-b85f-174d85f8dfae:

Integration-Time Request Flow
-----------------------------

UUID: :ref:`74841D46-F365-4521-B85F-174D85F8DFAE <uuid-74841d46-f365-4521-b85f-174d85f8dfae>`

1. Receive the operator-requested integration time.
2. Validate it against approved device constraints when those constraints are documented.
3. Submit the request through the Integration control interface.
4. Classify the outcome as accepted, rejected, or unavailable.
5. Expose the pending or active value and apply an accepted change at the documented subsequent acquisition boundary.

.. _uuid-f9a03188-0c7f-4e39-a1fd-4f50f85101aa:

Outcome Conditions
------------------

UUID: :ref:`F9A03188-0C7F-4E39-A1FD-4F50F85101AA <uuid-f9a03188-0c7f-4e39-a1fd-4f50f85101aa>`

The active value shall remain unchanged after rejection or interface unavailability. Units, range, quantization, default, acknowledgement, and exact application boundary are Not In Docs.

.. _uuid-60656f02-1956-4175-a6ff-85e4d06b7f56:

Request States
--------------

UUID: :ref:`60656F02-1956-4175-A6FF-85E4D06B7F56 <uuid-60656f02-1956-4175-a6ff-85e4d06b7f56>`

* **Received**
* **Validation Pending**
* **Accepted and Pending Application**
* **Rejected or Unavailable**
