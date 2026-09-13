Wavelength Coverage And Resolution
==================================

UUID: ``8D8313D8-A65B-4C40-B0A4-5F88B8E8E662``

The optical design target is 400-1000 nm coverage across the TCD1304DG active
array. The current firmware and host config reserve 3648 effective pixels for
light-sensitive data.

Coverage verification should use known reference wavelengths near both ends of
the target range and enough intermediate lines to fit a stable wavelength map.
The wavelength map should not be considered complete if it only fits the center
of the detector.

Resolution is tracked as FWHM of narrow sources. The project target is about
5 nm FWHM. FWHM should be measured after alignment and wavelength calibration,
then repeated at multiple wavelengths to catch grating-angle, focus, and slit
effects.



