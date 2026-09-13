Procedure
=========

Use the following host-PC procedure to capture or update bias and dark correction parameters:

1. Start the desktop app and connect to the spectrometer.

2. Stream valid frames into the rolling session buffer.

3. Cover the sensor or otherwise block light so the buffered frames represent a bias-only condition.

4. Open **Tools -> Calibration Manager** and set ``bias_capture_frame_count`` to the number of covered frames to average.

5. Run **Capture B_p**. The app averages the most recent buffered covered frames and writes the result into ``bias_counts``.

6. If a stored per-pixel dark vector exists, paste or load it into ``dark_offset_counts``. If no stored vector exists, leave it empty.

7. Enable or disable ``apply_dark_subtraction`` depending on whether frame-dark estimation should be active at runtime.

8. Run **Preview Calibration**. The latest frame is rebuilt immediately with the new calibration state for verification.

9. Inspect the live spectrum and export a short session if you need offline verification of captured values.

10. Run **Save Calibration** to persist the configuration to ``PythonGUI/configs/calibration.json``.