Procedure
=========

.. _uuid-459d7162-4d22-4d3f-bf7c-cd36538fd96b:

Command Outcome Flow
--------------------

UUID: :ref:`459D7162-4D22-4D3F-BF7C-CD36538FD96B <uuid-459d7162-4d22-4d3f-bf7c-cd36538fd96b>`

1. Gate the request using connection and acquisition preconditions.
2. Submit an eligible request through the Integration interface.
3. Classify the returned outcome as success, failure, rejection, or unavailable.
4. Expose the outcome and update only the dependent actions allowed by it.

.. _uuid-84aa521e-6499-4fbf-b197-99c8102459e5:

Outcome Conditions
------------------

UUID: :ref:`84AA521E-6499-4FBF-B197-99C8102459E5 <uuid-84aa521e-6499-4fbf-b197-99c8102459e5>`

Success permits the requested dependent action. Failure, rejection, unavailable device, or missing outcome shall not be reported as success. Command vocabulary, timeout, retry, and recovery are Not In Docs.

.. _uuid-104891fc-22c3-4364-b1bf-b8318331d115:

Command States
--------------

UUID: :ref:`104891FC-22C3-4364-B1BF-B8318331D115 <uuid-104891fc-22c3-4364-b1bf-b8318331d115>`

* **Ready for Command**
* **Command Pending**
* **Accepted**
* **Failed, Rejected, or Unavailable**
