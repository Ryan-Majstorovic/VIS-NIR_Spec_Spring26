Second-Order Diffraction
========================

UUID: ``406D13B5-12F2-4144-9F1E-C36E6D515FA0``

Second-order diffraction occurs when shorter wavelengths overlap longer
wavelength first-order content on the detector. This is especially important in
the long-wavelength portion of the 400-1000 nm target range.

The current mitigation strategy is physical filtering:

* Test a long-pass filter or custom thin-film linear variable filter.
* Prefer a cutoff behavior matched to the CCD wavelength position.
* Validate the filter against known reference sources and broadband input.

Software-only correction is not sufficient as the primary mitigation because it
requires knowing the original short-wavelength contribution and optical
throughput accurately. For research data, unmeasured overlap should be reduced
physically before any post-processing correction is applied.



