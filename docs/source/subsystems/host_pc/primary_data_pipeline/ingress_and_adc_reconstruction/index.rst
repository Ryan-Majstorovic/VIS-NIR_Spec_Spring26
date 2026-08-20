Ingress And ADC Reconstruction
==============================


.. _uuid-7f8ac58c-1708-486c-af4f-2d690f3ce607:

Overview
--------

UUID: :ref:`7F8AC58C-1708-486C-AF4F-2D690F3CE607 <uuid-7f8ac58c-1708-486c-af4f-2d690f3ce607>`

Ingress And ADC Reconstruction is the lowest-level host-side qualification
boundary inside the primary data pipeline. It accepts measurement frames from
the Integration transport boundary, verifies that a frame is complete and
requirements-conforming, observes frame identity and status information, and
preserves ordered raw ADC counts for downstream pipeline use.

This stage covers four core responsibilities:

* qualify complete measurement frames before they enter host processing
* observe frame identity and status without redefining their wire encoding
* preserve raw ADC counts in acquisition order with the associated frame
  context
* confirm that accepted measurement content includes all 3648 effective
  detector pixels for later correction and wavelength-association stages

Wire framing, transport chunking, text/binary coexistence, packet or marker
names, resynchronization, and total transported geometry beyond the 3648
effective detector pixels are ``Not In Docs`` and belong to the Integration
contract. This page defines only the Host PC qualification and raw-ADC
preservation behavior after a complete transport candidate reaches the host
pipeline boundary.

.. note::

   Insert the user-provided I/O diagram here after the Visio source and image are available.

Related Pages
-------------

.. toctree::
   :maxdepth: 1

   inputs_and_outputs
   procedure
   diagnostics
   testing
   calculations
   validation
