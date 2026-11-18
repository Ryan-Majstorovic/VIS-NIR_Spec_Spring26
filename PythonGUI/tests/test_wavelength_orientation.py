import unittest

import numpy as np

from backend.models.config import CalibrationConfig, DeviceConfig, PixelMappingPoint
from backend.processing.calibration_manager import CalibrationManager
from backend.processing.wavelength_map import indices_to_wavelengths


class WavelengthOrientationTests(unittest.TestCase):
    def setUp(self):
        self.manager = CalibrationManager(CalibrationConfig())
        self.device = DeviceConfig(effective_start_index=32, effective_sample_count=100)

    def fit(self, pairs, order=1):
        points = [PixelMappingPoint(pixel_index=pixel, wavelength_nm=nm) for pixel, nm in pairs]
        return self.manager.fit_wavelength_coefficients(points, fit_order=order, device_config=self.device)

    def test_accepts_both_wavelength_directions(self):
        for endpoints in ((420, 680), (680, 420)):
            coefficients = self.fit(zip((32, 131), endpoints))
            np.testing.assert_allclose(indices_to_wavelengths([32, 131], coefficients), endpoints)

    def test_ignores_turning_points_outside_the_active_pixels(self):
        pixels = (32, 80, 131)
        wavelengths = [700 - (pixel - 20) ** 2 / 100 for pixel in pixels]
        coefficients = self.fit(zip(pixels, wavelengths), order=2)
        self.assertTrue(np.all(np.diff(indices_to_wavelengths(range(32, 132), coefficients)) < 0))

    def test_rejects_a_reversal_or_flat_wavelengths(self):
        for pairs, order in (
            ([(32, 480), (80, 580), (131, 490)], 2),
            ([(32, 500), (131, 500)], 1),
        ):
            with self.subTest(pairs=pairs), self.assertRaisesRegex(ValueError, "must increase or decrease"):
                self.fit(pairs, order)
