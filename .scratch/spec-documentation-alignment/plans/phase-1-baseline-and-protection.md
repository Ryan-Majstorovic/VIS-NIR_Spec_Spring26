# Section 1 Baseline and Protection Inventory

Date: 2026-08-20
Scope: `docs/source/subsystems/embedded/` and `docs/source/subsystems/optics/`
Status: complete

## Purpose

This inventory freezes the accepted middle-layer cleanup before the Embedded and
Optics trees are migrated toward the Host PC documentation structure. It records
the recoverable diff, current paths, UUID locations, navigation graph, and URL
policy without changing the live documentation hierarchy.

## Recovery checkpoint

The exact approved cleanup diff is stored at:

`.scratch/spec-documentation-alignment/plans/phase-1-optics-embedded-cleanup.patch`

```text
BRANCH=Ryan
HEAD=34c3b754f020fb7d3d5bccfa4a38882fc1587e5d
PATCH_SHA256=36B5804D497738CBBFEF66FDD13613BA37DFAA49B0070F9399FAAF799695C005
PATCH_BYTES=22599
```

Recovery recommendation:

1. Stop later migration work.
2. Review the current worktree before applying anything.
3. Restore or reproduce the checkpoint in a clean worktree with
   `git apply phase-1-optics-embedded-cleanup.patch`.
4. Run the strict Sphinx build before continuing.

The patch is a recovery artifact, not an instruction to apply it over the
current worktree.

## Current cleanup diff

```text
warning: in the working copy of 'docs/source/subsystems/embedded/acquisition/Acquisition.rst', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'docs/source/subsystems/embedded/calibrations/Calibrations.rst', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'docs/source/subsystems/embedded/calibrations/frame_geometry/Frame Geometry Calibration.rst', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'docs/source/subsystems/embedded/calibrations/timing_reference/Timing Reference Calibration.rst', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'docs/source/subsystems/embedded/controller/Controller.rst', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'docs/source/subsystems/embedded/driver_board/Driver Board.rst', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'docs/source/subsystems/embedded/timers/Timers.rst', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'docs/source/subsystems/embedded/usb_cdc/USB CDC.rst', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'docs/source/subsystems/embedded/validation/Validation.rst', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'docs/source/subsystems/optics/alignment_enclosure/Alignment And Enclosure.rst', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'docs/source/subsystems/optics/filtering/Filtering.rst', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'docs/source/subsystems/optics/optical_path/Optical Path.rst', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'docs/source/subsystems/optics/performance_characterization/Performance Characterization.rst', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'docs/source/subsystems/optics/tradeoffs/Tradeoffs.rst', LF will be replaced by CRLF the next time Git touches it
M	docs/source/subsystems/embedded/acquisition/Acquisition.rst
D	docs/source/subsystems/embedded/acquisition/adc_dma/ADC DMA Secondary System.rst
M	docs/source/subsystems/embedded/calibrations/Calibrations.rst
M	docs/source/subsystems/embedded/calibrations/frame_geometry/Frame Geometry Calibration.rst
M	docs/source/subsystems/embedded/calibrations/timing_reference/Timing Reference Calibration.rst
M	docs/source/subsystems/embedded/controller/Controller.rst
D	docs/source/subsystems/embedded/controller/system_controller/STM32F411 System Controller.rst
M	docs/source/subsystems/embedded/driver_board/Driver Board.rst
D	docs/source/subsystems/embedded/driver_board/ccd_interface/CCD Interface Secondary System.rst
M	docs/source/subsystems/embedded/timers/Timers.rst
D	docs/source/subsystems/embedded/timers/adc_trigger_tim2/TIM2 ADC Trigger.rst
D	docs/source/subsystems/embedded/timers/icg_frame_tim4/TIM4 ICG Frame Timing.rst
D	docs/source/subsystems/embedded/timers/master_clock_tim1/TIM1 Master Clock.rst
D	docs/source/subsystems/embedded/timers/reserved_tim5/TIM5 Reserved Timer.rst
D	docs/source/subsystems/embedded/timers/shift_gate_tim3/TIM3 Shift Gate.rst
M	docs/source/subsystems/embedded/usb_cdc/USB CDC.rst
D	docs/source/subsystems/embedded/usb_cdc/binary_frame_stream/Binary Frame Stream Secondary System.rst
M	docs/source/subsystems/embedded/validation/Validation.rst
D	docs/source/subsystems/embedded/validation/firmware_checks/Firmware Checks Secondary System.rst
M	docs/source/subsystems/optics/alignment_enclosure/Alignment And Enclosure.rst
D	docs/source/subsystems/optics/alignment_enclosure/breadboard_to_enclosure/Breadboard-To-Enclosure Secondary System.rst
M	docs/source/subsystems/optics/filtering/Filtering.rst
D	docs/source/subsystems/optics/filtering/second_order_control/Second-Order Control Secondary System.rst
M	docs/source/subsystems/optics/optical_path/Optical Path.rst
D	docs/source/subsystems/optics/optical_path/czerny_turner/Czerny-Turner Secondary System.rst
M	docs/source/subsystems/optics/performance_characterization/Performance Characterization.rst
D	docs/source/subsystems/optics/performance_characterization/test_suite/Optics Test Suite Secondary System.rst
D	docs/source/subsystems/optics/performance_characterization/wavelength_and_resolution/Wavelength And Resolution Secondary System.rst
M	docs/source/subsystems/optics/tradeoffs/Tradeoffs.rst
D	docs/source/subsystems/optics/tradeoffs/grating_selection/Grating Selection Secondary System.rst
```

Expected baseline totals:

- 14 modified category or retained landing pages.
- 16 deleted single-child wrapper pages.
- No Host PC source files included in the checkpoint.

## Current RST path inventory

```text
EMBEDDED
docs/source/subsystems/embedded\acquisition\Acquisition.rst
docs/source/subsystems/embedded\acquisition\adc_dma\ADC And DMA Capture.rst
docs/source/subsystems/embedded\calibrations\Calibrations.rst
docs/source/subsystems/embedded\calibrations\frame_geometry\Frame Geometry Calibration.rst
docs/source/subsystems/embedded\calibrations\frame_geometry\Frame Geometry Inputs.rst
docs/source/subsystems/embedded\calibrations\frame_geometry\Frame Geometry Outputs.rst
docs/source/subsystems/embedded\calibrations\frame_geometry\Frame Geometry Procedure.rst
docs/source/subsystems/embedded\calibrations\frame_geometry\Frame Geometry State Machine.rst
docs/source/subsystems/embedded\calibrations\timing_reference\Timing Reference Calibration.rst
docs/source/subsystems/embedded\calibrations\timing_reference\Timing Reference Inputs.rst
docs/source/subsystems/embedded\calibrations\timing_reference\Timing Reference Outputs.rst
docs/source/subsystems/embedded\calibrations\timing_reference\Timing Reference Procedure.rst
docs/source/subsystems/embedded\calibrations\timing_reference\Timing Reference State Machine.rst
docs/source/subsystems/embedded\controller\Controller.rst
docs/source/subsystems/embedded\controller\system_controller\Embedded Architecture.rst
docs/source/subsystems/embedded\driver_board\ccd_interface\Driver Board Interface.rst
docs/source/subsystems/embedded\driver_board\Driver Board.rst
docs/source/subsystems/embedded\timers\adc_trigger_tim2\TIM2 ADC Trigger Details.rst
docs/source/subsystems/embedded\timers\CCD Timing.rst
docs/source/subsystems/embedded\timers\icg_frame_tim4\TIM4 ICG Timing.rst
docs/source/subsystems/embedded\timers\master_clock_tim1\TIM1 fM Clock.rst
docs/source/subsystems/embedded\timers\reserved_tim5\TIM5 Reserved Timer Details.rst
docs/source/subsystems/embedded\timers\shift_gate_tim3\TIM3 SH Timing.rst
docs/source/subsystems/embedded\timers\Timers.rst
docs/source/subsystems/embedded\usb_cdc\binary_frame_stream\USB CDC Stream.rst
docs/source/subsystems/embedded\usb_cdc\USB CDC.rst
docs/source/subsystems/embedded\validation\firmware_checks\Embedded Validation.rst
docs/source/subsystems/embedded\validation\traceability.rst
docs/source/subsystems/embedded\validation\Validation.rst
OPTICS
docs/source/subsystems/optics\alignment_enclosure\Alignment And Enclosure.rst
docs/source/subsystems/optics\alignment_enclosure\breadboard_to_enclosure\Alignment And Enclosure.rst
docs/source/subsystems/optics\filtering\Filtering.rst
docs/source/subsystems/optics\filtering\second_order_control\Second-Order Diffraction.rst
docs/source/subsystems/optics\optical_path\czerny_turner\Optics Architecture.rst
docs/source/subsystems/optics\optical_path\Optical Path.rst
docs/source/subsystems/optics\performance_characterization\Performance Characterization.rst
docs/source/subsystems/optics\performance_characterization\test_suite\Optics Characterization Tests.rst
docs/source/subsystems/optics\performance_characterization\wavelength_and_resolution\Wavelength Coverage And Resolution.rst
docs/source/subsystems/optics\tradeoffs\grating_selection\Optical Component Tradeoffs.rst
docs/source/subsystems/optics\tradeoffs\Tradeoffs.rst
```

Current totals:

- Embedded: 29 RST files.
- Optics: 11 RST files.
- Neither section currently contains an `index.rst`.

## UUID inventory

```text
docs/source/subsystems/embedded\acquisition\adc_dma\ADC And DMA Capture.rst:4:UUID: ``8F4E69AC-05DC-4E3C-8CF5-4E84DA7BBE2A``
docs/source/subsystems/embedded\calibrations\frame_geometry\Frame Geometry Inputs.rst:4:UUID: ``6142E944-4803-4D48-BA2F-33DAE9A3184D``
docs/source/subsystems/embedded\calibrations\frame_geometry\Frame Geometry Outputs.rst:4:UUID: ``D5A49E55-B850-43A5-8B51-78A4DFB63FFE``
docs/source/subsystems/embedded\calibrations\frame_geometry\Frame Geometry Procedure.rst:4:UUID: ``53FEB0B0-95AB-405B-827D-B255FE50D192``
docs/source/subsystems/embedded\calibrations\frame_geometry\Frame Geometry State Machine.rst:4:UUID: ``D2E3F405-6172-489A-BCDE-1234567890F1``
docs/source/subsystems/embedded\calibrations\timing_reference\Timing Reference Inputs.rst:4:UUID: ``78266345-6060-41B1-995E-76D7A96CF314``
docs/source/subsystems/embedded\calibrations\timing_reference\Timing Reference Outputs.rst:4:UUID: ``E935EEA3-4CC8-4BD6-B128-2B72C10D9352``
docs/source/subsystems/embedded\calibrations\timing_reference\Timing Reference Procedure.rst:4:UUID: ``91D8792D-AE7E-430D-ABCD-1999DB7D404F``
docs/source/subsystems/embedded\calibrations\timing_reference\Timing Reference State Machine.rst:4:UUID: ``C1D2E3F4-5061-4789-ABCD-0123456789EF``
docs/source/subsystems/embedded\controller\system_controller\Embedded Architecture.rst:4:UUID: ``9F6C2C68-53B8-4B6B-BB9F-42068A583BF3``
docs/source/subsystems/embedded\driver_board\ccd_interface\Driver Board Interface.rst:4:UUID: ``7AB68D84-F976-4944-A5BB-3633E38F8A3B``
docs/source/subsystems/embedded\timers\adc_trigger_tim2\TIM2 ADC Trigger Details.rst:4:UUID: ``3C47779C-63B3-4C7D-A690-C41F7C042E70``
docs/source/subsystems/embedded\timers\CCD Timing.rst:4:UUID: ``0B79E0A3-6CEE-4957-A820-C4B119B6FF9E``
docs/source/subsystems/embedded\timers\icg_frame_tim4\TIM4 ICG Timing.rst:4:UUID: ``51D66927-7652-4B5F-A591-22830C5F705F``
docs/source/subsystems/embedded\timers\master_clock_tim1\TIM1 fM Clock.rst:4:UUID: ``BB2BD987-A43C-4B7E-8A7B-5389C5155CF2``
docs/source/subsystems/embedded\timers\reserved_tim5\TIM5 Reserved Timer Details.rst:4:UUID: ``F58A525D-198A-4BB1-8F35-BA7BEE59E776``
docs/source/subsystems/embedded\timers\shift_gate_tim3\TIM3 SH Timing.rst:4:UUID: ``33D75617-7935-43B7-B7CC-303211704FEC``
docs/source/subsystems/embedded\usb_cdc\binary_frame_stream\USB CDC Stream.rst:4:UUID: ``A89AE97C-5C91-4E48-B052-A1DDC26781C0``
docs/source/subsystems/embedded\validation\firmware_checks\Embedded Validation.rst:4:UUID: ``542C4175-30A6-4498-8BE9-2DDDE4A65002``
docs/source/subsystems/optics\alignment_enclosure\breadboard_to_enclosure\Alignment And Enclosure.rst:4:UUID: ``C84AA8D3-91D6-42CF-A6E7-28E7EDCF87AE``
docs/source/subsystems/optics\filtering\second_order_control\Second-Order Diffraction.rst:4:UUID: ``406D13B5-12F2-4144-9F1E-C36E6D515FA0``
docs/source/subsystems/optics\optical_path\czerny_turner\Optics Architecture.rst:4:UUID: ``0F0D41FE-6F7B-4A3E-A8DD-3C1F7DCE2481``
docs/source/subsystems/optics\performance_characterization\test_suite\Optics Characterization Tests.rst:4:UUID: ``F66D66DC-23E9-42EC-A635-1D8BE9832C16``
docs/source/subsystems/optics\performance_characterization\wavelength_and_resolution\Wavelength Coverage And Resolution.rst:4:UUID: ``8D8313D8-A65B-4C40-B0A4-5F88B8E8E662``
docs/source/subsystems/optics\tradeoffs\grating_selection\Optical Component Tradeoffs.rst:4:UUID: ``D5CFD390-4E80-489E-87B7-CE1FC5E2E11D``
```

Baseline UUID policy finding:

- Embedded contains 19 visible bare UUIDs.
- Optics contains 6 visible bare UUIDs.
- Neither section currently uses Host PC-style native `uuid-...` labels.
- Later migration must preserve UUID values while adding normalized labels.

## Current toctree graph

```text
docs/source/subsystems/optics\tradeoffs\Tradeoffs.rst -> grating_selection/Optical Component Tradeoffs
docs/source/subsystems/embedded\validation\Validation.rst -> firmware_checks/Embedded Validation
docs/source/subsystems/embedded\validation\Validation.rst -> traceability
docs/source/subsystems/embedded\usb_cdc\USB CDC.rst -> binary_frame_stream/USB CDC Stream
docs/source/subsystems/optics\performance_characterization\Performance Characterization.rst -> wavelength_and_resolution/Wavelength Coverage And Resolution
docs/source/subsystems/optics\performance_characterization\Performance Characterization.rst -> test_suite/Optics Characterization Tests
docs/source/subsystems/embedded\timers\Timers.rst -> CCD Timing
docs/source/subsystems/embedded\timers\Timers.rst -> master_clock_tim1/TIM1 fM Clock
docs/source/subsystems/embedded\timers\Timers.rst -> adc_trigger_tim2/TIM2 ADC Trigger Details
docs/source/subsystems/embedded\timers\Timers.rst -> shift_gate_tim3/TIM3 SH Timing
docs/source/subsystems/embedded\timers\Timers.rst -> icg_frame_tim4/TIM4 ICG Timing
docs/source/subsystems/embedded\timers\Timers.rst -> reserved_tim5/TIM5 Reserved Timer Details
docs/source/subsystems/optics\optical_path\Optical Path.rst -> czerny_turner/Optics Architecture
docs/source/subsystems/embedded\driver_board\Driver Board.rst -> ccd_interface/Driver Board Interface
docs/source/subsystems/optics\filtering\Filtering.rst -> second_order_control/Second-Order Diffraction
docs/source/subsystems/embedded\calibrations\Calibrations.rst -> timing_reference/Timing Reference Calibration
docs/source/subsystems/embedded\calibrations\Calibrations.rst -> frame_geometry/Frame Geometry Calibration
docs/source/subsystems/embedded\controller\Controller.rst -> system_controller/Embedded Architecture
docs/source/subsystems/embedded\acquisition\Acquisition.rst -> adc_dma/ADC And DMA Capture
docs/source/subsystems/optics\alignment_enclosure\Alignment And Enclosure.rst -> breadboard_to_enclosure/Alignment And Enclosure
docs/source/subsystems/embedded\calibrations\timing_reference\Timing Reference Calibration.rst -> Timing Reference Inputs
docs/source/subsystems/embedded\calibrations\timing_reference\Timing Reference Calibration.rst -> Timing Reference Outputs
docs/source/subsystems/embedded\calibrations\timing_reference\Timing Reference Calibration.rst -> Timing Reference Procedure
docs/source/subsystems/embedded\calibrations\timing_reference\Timing Reference Calibration.rst -> Timing Reference State Machine
docs/source/subsystems/embedded\calibrations\frame_geometry\Frame Geometry Calibration.rst -> Frame Geometry Inputs
docs/source/subsystems/embedded\calibrations\frame_geometry\Frame Geometry Calibration.rst -> Frame Geometry Outputs
docs/source/subsystems/embedded\calibrations\frame_geometry\Frame Geometry Calibration.rst -> Frame Geometry Procedure
docs/source/subsystems/embedded\calibrations\frame_geometry\Frame Geometry Calibration.rst -> Frame Geometry State Machine
```

## Inbound subsystem references

```text
docs/source\index.rst:23:   subsystems/optics/optical_path/Optical Path
docs/source\index.rst:24:   subsystems/optics/tradeoffs/Tradeoffs
docs/source\index.rst:25:   subsystems/optics/filtering/Filtering
docs/source\index.rst:26:   subsystems/optics/alignment_enclosure/Alignment And Enclosure
docs/source\index.rst:27:   subsystems/optics/performance_characterization/Performance Characterization
docs/source\index.rst:33:   subsystems/embedded/controller/Controller
docs/source\index.rst:34:   subsystems/embedded/calibrations/Calibrations
docs/source\index.rst:35:   subsystems/embedded/timers/Timers
docs/source\index.rst:36:   subsystems/embedded/acquisition/Acquisition
docs/source\index.rst:37:   subsystems/embedded/usb_cdc/USB CDC
docs/source\index.rst:38:   subsystems/embedded/driver_board/Driver Board
docs/source\index.rst:39:   subsystems/embedded/validation/Validation
```

The root documentation index is currently the only full-path navigation owner
for the Embedded and Optics category pages. Relative child toctrees are recorded
above.

## URL compatibility policy

Use a preserve-first policy during migration:

1. Create and verify each new `overview.rst`, category `index.rst`, and
   behavior `index.rst` path before retiring its old title-cased path.
2. Keep old paths out of the new primary toctree so the sidebar has one
   authoritative hierarchy.
3. Do not delete an old path until its content, UUIDs, and inbound references
   are confirmed migrated.
4. If stable historical HTML URLs are required, add explicit compatibility
   handling in a separately approved operation; do not keep duplicate toctree
   routes.
5. Treat every final old-path deletion as destructive and require an approved
   file-operation manifest.

## Source boundary

This baseline is structural. No intended behavior was derived from firmware,
Python, tests, historical reports, PDFs, or Visio diagrams. Later content
population remains requirements-first and uses `docs/source/` as the
authoritative specification.

## Section 1 completion criteria

- [x] Exact current cleanup diff captured.
- [x] Git base and SHA-256 checksum recorded.
- [x] Current Embedded and Optics paths inventoried.
- [x] UUID locations inventoried.
- [x] Current toctree relationships inventoried.
- [x] Inbound full-path references inventoried.
- [x] Preserve-first URL policy recorded.
- [x] Strict Sphinx baseline build completed with warnings treated as errors.
- [x] `git diff --check` completed after creating the artifacts.

## Verification results

- Sphinx command: `python -m sphinx -E -a -W --keep-going -b html -c docs docs/source docs/build/html-structure-parity-baseline`
- Sphinx result: passed.
- Checkpoint reverse-apply check: passed.
- `git diff --check`: passed.
- Rendered baseline: `docs/build/html-structure-parity-baseline/index.html`.
