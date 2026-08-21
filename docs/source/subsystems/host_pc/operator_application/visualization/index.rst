Visualization
=============

.. note::

   Insert the user-provided I/O diagram here after the Visio source and image
   are available.

.. _uuid-7b78ae61-551f-4fd2-ba0e-79877ffb8163:

System Role
-----------

UUID: :ref:`7B78AE61-551F-4FD2-BA0E-79877FFB8163 <uuid-7b78ae61-551f-4fd2-ba0e-79877ffb8163>`

**Summary:** The Host PC visualization system shall present qualified
wavelength-associated processed spectra, rolling spectral history when
enabled, and connection, device, and session status while identifying
unavailable or stale display data.

.. _uuid-bf942b95-91a2-43a7-bbbc-02d3a26ef151:

System Objectives
-----------------

UUID: :ref:`BF942B95-91A2-43A7-BBBC-02D3A26EF151 <uuid-bf942b95-91a2-43a7-bbbc-02d3a26ef151>`

**Objective 1:** The Host PC visualization system shall accept only qualified
wavelength-and-intensity records for spectrum presentation.

   Rationale: Input qualification prevents invalid measurement data from being
   presented as a usable spectrum.

**Objective 2:** The Host PC visualization system shall present the current
intensity-versus-wavelength spectrum while preserving wavelength and intensity
correspondence.

   Rationale: Preserved pairing prevents a displayed value from being assigned
   to the wrong wavelength.

**Objective 3:** The Host PC visualization system shall append accepted records
to rolling spectrogram history when that presentation is enabled.

   Rationale: Ordered accepted records provide temporal context without adding
   unqualified data to the history.

**Objective 4:** The Host PC visualization system shall present connection,
device, and session indicators independently of spectrum rendering.

   Rationale: Independent status presentation preserves visibility of the
   operating state when no usable spectrum is available.

**Objective 5:** The Host PC visualization system shall identify no-record,
stale, unavailable, or invalid-value conditions.

   Rationale: Condition visibility prevents unavailable or stale data from
   appearing current.

**Objective 6:** The Host PC visualization system shall consume processed
values without introducing a new measurement calculation.

   Rationale: Calculation ownership remains with the Primary Data Pipeline so
   presentation does not change the measurement value.

.. _uuid-995c0e2c-fb17-4deb-9e91-b8825654f057:

System Relationship
-------------------

UUID: :ref:`995C0E2C-FB17-4DEB-9E91-B8825654F057 <uuid-995c0e2c-fb17-4deb-9e91-b8825654f057>`

.. list-table::
   :header-rows: 1

   * - Documentation
     - Responsibility
   * - :doc:`Inputs and Outputs <inputs_and_outputs>`
     - Qualified measurement-data and device or session-status boundaries.
   * - :doc:`Procedure <procedure>`
     - Display update flow and availability conditions.
   * - :doc:`Diagnostics <diagnostics>`
     - No-record, stale-data, and invalid-value conditions.
   * - :doc:`Testing <testing>`
     - Requirements-based presentation and indicator tests.
   * - :doc:`Calculations <calculations>`
     - Absence of a new measurement calculation and open display requirements.
   * - :doc:`Validation <validation>`
     - Local behavior claim, traceability state, and validation method.

.. _uuid-eeada21e-e48d-4e30-9a78-bf5a8ef98805:

Integration Boundary
--------------------

UUID: :ref:`EEADA21E-E48D-4E30-9A78-BF5A8EF98805 <uuid-eeada21e-e48d-4e30-9a78-bf5a8ef98805>`

**Summary:** The Host PC visualization system consumes wavelength-associated
processed values from the Primary Data Pipeline and device and session status
from adjacent Host PC systems. It owns operator-facing presentation, not
acquisition control, spectral processing, or a fixed screen layout. Axis
scaling, history depth, color mapping, decimation, saturation rendering, and
the display-rate profile remain ``Not In Docs``.

.. toctree::
   :maxdepth: 1
   :hidden:

   inputs_and_outputs
   procedure
   diagnostics
   testing
   calculations
   validation
