Communications Inspector
========================

.. _uuid-b61e6b65-10f8-40fb-97e5-75f7f5aa2b44:

UUID: :ref:`B61E6B65-10F8-40FB-97E5-75F7F5AA2B44 <uuid-b61e6b65-10f8-40fb-97e5-75f7f5aa2b44>`

The Communications Inspector is an optional support tool for observing the
host-device USB CDC boundary independently of the normal operator application.
It may produce verification evidence, but it is not an alternate requirements
authority, a measurement-processing path, or the normal user interface.

**Inputs:** an approved interface contract, an available host-device
connection, an observation duration, and the requirement/configuration
identifiers under test.

**Required observations:**

* whether accepted frames are complete and preserve 3648 effective samples;
* frame identity and observed continuity;
* status information exposed by the approved contract;
* accepted-frame count and observation duration; and
* observed control outcomes/status when a separately approved test exercises
  start, stop, or integration-time requests.

**Calculation:**

.. math::

   R_{accepted} = \frac{N_{accepted}}{T_{observation}}

where ``N_accepted`` is the number of complete frames accepted under the
approved contract and ``T_observation`` is the observation duration in seconds.
The subsystem minimum of at least 10 complete frames per second at minimum
integration time is distinct from the above-100-frames-per-second system design
target and from any host display-update rate.

**Evidence outputs:** record the requirement ID, hardware/configuration
revision, observation start and duration, accepted-frame count, rejected or
incomplete observations, identity/status observations, calculated accepted
frame rate, and evidence-artifact reference.  Detailed disposition and
retention rules belong to :doc:`Test and Verification <../../../test_and_verification/index>`.

**Operational constraints:** Whether the operator application and
Communications Inspector may access the port concurrently, which component owns
the connection, and how access is arbitrated are ``Not In Docs``.  Inspector
command-line options, log format, concurrency behavior, recovery, timeout,
naming, and retention details are also ``Not In Docs`` and shall not be inferred
from a tool implementation.

**Traceability:** :ref:`7205FDB2 <integration-traceability-7205fdb2>`;
alignment state ``Not Started``.
