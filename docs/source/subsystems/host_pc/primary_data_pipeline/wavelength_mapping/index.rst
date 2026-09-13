Wavelength Mapping
==================

.. note::

   Insert the user-provided I/O diagram here after the Visio source and image
   are available.

.. _uuid-ea7814f1-819a-4c2f-a709-6b4c829c8eb5:

System Role
-----------

UUID: :ref:`EA7814F1-819A-4C2F-A709-6B4C829C8EB5 <uuid-ea7814f1-819a-4c2f-a709-6b4c829c8eb5>`

**Summary:** The Host PC wavelength-mapping system associates each ordered
effective detector position and corrected value with wavelength using an
approved map and retains coverage and known-reference residual evidence.

.. _uuid-500b2c55-787b-4ae7-b6b3-6dd20c6360df:

System Objectives
-----------------

UUID: :ref:`500B2C55-787B-4AE7-B6B3-6DD20C6360DF <uuid-500b2c55-787b-4ae7-b6b3-6dd20c6360df>`

**Objective 1:** **Position mapping.** Wavelength Mapping shall use a
pixel-to-wavelength relationship to assign one wavelength to each effective
detector position and corrected detector value.

**Rationale:** One wavelength per detector position preserves the relationship
among position, corrected value, and reported wavelength.

**Objective 2:** **Coverage evidence.** Wavelength Mapping shall compare the
resulting wavelength array with the 400-1000 nm target and retain residuals
calculated from known reference wavelengths.

**Rationale:** Coverage and residual evidence show where the wavelength
assignment is supported by reference measurements.

**Objective 3:** **Output and diagnostics.** Wavelength Mapping shall prevent
the mapped record from advancing when the map is absent and shall report
incomplete coverage and wavelength residuals.

**Rationale:** Blocking an absent map prevents detector positions from being
reported with unsupported wavelength meaning.

.. _uuid-d82fc69a-e22a-43ea-9ce6-50eddaf3af89:

Documentation Relationship
--------------------------

UUID: :ref:`D82FC69A-E22A-43EA-9CE6-50EDDAF3AF89 <uuid-d82fc69a-e22a-43ea-9ce6-50eddaf3af89>`

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

.. _uuid-9fda6adc-41d8-4c77-9992-c819ca32917c:

Pipeline Boundary
-----------------

UUID: :ref:`9FDA6ADC-41D8-4C77-9992-C819CA32917C <uuid-9fda6adc-41d8-4c77-9992-c819ca32917c>`

**Summary:** The Host PC wavelength-mapping system receives ordered,
geometry-qualified corrected values and supplies wavelength-associated data and
validation evidence before spectral correction and record assembly. Function
form, polynomial order, coefficient format, extrapolation, uncertainty, and
residual thresholds remain ``Not In Docs``.

.. toctree::
   :maxdepth: 1
   :hidden:

   inputs_and_outputs
   procedure
   diagnostics
   testing
   calculations
   validation
