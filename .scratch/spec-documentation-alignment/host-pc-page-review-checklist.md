# Host PC Page Review Checklist

Use this checklist to walk through every page in the current Host PC Sphinx structure. Check a page after reviewing it and record observations after `Notes:` on the same line.

## Review prompts

For each page, check:

- Does the page state intended Host PC behavior rather than describe the current code?
- Are normative statements written as `The <named system> shall <X> <under Y> <to Z>`?
- Are rationales functional, specific to the associated item, indented beneath it, and not bolded?
- Is the page at the correct level of detail for its position in the hierarchy?
- Are unsupported details marked `Not In Docs`, planned, or TODO?
- Are subsystem boundaries and ownership clear without duplicating Integration or Embedded requirements?
- Are UUIDs, traceability, evidence expectations, diagrams, and navigation links appropriate?

## Progress

- Total pages: **102**
- Reviewed: **0**
- Remaining: **102**

## Host PC System Overview (1 page)

- [ ] **Host PC System Overview** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/overview.html) · [Source](../../docs/source/subsystems/host_pc/overview.rst) — Notes: First I dont think that the system role needs to be split into summary outcome and rationale I think summary is all that is needed and the rest cna be folded in remember were writing facts about the system not about the documentation
- [ ] The objectives also need to be remastered for the writing facts about the system not about the documentation
- [ ] "Standalone validation tools shall remain supporting evidence rather than the normal operating path." This can go
- [ ] I think the ojbective can be split up more granular Im thinking 6-7 objectives
- [ ] Same integration boundary formatting with the system role section this can be a summary only with link to the integration interfaces as that will be the section where we define every boundary optical to ccd ccd to mcu mcu to host pc
- [ ] The realted pages secction should be folded into the system Relationship and I think that there should only be one section about the sub items I.e. get rid of the downstream or adjacent relationship jus have the primary responcibility and make that a few words I dont need that section's full summary
- [ ] when i say folde rin the related pages i just mean use the reference link for the system name rather than a separate section

## Primary Data Pipeline (43 pages)

- [ ] **Primary Data Pipeline Overview** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/index.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/index.rst) — Notes:

### Ingress and ADC Reconstruction (7 pages)

- [ ] **Ingress and ADC Reconstruction Overview** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/ingress_and_adc_reconstruction/index.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/ingress_and_adc_reconstruction/index.rst) — Notes:
- [ ] **Ingress and ADC Reconstruction — Inputs and Outputs** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/ingress_and_adc_reconstruction/inputs_and_outputs.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/ingress_and_adc_reconstruction/inputs_and_outputs.rst) — Notes:
- [ ] **Ingress and ADC Reconstruction — Procedure** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/ingress_and_adc_reconstruction/procedure.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/ingress_and_adc_reconstruction/procedure.rst) — Notes:
- [ ] **Ingress and ADC Reconstruction — Diagnostics** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/ingress_and_adc_reconstruction/diagnostics.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/ingress_and_adc_reconstruction/diagnostics.rst) — Notes:
- [ ] **Ingress and ADC Reconstruction — Testing** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/ingress_and_adc_reconstruction/testing.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/ingress_and_adc_reconstruction/testing.rst) — Notes:
- [ ] **Ingress and ADC Reconstruction — Calculations** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/ingress_and_adc_reconstruction/calculations.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/ingress_and_adc_reconstruction/calculations.rst) — Notes:
- [ ] **Ingress and ADC Reconstruction — Validation** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/ingress_and_adc_reconstruction/validation.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/ingress_and_adc_reconstruction/validation.rst) — Notes:

### Bias and Dark Correction (7 pages)

- [ ] **Bias and Dark Correction Overview** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/bias_dark_correction/index.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/bias_dark_correction/index.rst) — Notes:
- [ ] **Bias and Dark Correction — Inputs and Outputs** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/bias_dark_correction/inputs_and_outputs.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/bias_dark_correction/inputs_and_outputs.rst) — Notes:
- [ ] **Bias and Dark Correction — Procedure** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/bias_dark_correction/procedure.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/bias_dark_correction/procedure.rst) — Notes:
- [ ] **Bias and Dark Correction — Diagnostics** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/bias_dark_correction/diagnostics.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/bias_dark_correction/diagnostics.rst) — Notes:
- [ ] **Bias and Dark Correction — Testing** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/bias_dark_correction/testing.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/bias_dark_correction/testing.rst) — Notes:
- [ ] **Bias and Dark Correction — Calculations** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/bias_dark_correction/calculations.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/bias_dark_correction/calculations.rst) — Notes:
- [ ] **Bias and Dark Correction — Validation** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/bias_dark_correction/validation.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/bias_dark_correction/validation.rst) — Notes:

### Bad Pixel Masking (7 pages)

- [ ] **Bad Pixel Masking Overview** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/bad_pixel_masking/index.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/bad_pixel_masking/index.rst) — Notes:
- [ ] **Bad Pixel Masking — Inputs and Outputs** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/bad_pixel_masking/inputs_and_outputs.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/bad_pixel_masking/inputs_and_outputs.rst) — Notes:
- [ ] **Bad Pixel Masking — Procedure** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/bad_pixel_masking/procedure.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/bad_pixel_masking/procedure.rst) — Notes:
- [ ] **Bad Pixel Masking — Diagnostics** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/bad_pixel_masking/diagnostics.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/bad_pixel_masking/diagnostics.rst) — Notes:
- [ ] **Bad Pixel Masking — Testing** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/bad_pixel_masking/testing.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/bad_pixel_masking/testing.rst) — Notes:
- [ ] **Bad Pixel Masking — Calculations** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/bad_pixel_masking/calculations.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/bad_pixel_masking/calculations.rst) — Notes:
- [ ] **Bad Pixel Masking — Validation** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/bad_pixel_masking/validation.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/bad_pixel_masking/validation.rst) — Notes:

### Wavelength Mapping (7 pages)

- [ ] **Wavelength Mapping Overview** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/wavelength_mapping/index.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/wavelength_mapping/index.rst) — Notes:
- [ ] **Wavelength Mapping — Inputs and Outputs** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/wavelength_mapping/inputs_and_outputs.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/wavelength_mapping/inputs_and_outputs.rst) — Notes:
- [ ] **Wavelength Mapping — Procedure** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/wavelength_mapping/procedure.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/wavelength_mapping/procedure.rst) — Notes:
- [ ] **Wavelength Mapping — Diagnostics** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/wavelength_mapping/diagnostics.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/wavelength_mapping/diagnostics.rst) — Notes:
- [ ] **Wavelength Mapping — Testing** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/wavelength_mapping/testing.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/wavelength_mapping/testing.rst) — Notes:
- [ ] **Wavelength Mapping — Calculations** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/wavelength_mapping/calculations.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/wavelength_mapping/calculations.rst) — Notes:
- [ ] **Wavelength Mapping — Validation** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/wavelength_mapping/validation.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/wavelength_mapping/validation.rst) — Notes:

### Spectral Corrections (7 pages)

- [ ] **Spectral Corrections Overview** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/spectral_corrections/index.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/spectral_corrections/index.rst) — Notes:
- [ ] **Spectral Corrections — Inputs and Outputs** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/spectral_corrections/inputs_and_outputs.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/spectral_corrections/inputs_and_outputs.rst) — Notes:
- [ ] **Spectral Corrections — Procedure** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/spectral_corrections/procedure.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/spectral_corrections/procedure.rst) — Notes:
- [ ] **Spectral Corrections — Diagnostics** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/spectral_corrections/diagnostics.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/spectral_corrections/diagnostics.rst) — Notes:
- [ ] **Spectral Corrections — Testing** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/spectral_corrections/testing.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/spectral_corrections/testing.rst) — Notes:
- [ ] **Spectral Corrections — Calculations** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/spectral_corrections/calculations.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/spectral_corrections/calculations.rst) — Notes:
- [ ] **Spectral Corrections — Validation** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/spectral_corrections/validation.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/spectral_corrections/validation.rst) — Notes:

### Processed Spectrum Output and Retention (7 pages)

- [ ] **Processed Spectrum Output and Retention Overview** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/processed_spectrum_output_and_retention/index.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/processed_spectrum_output_and_retention/index.rst) — Notes:
- [ ] **Processed Spectrum Output and Retention — Inputs and Outputs** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/processed_spectrum_output_and_retention/inputs_and_outputs.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/processed_spectrum_output_and_retention/inputs_and_outputs.rst) — Notes:
- [ ] **Processed Spectrum Output and Retention — Procedure** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/processed_spectrum_output_and_retention/procedure.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/processed_spectrum_output_and_retention/procedure.rst) — Notes:
- [ ] **Processed Spectrum Output and Retention — Diagnostics** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/processed_spectrum_output_and_retention/diagnostics.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/processed_spectrum_output_and_retention/diagnostics.rst) — Notes:
- [ ] **Processed Spectrum Output and Retention — Testing** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/processed_spectrum_output_and_retention/testing.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/processed_spectrum_output_and_retention/testing.rst) — Notes:
- [ ] **Processed Spectrum Output and Retention — Calculations** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/processed_spectrum_output_and_retention/calculations.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/processed_spectrum_output_and_retention/calculations.rst) — Notes:
- [ ] **Processed Spectrum Output and Retention — Validation** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/primary_data_pipeline/processed_spectrum_output_and_retention/validation.html) · [Source](../../docs/source/subsystems/host_pc/primary_data_pipeline/processed_spectrum_output_and_retention/validation.rst) — Notes:

## Device Control and Acquisition Coordination (29 pages)

- [ ] **Device Control and Acquisition Coordination Overview** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/device_control_and_acquisition_coordination/index.html) · [Source](../../docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/index.rst) — Notes:

### Connection Management (7 pages)

- [ ] **Connection Management Overview** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/device_control_and_acquisition_coordination/connection_management/index.html) · [Source](../../docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/connection_management/index.rst) — Notes:
- [ ] **Connection Management — Inputs and Outputs** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/device_control_and_acquisition_coordination/connection_management/inputs_and_outputs.html) · [Source](../../docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/connection_management/inputs_and_outputs.rst) — Notes:
- [ ] **Connection Management — Procedure** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/device_control_and_acquisition_coordination/connection_management/procedure.html) · [Source](../../docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/connection_management/procedure.rst) — Notes:
- [ ] **Connection Management — Diagnostics** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/device_control_and_acquisition_coordination/connection_management/diagnostics.html) · [Source](../../docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/connection_management/diagnostics.rst) — Notes:
- [ ] **Connection Management — Testing** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/device_control_and_acquisition_coordination/connection_management/testing.html) · [Source](../../docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/connection_management/testing.rst) — Notes:
- [ ] **Connection Management — Calculations** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/device_control_and_acquisition_coordination/connection_management/calculations.html) · [Source](../../docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/connection_management/calculations.rst) — Notes:
- [ ] **Connection Management — Validation** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/device_control_and_acquisition_coordination/connection_management/validation.html) · [Source](../../docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/connection_management/validation.rst) — Notes:

### Acquisition Session Control (7 pages)

- [ ] **Acquisition Session Control Overview** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/device_control_and_acquisition_coordination/acquisition_session_control/index.html) · [Source](../../docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/acquisition_session_control/index.rst) — Notes:
- [ ] **Acquisition Session Control — Inputs and Outputs** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/device_control_and_acquisition_coordination/acquisition_session_control/inputs_and_outputs.html) · [Source](../../docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/acquisition_session_control/inputs_and_outputs.rst) — Notes:
- [ ] **Acquisition Session Control — Procedure** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/device_control_and_acquisition_coordination/acquisition_session_control/procedure.html) · [Source](../../docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/acquisition_session_control/procedure.rst) — Notes:
- [ ] **Acquisition Session Control — Diagnostics** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/device_control_and_acquisition_coordination/acquisition_session_control/diagnostics.html) · [Source](../../docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/acquisition_session_control/diagnostics.rst) — Notes:
- [ ] **Acquisition Session Control — Testing** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/device_control_and_acquisition_coordination/acquisition_session_control/testing.html) · [Source](../../docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/acquisition_session_control/testing.rst) — Notes:
- [ ] **Acquisition Session Control — Calculations** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/device_control_and_acquisition_coordination/acquisition_session_control/calculations.html) · [Source](../../docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/acquisition_session_control/calculations.rst) — Notes:
- [ ] **Acquisition Session Control — Validation** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/device_control_and_acquisition_coordination/acquisition_session_control/validation.html) · [Source](../../docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/acquisition_session_control/validation.rst) — Notes:

### Integration Time Control (7 pages)

- [ ] **Integration Time Control Overview** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/device_control_and_acquisition_coordination/integration_time_control/index.html) · [Source](../../docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/integration_time_control/index.rst) — Notes:
- [ ] **Integration Time Control — Inputs and Outputs** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/device_control_and_acquisition_coordination/integration_time_control/inputs_and_outputs.html) · [Source](../../docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/integration_time_control/inputs_and_outputs.rst) — Notes:
- [ ] **Integration Time Control — Procedure** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/device_control_and_acquisition_coordination/integration_time_control/procedure.html) · [Source](../../docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/integration_time_control/procedure.rst) — Notes:
- [ ] **Integration Time Control — Diagnostics** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/device_control_and_acquisition_coordination/integration_time_control/diagnostics.html) · [Source](../../docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/integration_time_control/diagnostics.rst) — Notes:
- [ ] **Integration Time Control — Testing** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/device_control_and_acquisition_coordination/integration_time_control/testing.html) · [Source](../../docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/integration_time_control/testing.rst) — Notes:
- [ ] **Integration Time Control — Calculations** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/device_control_and_acquisition_coordination/integration_time_control/calculations.html) · [Source](../../docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/integration_time_control/calculations.rst) — Notes:
- [ ] **Integration Time Control — Validation** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/device_control_and_acquisition_coordination/integration_time_control/validation.html) · [Source](../../docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/integration_time_control/validation.rst) — Notes:

### Command Status Handling (7 pages)

- [ ] **Command Status Handling Overview** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/device_control_and_acquisition_coordination/command_status_handling/index.html) · [Source](../../docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/command_status_handling/index.rst) — Notes:
- [ ] **Command Status Handling — Inputs and Outputs** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/device_control_and_acquisition_coordination/command_status_handling/inputs_and_outputs.html) · [Source](../../docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/command_status_handling/inputs_and_outputs.rst) — Notes:
- [ ] **Command Status Handling — Procedure** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/device_control_and_acquisition_coordination/command_status_handling/procedure.html) · [Source](../../docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/command_status_handling/procedure.rst) — Notes:
- [ ] **Command Status Handling — Diagnostics** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/device_control_and_acquisition_coordination/command_status_handling/diagnostics.html) · [Source](../../docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/command_status_handling/diagnostics.rst) — Notes:
- [ ] **Command Status Handling — Testing** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/device_control_and_acquisition_coordination/command_status_handling/testing.html) · [Source](../../docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/command_status_handling/testing.rst) — Notes:
- [ ] **Command Status Handling — Calculations** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/device_control_and_acquisition_coordination/command_status_handling/calculations.html) · [Source](../../docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/command_status_handling/calculations.rst) — Notes:
- [ ] **Command Status Handling — Validation** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/device_control_and_acquisition_coordination/command_status_handling/validation.html) · [Source](../../docs/source/subsystems/host_pc/device_control_and_acquisition_coordination/command_status_handling/validation.rst) — Notes:

## Operator Application (29 pages)

- [ ] **Operator Application Overview** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/operator_application/index.html) · [Source](../../docs/source/subsystems/host_pc/operator_application/index.rst) — Notes:

### Session Control (7 pages)

- [ ] **Session Control Overview** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/operator_application/session_control/index.html) · [Source](../../docs/source/subsystems/host_pc/operator_application/session_control/index.rst) — Notes:
- [ ] **Session Control — Inputs and Outputs** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/operator_application/session_control/inputs_and_outputs.html) · [Source](../../docs/source/subsystems/host_pc/operator_application/session_control/inputs_and_outputs.rst) — Notes:
- [ ] **Session Control — Procedure** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/operator_application/session_control/procedure.html) · [Source](../../docs/source/subsystems/host_pc/operator_application/session_control/procedure.rst) — Notes:
- [ ] **Session Control — Diagnostics** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/operator_application/session_control/diagnostics.html) · [Source](../../docs/source/subsystems/host_pc/operator_application/session_control/diagnostics.rst) — Notes:
- [ ] **Session Control — Testing** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/operator_application/session_control/testing.html) · [Source](../../docs/source/subsystems/host_pc/operator_application/session_control/testing.rst) — Notes:
- [ ] **Session Control — Calculations** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/operator_application/session_control/calculations.html) · [Source](../../docs/source/subsystems/host_pc/operator_application/session_control/calculations.rst) — Notes:
- [ ] **Session Control — Validation** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/operator_application/session_control/validation.html) · [Source](../../docs/source/subsystems/host_pc/operator_application/session_control/validation.rst) — Notes:

### Visualization (7 pages)

- [ ] **Visualization Overview** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/operator_application/visualization/index.html) · [Source](../../docs/source/subsystems/host_pc/operator_application/visualization/index.rst) — Notes:
- [ ] **Visualization — Inputs and Outputs** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/operator_application/visualization/inputs_and_outputs.html) · [Source](../../docs/source/subsystems/host_pc/operator_application/visualization/inputs_and_outputs.rst) — Notes:
- [ ] **Visualization — Procedure** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/operator_application/visualization/procedure.html) · [Source](../../docs/source/subsystems/host_pc/operator_application/visualization/procedure.rst) — Notes:
- [ ] **Visualization — Diagnostics** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/operator_application/visualization/diagnostics.html) · [Source](../../docs/source/subsystems/host_pc/operator_application/visualization/diagnostics.rst) — Notes:
- [ ] **Visualization — Testing** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/operator_application/visualization/testing.html) · [Source](../../docs/source/subsystems/host_pc/operator_application/visualization/testing.rst) — Notes:
- [ ] **Visualization — Calculations** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/operator_application/visualization/calculations.html) · [Source](../../docs/source/subsystems/host_pc/operator_application/visualization/calculations.rst) — Notes:
- [ ] **Visualization — Validation** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/operator_application/visualization/validation.html) · [Source](../../docs/source/subsystems/host_pc/operator_application/visualization/validation.rst) — Notes:

### Calibration and User Settings (7 pages)

- [ ] **Calibration and User Settings Overview** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/operator_application/calibration_and_user_settings/index.html) · [Source](../../docs/source/subsystems/host_pc/operator_application/calibration_and_user_settings/index.rst) — Notes:
- [ ] **Calibration and User Settings — Inputs and Outputs** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/operator_application/calibration_and_user_settings/inputs_and_outputs.html) · [Source](../../docs/source/subsystems/host_pc/operator_application/calibration_and_user_settings/inputs_and_outputs.rst) — Notes:
- [ ] **Calibration and User Settings — Procedure** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/operator_application/calibration_and_user_settings/procedure.html) · [Source](../../docs/source/subsystems/host_pc/operator_application/calibration_and_user_settings/procedure.rst) — Notes:
- [ ] **Calibration and User Settings — Diagnostics** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/operator_application/calibration_and_user_settings/diagnostics.html) · [Source](../../docs/source/subsystems/host_pc/operator_application/calibration_and_user_settings/diagnostics.rst) — Notes:
- [ ] **Calibration and User Settings — Testing** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/operator_application/calibration_and_user_settings/testing.html) · [Source](../../docs/source/subsystems/host_pc/operator_application/calibration_and_user_settings/testing.rst) — Notes:
- [ ] **Calibration and User Settings — Calculations** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/operator_application/calibration_and_user_settings/calculations.html) · [Source](../../docs/source/subsystems/host_pc/operator_application/calibration_and_user_settings/calculations.rst) — Notes:
- [ ] **Calibration and User Settings — Validation** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/operator_application/calibration_and_user_settings/validation.html) · [Source](../../docs/source/subsystems/host_pc/operator_application/calibration_and_user_settings/validation.rst) — Notes:

### Export Initiation and Session Retention (7 pages)

- [ ] **Export Initiation and Session Retention Overview** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/operator_application/export_initiation_and_session_retention/index.html) · [Source](../../docs/source/subsystems/host_pc/operator_application/export_initiation_and_session_retention/index.rst) — Notes:
- [ ] **Export Initiation and Session Retention — Inputs and Outputs** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/operator_application/export_initiation_and_session_retention/inputs_and_outputs.html) · [Source](../../docs/source/subsystems/host_pc/operator_application/export_initiation_and_session_retention/inputs_and_outputs.rst) — Notes:
- [ ] **Export Initiation and Session Retention — Procedure** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/operator_application/export_initiation_and_session_retention/procedure.html) · [Source](../../docs/source/subsystems/host_pc/operator_application/export_initiation_and_session_retention/procedure.rst) — Notes:
- [ ] **Export Initiation and Session Retention — Diagnostics** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/operator_application/export_initiation_and_session_retention/diagnostics.html) · [Source](../../docs/source/subsystems/host_pc/operator_application/export_initiation_and_session_retention/diagnostics.rst) — Notes:
- [ ] **Export Initiation and Session Retention — Testing** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/operator_application/export_initiation_and_session_retention/testing.html) · [Source](../../docs/source/subsystems/host_pc/operator_application/export_initiation_and_session_retention/testing.rst) — Notes:
- [ ] **Export Initiation and Session Retention — Calculations** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/operator_application/export_initiation_and_session_retention/calculations.html) · [Source](../../docs/source/subsystems/host_pc/operator_application/export_initiation_and_session_retention/calculations.rst) — Notes:
- [ ] **Export Initiation and Session Retention — Validation** — [Rendered](../../docs/build/html-structure-parity-section-2/subsystems/host_pc/operator_application/export_initiation_and_session_retention/validation.html) · [Source](../../docs/source/subsystems/host_pc/operator_application/export_initiation_and_session_retention/validation.rst) — Notes:

## General notes

- 
