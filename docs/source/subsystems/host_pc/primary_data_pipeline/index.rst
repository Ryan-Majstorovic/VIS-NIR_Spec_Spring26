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

**Objective 1:** The Host PC primary-data-pipeline system shall accept only
eligible complete measurement content, confirm frame identity, status, and
3648-effective-pixel geometry, and preserve ordered raw ADC counts with their
frame context.

   Rationale: Completeness, compatibility, and ordered preservation prevent
   incomplete, incompatible, or misordered input from advancing.

**Objective 2:** The Host PC primary-data-pipeline system shall apply enabled,
available, and compatible bias and dark terms while preserving raw counts and
correction metadata.

   Rationale: Conditional correction prevents unavailable or incompatible
   calibration data from silently changing the measurement.

**Objective 3:** The Host PC primary-data-pipeline system shall qualify known
unreliable detector positions using a geometry-compatible mask and retain mask
identity and affected positions.

   Rationale: Geometry qualification prevents unreliable positions from
   silently qualifying as valid while preserving mask provenance.

**Objective 4:** The Host PC primary-data-pipeline system shall associate each
effective detector position with wavelength using an approved map and retain
coverage and known-reference residual evidence.

   Rationale: Approved mapping protects wavelength meaning and retained
   residual evidence supports validation traceability.

**Objective 5:** The Host PC primary-data-pipeline system shall apply separately
configured flat-field or PRNU, spectral-response or QE, and normalization
operations only when their required inputs and bases are defined and
compatible.

   Rationale: Prerequisite and compatibility gating prevent distinct or
   undefined corrections from being conflated or applied without required
   inputs.

**Objective 6:** The Host PC primary-data-pipeline system shall preserve raw
counts, align raw counts, processed counts, wavelength, volts when defined, and
processed intensity, and mark the record session-ready only when required
products are complete and aligned.

   Rationale: Source preservation and product alignment keep derived products
   tied to one measurement and retain recovery and reprocessing value.

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
