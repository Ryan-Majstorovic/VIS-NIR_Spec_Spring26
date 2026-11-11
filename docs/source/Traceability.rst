Traceability
============

UUID: ``2A4E1306-71B5-4D29-82AE-0138479CCBF6``

Traceability IDs link design claims to the files and artifacts that implement
or evidence them. Source code uses ``DOC-UUID`` comments only at major files
or behavior blocks.

.. list-table::
   :header-rows: 1

   * - UUID
     - Area
     - Claim
     - Source / Evidence
   * - ``0F0D41FE-6F7B-4A3E-A8DD-3C1F7DCE2481``
     - Optics
     - The B&W Tek Czerny-Turner bench disperses approximately 400-800 nm
       light onto the TCD1304DG effective pixels.
     - Optics Architecture page; OPT-2 and OPT-4 test records.
   * - ``9F6C2C68-53B8-4B6B-BB9F-42068A583BF3``
     - Embedded
     - STM32F411 firmware captures 3694-sample frames and streams ``CCD1``
       packets over USB CDC.
     - ``CCD-Driver-Code/STM32F411_Basic/Core/Src/main.c`` and firmware notes.
   * - ``2BD0CC64-CA9B-4886-BE5C-970D86E21283``
     - Host PC
     - Python parser validates ``CCD1`` binary frames and produces structured
       frame packets for the app.
     - ``PythonGUI/backend/device/protocol.py``.
   * - ``552FD33D-F11F-41B7-B520-81E940994448``
     - Calibration
     - Host processing applies dark/bias, wavelength, intensity, and response
       corrections before live display and export.
     - ``PythonGUI/backend/processing/spectrum_builder.py`` and calibration
       config models.
   * - ``76A44D70-6073-458A-A7D6-5AC9AF4E7B77``
     - Calibration
     - Host PC captures ``B_p`` from buffered covered frames, estimates
       ``beta_f`` from shielded pixels 16 through 28, preserves raw counts,
       and records applied dark/bias terms in export artifacts.
     - ``PythonGUI/frontend/kivy_app.py``,
       ``PythonGUI/backend/processing/calibration_manager.py``,
       ``PythonGUI/backend/processing/dark_subtraction.py``,
       ``PythonGUI/backend/processing/spectrum_builder.py``,
       ``PythonGUI/backend/storage/export_csv.py``, and
       ``PythonGUI/backend/storage/binary_capture.py``.
   * - ``70686C4A-AEE9-44A6-8B28-D74FD756FCD6``
     - Export
     - CSV export writes raw and derived spectrum columns.
     - ``PythonGUI/backend/storage/export_csv.py``.
   * - ``C6B4929A-5CFB-46E8-A592-FD75E67ED745``
     - Test
     - Standalone COM inspector checks USB CDC frame rate and frame
       integrity (test EMB-2).
     - ``Spectrometer-COM-Inspector/spectrometer_com_inspector.py`` and README.

Source Material
---------------

UUID: ``A0A18ED1-BA3C-41FC-B8E6-A4C5BBD5D251``

This documentation draws on these technical sources:

* The team design document (``SDDEC26-06_Team_Spectro_Design_Document``):
  requirements, standards, calibration, and testing sections.
* The team's reference-spectrometer comparison plan
  (``SDDEC26-06_Spectrometer_Comparison_Plan``).
* The repository ``README.md``, ``CCD-Driver-Code/STM32F411_Basic/readme.txt``
  and firmware source, ``PythonGUI/README.md`` and ``PythonGUI/CODE_TOUR.md``,
  and the ``Spectrometer-COM-Inspector`` README and source.

Optics artifacts such as bench photographs, alignment notes, and filter
measurements reuse the optics UUID above until a separate requirement needs
its own ID.
