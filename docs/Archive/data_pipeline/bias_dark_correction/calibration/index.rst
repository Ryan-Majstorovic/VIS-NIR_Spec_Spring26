Bias and Dark Calibration
=========================

UUID: ``D29A5387-FD1F-40F8-9132-0R421ED6F4D9``

This page documents the calibration workflow for bias and dark correction parameters. The calibration process captures or loads the additive correction values (master bias ``B_p``, frame dark reference ``beta_f``, per-pixel dark offsets ``D_p``) that are later applied at runtime by the runtime_correction stage.

Overview
--------

The calibration procedure produces the following artifacts stored in ``CalibrationConfig``:

* **Master bias vector ``B_p``** -- Captured from averaged covered-frame measurements.
* **Per-pixel dark offset vector ``D_p``** -- Loaded from config or pasted into the calibration form.
* **Dark subtraction toggle ``apply_dark_subtraction``** -- Enables frame-dark estimation at runtime.

These values are consumed by the runtime correction pipeline on every incoming frame but are themselves produced by a separate calibration process that runs when the sensor is covered or dark.

Related Pages
-------------

.. toctree::
   :maxdepth: 1

   inputs_and_outputs
   procedure
   calculations