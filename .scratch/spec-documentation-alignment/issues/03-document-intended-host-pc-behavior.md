# Document Intended Host PC Behavior

Type: task
Status: resolved
Blocked by: 01

## Question

What should the host PC software do, and how should the intended runtime, configuration, processing, display, export, and validation behavior be captured in the Sphinx documentation before code comparison begins?

## Done When

- Intended host-PC behavior is documented in the host-PC documentation area under `docs/source/subsystems/host_pc/`.
- The intended data-flow from device input through processed spectrum output is described in a way that can be checked against `PythonGUI/`.
- User-visible behaviors, configuration expectations, and calibration responsibilities are explicit.

## Comments

## Answer

- The Host PC documentation authority now lives under `docs/source/subsystems/host_pc/` with one top-level `Host PC System Overview` page and three authoritative systems:
  - `primary_data_pipeline`
  - `device_control_and_acquisition_coordination`
  - `operator_application`
- The Host PC branch was restructured so the root Sphinx navigation points to a single Host PC overview path instead of duplicating older runtime, configuration, display/export, and validation branches.
- The primary data pipeline now uses the agreed first-pass stage structure:
  - `ingress_and_adc_reconstruction`
  - `bias_dark_correction`
  - `bad_pixel_masking`
  - `wavelength_mapping`
  - `spectral_corrections`
  - `processed_spectrum_output_and_retention`
- The acquisition-control system now uses the agreed first-pass behavior pages:
  - `connection_management`
  - `acquisition_session_control`
  - `integration_time_control`
  - `command_status_handling`
- The operator application now uses the agreed first-pass workflow pages:
  - `session_control`
  - `visualization`
  - `calibration_and_user_settings`
  - `export_initiation_and_session_retention`
- Low-level host-to-microcontroller interaction details were intentionally kept out of the Host PC subsystem pages and routed to the Integration interface surface instead.
- Existing substantive Host PC text was preserved where it was strongest, especially the prior pipeline overview concepts, the receive-path specification material, and the live visualization/export summary.
- Obsolete Host PC branches were removed from the docs tree after the new structure was in place.
- Verification: `python -m sphinx -b html -c docs docs/source docs/build/html`
