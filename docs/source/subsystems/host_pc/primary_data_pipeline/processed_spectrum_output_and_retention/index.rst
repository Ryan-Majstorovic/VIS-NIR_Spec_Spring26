Processed Spectrum Output And Retention
=======================================

.. note::

   Insert the user-provided I/O diagram here after the Visio source and image
   are available.

.. _uuid-cd57310a-a435-497c-9c33-9cf5cd8da7c3:

System Role
-----------

UUID: :ref:`CD57310A-A435-497C-9C33-9CF5CD8DA7C3 <uuid-cd57310a-a435-497c-9c33-9cf5cd8da7c3>`

**Summary:** The Host PC processed-spectrum-output-and-retention system
assembles aligned raw ADC counts, processed counts, wavelength, volts when
defined, and processed intensity into a session-ready record while preserving
the raw measurement for application use.

.. _uuid-1ed83ec4-f108-42f9-af0b-fa83fb8f431d:

System Objectives
-----------------

UUID: :ref:`1ED83EC4-F108-42F9-AF0B-FA83FB8F431D <uuid-1ed83ec4-f108-42f9-af0b-fa83fb8f431d>`

**Objective 1:** The Host PC processed-spectrum-output-and-retention system
shall associate raw ADC counts, processed counts, wavelength, volts when
defined, and processed intensity with the same source measurement.

   Rationale: Common measurement identity prevents products from different
   acquisitions from being combined into one record.

**Objective 2:** The Host PC processed-spectrum-output-and-retention system
shall preserve raw ADC counts independently of derived values.

   Rationale: Independent raw-data preservation supports recovery and later
   reprocessing without treating a derived value as the source measurement.

**Objective 3:** The Host PC processed-spectrum-output-and-retention system
shall maintain one-to-one correspondence among available product arrays.

   Rationale: Array correspondence prevents wavelength, counts, volts, or
   intensity from being assigned to the wrong detector position.

**Objective 4:** The Host PC processed-spectrum-output-and-retention system
shall mark a record ready only when required products are complete and aligned.

   Rationale: Readiness gating prevents incomplete or mismatched products from
   appearing as a usable spectrum record.

**Objective 5:** The Host PC processed-spectrum-output-and-retention system
shall retain the session-ready record and provide it to visualization,
retention, and export initiation without owning the export user interface.

   Rationale: A defined application handoff keeps the data product available to
   operator workflows without moving export-interface behavior into the
   pipeline.

**Objective 6:** The Host PC processed-spectrum-output-and-retention system
shall report missing products, incompatible identities or lengths, and
retention failures and gate affected outputs.

   Rationale: Failure visibility and gating prevent incomplete or unretained
   records from silently advancing to application use.

.. _uuid-c17f356a-d747-4a3a-985a-98dea2055235:

Documentation Relationship
--------------------------

UUID: :ref:`C17F356A-D747-4A3A-985A-98DEA2055235 <uuid-c17f356a-d747-4a3a-985a-98dea2055235>`

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

.. _uuid-cc12d520-e64a-449d-89b5-895a9d3984a7:

Application Boundary
--------------------

UUID: :ref:`CC12D520-E64A-449D-89B5-895A9D3984A7 <uuid-cc12d520-e64a-449d-89b5-895a9d3984a7>`

**Summary:** The Host PC processed-spectrum-output-and-retention system receives
completed pipeline products and supplies session-ready records to
visualization, retention, and export initiation without owning the export user
interface. Volts conversion, record schema, metadata, retention duration,
memory limits, and incomplete-record policy remain ``Not In Docs``.

.. toctree::
   :maxdepth: 1
   :hidden:

   inputs_and_outputs
   procedure
   diagnostics
   testing
   calculations
   validation
