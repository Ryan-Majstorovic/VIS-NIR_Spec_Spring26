Ingress And ADC Reconstruction
==============================

.. note::

   Insert the user-provided I/O diagram here after the Visio source and image
   are available.

.. _uuid-7f8ac58c-1708-486c-af4f-2d690f3ce607:

System Role
-----------

UUID: :ref:`7F8AC58C-1708-486C-AF4F-2D690F3CE607 <uuid-7f8ac58c-1708-486c-af4f-2d690f3ce607>`

**Summary:** The Host PC ingress-and-ADC-reconstruction system qualifies
received transport candidates as complete measurement frames and preserves
ordered raw ADC counts with frame identity, status, and the documented 3648
effective detector pixels for downstream processing.

.. _uuid-8a67f948-8087-42d0-a37d-1aa34db6d15b:

System Objectives
-----------------

UUID: :ref:`8A67F948-8087-42D0-A37D-1AA34DB6D15B <uuid-8a67f948-8087-42d0-a37d-1aa34db6d15b>`

**Objective 1:** **Traffic collection.** Ingress and ADC Reconstruction shall
collect measurement traffic only while the acquisition interface is available
and shall keep non-measurement traffic out of the processing pipeline.

**Rationale:** Separating measurement and non-measurement traffic prevents
status text or unsupported content from becoming detector data.

**Objective 2:** **Frame validation.** Ingress and ADC Reconstruction shall
verify frame identity, status, completeness, and the presence of all 3648
effective samples before releasing a frame.

**Rationale:** These checks prevent partial or structurally incorrect frames
from being interpreted as complete measurements.

**Objective 3:** **Output and rejection.** Ingress and ADC Reconstruction shall
preserve accepted raw samples in acquisition order and shall report incomplete
frames, malformed content, unsupported content, and frame-identity gaps.

**Rationale:** Explicit rejection evidence supports recovery without inventing
samples or redefining the Integration-owned wire format.

.. _uuid-703cb7d9-edc2-4560-8a11-4c321fc92d56:

Documentation Relationship
--------------------------

UUID: :ref:`703CB7D9-EDC2-4560-8A11-4C321FC92D56 <uuid-703cb7d9-edc2-4560-8a11-4c321fc92d56>`

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

.. _uuid-24659d9a-0778-4e53-9580-c80921452d60:

Integration Boundary
--------------------

UUID: :ref:`24659D9A-0778-4E53-9580-C80921452D60 <uuid-24659d9a-0778-4e53-9580-c80921452d60>`

**Summary:** The Host PC ingress-and-ADC-reconstruction system receives a
transport candidate from the Integration boundary and determines whether it is
eligible to become a complete measurement frame. Framing, chunking, encoding,
resynchronization, recovery, and total transported geometry beyond the 3648
effective detector pixels are ``Not In Docs`` for this system and remain owned
by Integration.

.. toctree::
   :maxdepth: 1
   :hidden:

   inputs_and_outputs
   procedure
   diagnostics
   testing
   calculations
   validation
