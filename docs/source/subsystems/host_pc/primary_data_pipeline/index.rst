Primary Data Pipeline
=====================

.. note::

   Insert the user-provided pipeline overview or I/O diagram here after the
   Visio source and image are available.

.. _uuid-2d3495cb-05f7-4990-9126-110d5070e578:

System Role
-----------

UUID: :ref:`2D3495CB-05F7-4990-9126-110D5070E578 <uuid-2d3495cb-05f7-4990-9126-110d5070e578>`

**Summary:** The Host PC primary-data-pipeline system qualifies complete
measurement frames, preserves ordered detector data, performs the documented
correction and wavelength-mapping stages, and produces an aligned,
session-ready spectrum record.

.. _uuid-ca0b9906-c320-4d0d-a856-bf8f3adfb7fd:

System Objectives
-----------------

UUID: :ref:`CA0B9906-C320-4D0D-A856-BF8F3ADFB7FD <uuid-ca0b9906-c320-4d0d-a856-bf8f3adfb7fd>`

**Objective 1:** **Frame entry.** The Primary Data Pipeline shall admit a frame
only when its identity and status are present and it contains all 3648 effective
detector samples in acquisition order.

**Rationale:** Blocking incomplete or unidentified frames prevents missing or
misordered detector data from entering measurement processing.

**Objective 2:** **Processing sequence.** The Primary Data Pipeline shall
perform bias and dark correction, bad-pixel handling, wavelength mapping, and
configured spectral corrections without overwriting the source raw counts.

**Rationale:** A defined sequence and preserved source values allow every
derived result to be traced back to the detector measurement.

**Objective 3:** **Record output.** The Primary Data Pipeline shall associate
raw counts, processed counts, wavelength, volts when defined, and processed
intensity with the same source frame and shall mark the record session-ready
only when the arrays are complete and aligned.

**Rationale:** Source identity and array alignment prevent values from different
frames or detector positions from being combined.

.. _uuid-82ddd480-efc3-48b7-beb6-e3ed17755f65:

System Relationship
-------------------

UUID: :ref:`82DDD480-EFC3-48B7-BEB6-E3ED17755F65 <uuid-82ddd480-efc3-48b7-beb6-e3ed17755f65>`

.. list-table::
   :header-rows: 1

   * - System
     - Primary Responsibility
   * - :doc:`Ingress And ADC Reconstruction <ingress_and_adc_reconstruction/index>`
     - Complete-frame qualification and ordered raw-ADC preservation.
   * - :doc:`Bias And Dark Correction <bias_dark_correction/index>`
     - Configured baseline and dark correction with raw-data preservation.
   * - :doc:`Bad Pixel Masking <bad_pixel_masking/index>`
     - Geometry-compatible qualification of known unreliable positions.
   * - :doc:`Wavelength Mapping <wavelength_mapping/index>`
     - Effective detector-position association with wavelength.
   * - :doc:`Spectral Corrections <spectral_corrections/index>`
     - Separately configured flat-field, response, and normalization operations.
   * - :doc:`Processed Spectrum Output And Retention <processed_spectrum_output_and_retention/index>`
     - Aligned session-ready spectrum records and application handoff.

.. _uuid-01d4293e-28a0-439f-8dde-949e0cf4d979:

Integration Boundary
--------------------

UUID: :ref:`01D4293E-28A0-439F-8DDE-949E0CF4D979 <uuid-01d4293e-28a0-439f-8dde-949e0cf4d979>`

**Summary:** The Host PC primary-data-pipeline system receives complete
transport candidates from the Integration-owned boundary and supplies aligned
processed records to visualization, retention, and export initiation. The
pipeline consumes rather than redefines the wire contract. Framing, encoding,
field ranges, resynchronization, malformed-input recovery, and transported
geometry beyond the documented 3648 effective detector pixels are
``Not In Docs`` for the Host PC pipeline and remain owned by Integration.

.. toctree::
   :maxdepth: 1
   :hidden:

   ingress_and_adc_reconstruction/index
   bias_dark_correction/index
   bad_pixel_masking/index
   wavelength_mapping/index
   spectral_corrections/index
   processed_spectrum_output_and_retention/index
