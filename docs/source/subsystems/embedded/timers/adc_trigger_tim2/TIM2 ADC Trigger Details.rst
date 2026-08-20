TIM2 ADC Trigger Details
============================

UUID: ``3C47779C-63B3-4C7D-A690-C41F7C042E70``

The ADC-trigger timing function shall provide a repeatable trigger for each CCD
sample during an active capture.  The exact trigger frequency, phase relative
to the analog waveform, trigger routing, monitor point, enable boundary, and
stop boundary are ``Not In Docs``.  They shall be specified before firmware
conformance is assessed.

**Expected outcome:** Each accepted effective pixel has one deterministic ADC
conversion opportunity, and triggers do not continue after the defined frame
completion boundary.





