from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from pydantic import ValidationError

from backend.models.config import CursorConfig
from backend.storage.config_store import ConfigStore
from frontend.spectrum_markers import (
    MarkerSelection,
    directional_extremum,
    global_extremum,
    marker_delta,
    marker_value,
    nearest_index,
    search_origin,
)


class CursorConfigTests(unittest.TestCase):
    def test_older_config_loads_cursor_defaults_and_saves_only_cursor_changes(self):
        with TemporaryDirectory() as directory:
            default_path = Path(directory) / "default_user.json"
            active_path = Path(directory) / "user.json"
            default_path.write_text('{"serial":{"port":"COM7"},"ui":{"live_display_fps":24}}', encoding="utf-8")
            store = ConfigStore(default_path, active_path)
            self.assertEqual(store.load().ui.cursor, CursorConfig())
            self.assertTrue(store.load().ui.cursor.swap_reference_on_double_click)
            preferences = CursorConfig(
                line_thickness=3.5, line_style="dashed", point_size="large", inactive_opacity_percent=30,
                palette="high_contrast", readout_size="large", readout_visibility="selected_reference",
                show_difference=False, swap_reference_on_double_click=False, peak_sensitivity_percent=2.25,
            )
            store.save_cursor(preferences)
            reloaded = ConfigStore(default_path, active_path).load()
            self.assertEqual(reloaded.ui.cursor, preferences)
            self.assertEqual(reloaded.serial.port, "COM7")
            self.assertEqual(reloaded.ui.live_display_fps, 24)

    def test_cursor_config_rejects_values_outside_display_options(self):
        for field, value in (
            ("line_thickness", 1.25), ("line_thickness", 4.5), ("inactive_opacity_percent", 27),
            ("peak_sensitivity_percent", float("nan")), ("peak_sensitivity_percent", 101),
        ):
            with self.subTest(field=field, value=value), self.assertRaises(ValidationError):
                CursorConfig.model_validate({field: value})


class SpectrumMarkerTests(unittest.TestCase):
    def test_place_and_move_three_numbered_markers_then_remove_reference(self):
        markers = MarkerSelection()
        self.assertEqual(markers.place(532), 1)
        for number, pixel in ((2, 650), (3, 723)):
            markers.adding = True
            self.assertEqual(markers.place(pixel), number)
            self.assertFalse(markers.adding)
        markers.reference = 1
        self.assertEqual(markers.place(724), 3)
        self.assertEqual(markers.pixels, {1: 532, 2: 650, 3: 724})
        markers.selected = 1
        self.assertEqual(markers.remove_selected(), 1)
        self.assertIsNone(markers.reference)
        self.assertEqual(markers.selected, 3)
        markers.adding = True
        self.assertEqual(markers.place(810), 4)

    def test_numbering_restarts_after_last_individual_removal(self):
        markers = MarkerSelection()
        for number in range(1, 5):
            markers.adding = True
            self.assertEqual(markers.place(number * 100), number)

        for number in range(4, 0, -1):
            self.assertEqual(markers.remove_selected(), number)
        self.assertEqual(markers.place(994), 1)
        self.assertEqual(markers.pixels, {1: 994})

    def test_search_origin_preserves_direction_if_marker_is_outside_trace(self):
        self.assertIsNone(search_origin([32, 34, 36], None))
        self.assertEqual(search_origin([32, 34, 36], 34), 1)
        self.assertEqual(search_origin([32, 34, 36], 33), 0.5)
        self.assertEqual(search_origin([32, 34, 36], 31), -0.5)
        self.assertEqual(search_origin([32, 34, 36], 37), 2.5)

    def test_snaps_to_real_pixel_and_keeps_pixel_when_domain_changes(self):
        self.assertEqual(nearest_index([32, 34, 38], 36), 1)
        self.assertEqual(nearest_index(range(32, 38), 100), 5)
        self.assertEqual(marker_value(range(34, 38), [1, 2, 3, 4], 36), (36, 3))
        self.assertIsNone(marker_value(range(37, 42), [1, 2, 3, 4, 5], 36))

    def test_delta_is_signed_b_minus_a(self):
        self.assertEqual(marker_delta((100, 0.75), (92, 0.25)), (-8, -0.5))

    def test_global_extrema_include_edges_and_ignore_nonfinite_values(self):
        values = [2.0, float("nan"), 2.0, -1.0]
        self.assertEqual(global_extremum(values, maximum=True), 0)
        self.assertEqual(global_extremum(values, maximum=False), 3)
        self.assertIsNone(global_extremum([], maximum=True))

    def test_peaks_in_both_directions_and_plateau_midpoint(self):
        values = [0, 2, 2, 2, 0, 3, 0]
        self.assertEqual(directional_extremum(values, None, direction=1, maximum=True, prominence=1), 2)
        self.assertEqual(directional_extremum(values, 2, direction=1, maximum=True, prominence=1), 5)
        self.assertEqual(directional_extremum(values, 5, direction=-1, maximum=True, prominence=1), 2)
        self.assertIsNone(directional_extremum(values, 5, direction=1, maximum=True, prominence=1))

    def test_valley_and_noise_filtering(self):
        values = [1, 0.96, 1, 0.2, 1]
        self.assertEqual(directional_extremum(values, None, direction=1, maximum=False, prominence=0.1), 3)
        self.assertEqual(directional_extremum(values, None, direction=1, maximum=False, prominence=0), 1)

    def test_flat_empty_and_gapped_traces(self):
        for values in ([], [1], [1, 1, 1], [0, 1, float("nan"), 0]):
            with self.subTest(values=values):
                self.assertIsNone(directional_extremum(values, None, direction=1, maximum=True, prominence=0))
