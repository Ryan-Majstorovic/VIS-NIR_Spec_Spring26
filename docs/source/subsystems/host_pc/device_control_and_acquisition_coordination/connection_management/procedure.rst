Procedure
=========

.. _uuid-fc9a0c23-2cb7-43af-8638-ac039a7aab41:

Connection Flow
---------------

UUID: :ref:`FC9A0C23-2CB7-43AF-8638-AC039A7AAB41 <uuid-fc9a0c23-2cb7-43af-8638-ac039a7aab41>`

1. Begin in Disconnected with acquisition and command actions gated.
2. On an operator connection request, evaluate device availability and interface readiness.
3. Enter Ready only after the connection is usable for host control.
4. On disconnect or connection loss, gate dependent actions and expose the unavailable state.

.. _uuid-3f2927fa-43a3-4003-882e-b13904cd1d9b:

Allowed Transitions
-------------------

UUID: :ref:`3F2927FA-43A3-4003-882E-B13904CD1D9B <uuid-3f2927fa-43a3-4003-882e-b13904cd1d9b>`

Disconnected to Connecting requires an operator request. Connecting to Ready requires confirmed readiness. Ready to Disconnected or Unavailable follows an operator disconnect or observed loss. Discovery, timeout, retry, and reconnect policy are Not In Docs.

.. _uuid-abc05360-1342-453d-85ac-c02441891fec:

Connection States
-----------------

UUID: :ref:`ABC05360-1342-453D-85AC-C02441891FEC <uuid-abc05360-1342-453d-85ac-c02441891fec>`

* **Disconnected**
* **Connecting**
* **Ready**
* **Unavailable**
