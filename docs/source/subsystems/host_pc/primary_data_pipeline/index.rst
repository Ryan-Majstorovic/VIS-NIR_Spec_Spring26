Primary Data Pipeline
=====================

.. _uuid-2d3495cb-05f7-4990-9126-110d5070e578:

System Role
-----------

UUID: :ref:`2D3495CB-05F7-4990-9126-110D5070E578 <uuid-2d3495cb-05f7-4990-9126-110d5070e578>`

**Summary:** The Host PC primary data pipeline converts incoming device
transport data into validated, corrected, wavelength-associated, and retained
spectrum outputs. This is the main backend measurement path and therefore the
most rigorous Host PC behavior to document and test.

**Expected Outcome:** One continuous host-side processing path shall begin at
incoming device data and end at a processed spectrum record that is ready for
retention, visualization, and export initiation.

**Rationale:** This section isolates the measurement-processing backend from
acquisition-control and operator-facing concerns so the intended data product
can be reviewed against implementation without UI or protocol noise.

.. _uuid-ca0b9906-c320-4d0d-a856-bf8f3adfb7fd:

Pipeline Objectives
-------------------

UUID: :ref:`CA0B9906-C320-4D0D-A856-BF8F3ADFB7FD <uuid-ca0b9906-c320-4d0d-a856-bf8f3adfb7fd>`

**Objective 1:** Preserve the full incoming measurement content through ingress
and ADC reconstruction before downstream corrections are applied.

**Objective 2:** Apply only the intended host-side correction and mapping
stages needed to make the readout interpretable and comparable.

**Objective 3:** Keep retained pipeline outputs traceable to the corrected,
wavelength-associated spectrum product rather than to unrelated UI state.

**Objective 4:** Keep pipeline validation local to each transformation boundary
so later code review can isolate where intended behavior and implementation may
diverge.

.. _uuid-82ddd480-efc3-48b7-beb6-e3ed17755f65:

Stage Relationship
------------------

UUID: :ref:`82DDD480-EFC3-48B7-BEB6-E3ED17755F65 <uuid-82ddd480-efc3-48b7-beb6-e3ed17755f65>`

+---------------------------------------+----------------------------------------------------------+-----------------------------------------------------------+
| Stage                                 | Pipeline Role                                            | Resulting Data Condition                                  |
+=======================================+==========================================================+===========================================================+
| Ingress And ADC Reconstruction        | Turn incoming transport data into structured frame       | The host has reconstructable frame data and ordered ADC   |
|                                       | content and ordered ADC-domain measurement data.         | samples that can enter correction stages.                 |
+---------------------------------------+----------------------------------------------------------+-----------------------------------------------------------+
| Bias And Dark Correction              | Remove baseline detector offset and dark contribution    | The readout is shifted closer to scene-dominated signal   |
|                                       | from reconstructed detector data.                        | content.                                                  |
+---------------------------------------+----------------------------------------------------------+-----------------------------------------------------------+
| Bad Pixel Masking                     | Prevent known unreliable detector positions from         | Invalid detector positions no longer distort later        |
|                                       | propagating into later analysis.                         | calculations.                                             |
+---------------------------------------+----------------------------------------------------------+-----------------------------------------------------------+
| Wavelength Mapping                    | Relate corrected detector-position data to wavelength-   | The readout gains wavelength interpretation.              |
|                                       | domain meaning.                                          |                                                           |
+---------------------------------------+----------------------------------------------------------+-----------------------------------------------------------+
| Spectral Corrections                  | Group the remaining first-pass spectral correction       | The spectrum is further normalized or response-corrected  |
|                                       | behaviors until their intended definitions are split     | before retention and downstream use.                      |
|                                       | further.                                                 |                                                           |
+---------------------------------------+----------------------------------------------------------+-----------------------------------------------------------+
| Processed Spectrum Output And         | Deliver the corrected host-side spectrum product and     | The pipeline output is retained in a form ready for       |
| Retention                             | retain the session-ready data needed by later workflows. | visualization and export initiation.                      |
+---------------------------------------+----------------------------------------------------------+-----------------------------------------------------------+

.. note::

   Insert the user-provided pipeline overview or I/O diagram here after the
   Visio source and image are available.

Related Pages
-------------

.. toctree::
   :maxdepth: 1

   ingress_and_adc_reconstruction/index
   bias_dark_correction/index
   bad_pixel_masking/index
   wavelength_mapping/index
   spectral_corrections/index
   processed_spectrum_output_and_retention/index