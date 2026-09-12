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

**Objective 1:** **Spectrum display.** Visualization shall plot processed
intensity against wavelength and shall preserve the index correspondence
between the two arrays.

**Rationale:** Index correspondence prevents an intensity value from being
displayed at the wrong wavelength.

**Objective 2:** **History and status.** Visualization shall append each
received spectrum to rolling history when enabled and shall present connection,
device, and session indicators separately from the plot.

**Rationale:** Separate status indicators allow the operator to evaluate
measurement context without altering the spectrum presentation.

**Objective 3:** **Presentation faults.** Visualization shall identify missing,
stale, unavailable, and non-finite records and shall display processed values
without performing another measurement correction.

**Rationale:** Explicit fault presentation prevents invalid data from appearing
current and preserves processing ownership in the Primary Data Pipeline.

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
