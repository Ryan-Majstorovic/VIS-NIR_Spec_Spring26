Operator Application
====================

The Operator Application subsystem provides the graphical user interface, live spectral visualization, interactive calibration tools, and session export facilities for the VIS-NIR spectrometer. It executes in a Kivy desktop environment decoupled from the high-rate hardware ingress thread.

.. _uuid-71d2ed58-e8db-4e12-ba3f-d9ab7883c5e6:

Subsystem Role & Architecture
-----------------------------

UUID: :ref:`71D2ED58-E8DB-4E12-BA3F-D9AB7883C5E6 <uuid-71d2ed58-e8db-4e12-ba3f-d9ab7883c5e6>`

The Operator Application translates complex instrument data streams into an accessible laboratory desktop environment:
* **Interactive Visualization:** Real-time line plotting with mouse cursor readouts and rolling 2D waterfall spectrograms.
* **Decoupled Cadence:** Operates at approximately 30 FPS to provide smooth user interaction while background threads process full 125 Hz streaming.
* **Calibration Workflows:** One-click dark/bias capture, live algorithm toggles, and polynomial wavelength fitting.
* **Session Export:** Full-rate HDF5 recording and ZIP export of frame data and calibration history.

.. _uuid-6036bb15-b648-4643-a82f-44bc18209cd1:

Subsystem Sections
------------------

UUID: :ref:`6036BB15-B648-4643-A82F-44BC18209CD1 <uuid-6036bb15-b648-4643-a82f-44bc18209cd1>`

.. list-table::
   :header-rows: 1

   * - Section
     - Core Responsibilities
   * - :doc:`session_control`
     - Recording and export controls, with recent-frame buffers for bias capture and display.
   * - :doc:`visualization`
     - Decoupled 30 FPS line spectrum plotting, 256-bin rolling spectrogram, and configurable dynamic ceiling scaling.
   * - :doc:`calibration_and_user_settings`
     - Dark subtraction toggles, master bias capture, wavelength reference point editing, and JSON configuration storage.
   * - :doc:`export_initiation_and_session_retention`
     - Dense HDF5 recording and post-recording export of measurement CSV and calibration JSON in one ZIP.

.. toctree::
   :maxdepth: 1

   session_control
   visualization
   calibration_and_user_settings
   export_initiation_and_session_retention
