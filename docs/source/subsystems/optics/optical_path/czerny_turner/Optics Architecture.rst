Optics Architecture
===================

UUID: ``0F0D41FE-6F7B-4A3E-A8DD-3C1F7DCE2481``

The optical subsystem is responsible for separating incident light by
wavelength and imaging the resulting spectrum onto the TCD1304DG linear CCD.
The selected layout is a reflective Czerny-Turner-style path:

1. A slit defines the source width presented to the spectrometer.
2. A collimating mirror forms a collimated beam.
3. A reflective diffraction grating disperses the beam by wavelength.
4. A focusing mirror images the dispersed spectrum onto the CCD.
5. The TCD1304DG converts the focused spectrum into a sequential analog signal.

This layout supports a compact optical path and avoids lens chromatic effects
across the wide VIS-NIR range. Slit width, mirror placement, grating angle, and
CCD position must be tuned together because they determine throughput,
resolution, wavelength coverage, and alignment sensitivity.



