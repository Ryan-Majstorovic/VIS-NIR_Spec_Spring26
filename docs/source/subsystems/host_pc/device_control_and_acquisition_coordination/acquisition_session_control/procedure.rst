Procedure
=========

.. _uuid-625a4419-1e01-4858-a48a-e22c421be1b1:

Acquisition Flow
----------------

UUID: :ref:`625A4419-1E01-4858-A48A-E22C421BE1B1 <uuid-625a4419-1e01-4858-a48a-e22c421be1b1>`

1. Accept Start only while the connection is Ready.
2. Enter Acquiring after the start outcome is accepted.
3. Route complete frames to processing and retention while acquisition remains active.
4. Accept Stop and prevent new frames from entering the session after the approved stop boundary.
5. Expose whether the resulting session is complete, partial, or interrupted.

.. _uuid-36a46270-284d-4aa3-aa1f-c9bca22a6238:

Transition Conditions
---------------------

UUID: :ref:`36A46270-284D-4AA3-AA1F-C9BCA22A6238 <uuid-36a46270-284d-4aa3-aa1f-c9bca22a6238>`

Start is gated by readiness. Stop/drain, pause, buffering, backpressure, and dropped-frame behavior are Not In Docs. Transport rate, display rate, and the above-100-fps design target remain separate.

.. _uuid-968667da-2c16-439d-b07c-f92e8f66ef41:

Acquisition States
------------------

UUID: :ref:`968667DA-2C16-439D-B07C-F92E8F66EF41 <uuid-968667da-2c16-439d-b07c-f92e8f66ef41>`

* **Stopped**
* **Starting**
* **Acquiring**
* **Stopping or Interrupted**
