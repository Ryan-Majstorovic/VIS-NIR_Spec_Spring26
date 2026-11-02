System Control and Hardware Interface
======================================

The System Control and Hardware Interface subsystem coordinates the microcontroller core execution lifecycle, processes host commands across the USB virtual COM port, enforces instrument state transitions, and interfaces the digital controller directly with the Toshiba TCD1304DG linear CCD sensor and driver board electronics.

.. _uuid-41323849-9a8f-41cf-b6ab-7db1e70ac012:

Subsystem Role & Responsibilities
---------------------------------

UUID: :ref:`41323849-9A8F-41CF-B6AB-7DB1E70AC012 <uuid-41323849-9a8f-41cf-b6ab-7db1e70ac012>`

This subsystem serves as the core orchestration plane for the embedded instrument:

* **Microcontroller Lifecycle:** Configures the STM32F411CEU6 system clock tree (96 MHz SYSCLK from 25 MHz HSE), manages Nested Vectored Interrupt Controller (NVIC) priorities, initializes hardware peripherals, and supervises fault recovery.
* **Host Command Processing:** Ingests ASCII command tokens over USB CDC, validates integration-time constraints, regulates state machine transitions, and formats synchronous response frames.
* **Hardware & Sensor Interfacing:** Routes logic-level master clock and shift-gate signals through the CCD driver board, provides low-noise analog buffering to the ADC input, and isolates sensor power domains.

.. _uuid-56b2a61d-6e60-42b6-b1d2-58feda66f353:

Subsystem Sections
------------------

UUID: :ref:`56B2A61D-6E60-42B6-B1D2-58FEDA66F353 <uuid-56b2a61d-6e60-42b6-b1d2-58feda66f353>`

.. list-table::
   :header-rows: 1

   * - Section
     - Core Engineering Responsibilities
   * - :doc:`microcontroller_and_firmware_architecture`
     - STM32F411 clock distribution, NVIC interrupt priority matrix, peripheral initialization, and execution loop orchestration.
   * - :doc:`command_protocol_and_state_machine`
     - Serial ASCII command parsing, integration parameter validation, operational state machine, and response dispatch.
   * - :doc:`driver_board_and_sensor_interface`
     - TCD1304DG detector pinout, clock buffering, video output amplification, power decoupling, and pre-power verification.

.. toctree::
   :maxdepth: 1

   microcontroller_and_firmware_architecture
   command_protocol_and_state_machine
   driver_board_and_sensor_interface
