VIS-NIR Spectrometer Technical Documentation
============================================

This documentation describes the current technical design for the VIS-NIR
spectrometer prototype. It is limited to optics, embedded acquisition,
host-PC software, calibration, integration, and characterization. Nontechnical
course-deliverable material is intentionally outside this documentation set.

.. toctree::
   :maxdepth: 1
   :caption: System

   Technical Source Notes
   System Overview
   Requirements And Metrics
   Calibration And Characterization
   Traceability

.. toctree::
   :maxdepth: 1
   :caption: Optics

   subsystems/optics/optical_path/Optical Path
   subsystems/optics/tradeoffs/Tradeoffs
   subsystems/optics/filtering/Filtering
   subsystems/optics/alignment_enclosure/Alignment And Enclosure
   subsystems/optics/performance_characterization/Performance Characterization

.. toctree::
   :maxdepth: 1
   :caption: Embedded

   subsystems/embedded/controller/Controller
   subsystems/embedded/calibrations/Calibrations
   subsystems/embedded/timers/Timers
   subsystems/embedded/acquisition/Acquisition
   subsystems/embedded/usb_cdc/USB CDC
   subsystems/embedded/driver_board/Driver Board
   subsystems/embedded/validation/Validation

.. toctree::
   :maxdepth: 1
   :caption: Host PC

   Host PC System Overview <subsystems/host_pc/overview>
   subsystems/host_pc/primary_data_pipeline/index
   subsystems/host_pc/device_control_and_acquisition_coordination/index
   subsystems/host_pc/operator_application/index

.. toctree::
   :maxdepth: 1
   :caption: Integration

   subsystems/integration/data_flow/Data Flow
   subsystems/integration/interfaces/Interfaces
   subsystems/integration/test_strategy/Test Strategy
