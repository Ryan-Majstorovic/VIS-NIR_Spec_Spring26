# Embedded Documentation Completion Plan

Status: implemented and Terra-approved
Planning model: `gpt-5.6-sol`
Implementation model: `gpt-5.6-luna`
Review model: `gpt-5.6-terra`
Destination: `docs/source/subsystems/embedded/`

## Objective

Complete the Embedded documentation as an intended-behavior specification for
the spectrometer controller, CCD timing, ADC/DMA acquisition, USB transfer
responsibility, driver-board interface, embedded calibration checks, and
subsystem verification. Requirements and existing authoritative documentation
define intent; firmware is reserved for a later comparison pass.

## Source authority

1. `docs/source/Requirements And Metrics.rst`
2. `.scratch/spec-documentation-alignment/issues/02-document-intended-embedded-behavior.md`
3. Technical requirements, metrics, embedded design, and testing sections of
   `General/SDDEC26-06_Team_Spectro_Design_Document.docx`
4. Existing Embedded pages for structure and already-documented intent

Do not inspect or cite `CCD-Driver-Code`, Python implementation, tests, logs,
captures, or measurements while authoring this pass.

## Current-state inventory

- 16 pages contain substantive content but mix intended behavior with
  implementation-specific wording.
- 3 pages are materially incomplete:
  - `calibrations/frame_geometry/Frame Geometry State Machine.rst`
  - `calibrations/timing_reference/Timing Reference State Machine.rst`
  - `timers/shift_gate_tim3/TIM3 SH Timing.rst`
- 19 pages are organizational wrappers whose toctrees should be preserved.

## Requirement-to-document mapping

| Requirement area | Documentation destination |
|---|---|
| STM32F411CEU6 controller responsibilities | `controller/**` |
| fM, ICG, and SH timing generation | `timers/**` |
| Configurable integration time support | Controller architecture, SH/ICG timing, timing-reference calibration |
| Timer-triggered ADC/DMA acquisition of 3648 effective pixels | `acquisition/**` |
| Complete binary measurement-frame transfer with frame IDs and flags | `usb_cdc/**` at the Embedded responsibility boundary |
| Start, stop, and integration-time request application | Controller and USB responsibility pages |
| Driver-board timing routing, CCD output path, power integrity, and analog conditioning expectations | `driver_board/**` |
| Timing-reference and frame-geometry verification | `calibrations/**` |
| Timing, ADC/DMA, USB, control, interface, stress, and regression checks | `validation/**` |

Keep the above-100-fps system design target separate from lower subsystem and
display-rate criteria.

## Planned file operations

### Controller

Modify:

- `controller/Controller.rst`
- `controller/system_controller/STM32F411 System Controller.rst`
- `controller/system_controller/Embedded Architecture.rst`

Describe system responsibility, supported operating responsibilities, host
control boundary, and dependencies without register, pin, or firmware-flow
claims.

### Acquisition

Modify:

- `acquisition/Acquisition.rst`
- `acquisition/adc_dma/ADC DMA Secondary System.rst`
- `acquisition/adc_dma/ADC And DMA Capture.rst`

Specify the requirement to acquire all 3648 effective detector pixels without
dropped effective samples. Keep ADC trigger frequency, sample phase, voltage
range, clipping behavior, DMA layout, and buffer policy open.

### Timers

Modify all pages under `timers/`, including the master-clock, ADC-trigger,
shift-gate, ICG-frame, and reserved-TIM5 branches.

Requirements-backed nominal timing values may be stated where the design
requirements provide them:

- fM near 2 MHz, with the stated fM tolerance kept distinct.
- ICG period target of 8 ms.
- ICG pulse target of 7.388 ms.
- SH target of 10 microseconds.

Do not infer timer register values, pin assignments, timer channel details, or
the formula relating configurable integration time to SH/ICG timing. Retain
TIM5 as reserved and state that no baseline requirement assigns it an active
function.

### USB CDC

Modify:

- `usb_cdc/USB CDC.rst`
- `usb_cdc/binary_frame_stream/Binary Frame Stream Secondary System.rst`
- `usb_cdc/binary_frame_stream/USB CDC Stream.rst`

Define Embedded responsibility for producing complete measurement frames with
frame identity and status information. Defer normative packet layout and
control/status encoding to Integration.

### Driver board

Modify:

- `driver_board/Driver Board.rst`
- `driver_board/ccd_interface/CCD Interface Secondary System.rst`
- `driver_board/ccd_interface/Driver Board Interface.rst`

Capture requirement-level routing, CCD output, power, decoupling, filtering,
continuity, and oscilloscope-verification expectations. Keep rails, pin maps,
logic levels, and component values open.

### Calibration

Modify:

- `calibrations/Calibrations.rst`
- All five pages under `calibrations/timing_reference/`
- All five pages under `calibrations/frame_geometry/`

Limit Embedded calibration to timing-reference and frame-geometry checks. Bias,
dark, wavelength, flat-field, and response correction remain Host PC or
system-verification responsibilities.

### Validation and traceability

Modify:

- `validation/Validation.rst`
- `validation/firmware_checks/Firmware Checks Secondary System.rst`
- `validation/firmware_checks/Embedded Validation.rst`

Create:

- `validation/traceability.rst`

The new local traceability page will contain behavior claim, alignment state,
defining page, future implementation location, and requirements evidence.

## Content reconstruction rules

- Replace implementation-coupled statements with stable requirement wording.
- Remove register values, MCU pin names, parser layouts, and current buffer
  behavior unless independently stated as a requirement.
- Preserve valid titles, toctrees, paths, and standard UUIDs.
- Use visible standard UUID anchors on new traceable technical blocks.
- Use `Not Started` for documented behavior awaiting later firmware review.
- Use `Not In Docs` for unresolved contract details.

## Open requirements

- Total transported samples beyond 3648 effective detector pixels.
- Packet magic, header size, byte order, field widths, flag meanings,
  acknowledgments, and recovery behavior.
- Integration-time units, range, resolution, default, validation, and timing
  relationship.
- ADC trigger frequency, phase, input range, clipping, and buffering.
- Exact timer-to-signal ownership where only current page names imply it.
- Driver-board rails, pins, logic levels, and filter component values.
- ICG and SH tolerances beyond their stated nominal targets.
- Evidence naming, retention, capture duration, and repetition counts.

## Dependencies and risks

- Integration owns the shared wire and command contract.
- Host PC owns command initiation and calibrated host processing.
- Test and Verification owns system acceptance evidence.
- Configurable integration time may conflict with fixed nominal timing; both
  must be documented without inventing the missing relationship.
- Current 3694-sample statements must not be promoted into requirements.

## Implementation order

1. Re-read authority sources and confirm the scoped files are unchanged.
2. Revise controller and subsystem-wrapper language.
3. Populate timing and acquisition behavior.
4. Populate USB and driver-board responsibility pages.
5. Complete timing-reference and frame-geometry pages.
6. Reconstruct validation and add local traceability.
7. Check every factual claim against the requirement mapping.
8. Convert all remaining unsupported details into explicit open requirements.

## Verification

Run after implementation:

```powershell
python -m sphinx -W --keep-going -b html -c docs docs/source docs/build/html
git diff --check
git diff -- docs/source/subsystems/embedded
```

Confirm:

- Every toctree target exists once.
- Standard UUID anchors and local hexadecimal IDs are unique.
- No implementation paths, registers, pins, or parser formats were added as
  requirements.
- Every unresolved behavior is visibly marked.
- No file outside the approved Embedded scope changed.

## Approval checklist

- [ ] Destination and scope approved.
- [ ] File creation and modification list approved.
- [ ] Requirements-backed nominal timing values approved.
- [ ] 3648-effective-pixel wording approved.
- [ ] Open-requirement list approved.
- [ ] Local traceability approach approved.
