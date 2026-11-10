import io
import logging
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.core.runtime import configure_logging


class LoggingTests(unittest.TestCase):
    def test_windowed_launch_does_not_log_into_kivy_redirected_stderr(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch('sys.__stdout__', None), patch('logging.basicConfig') as setup:
                configure_logging(Path(directory)/'app.log')
            handlers = setup.call_args.kwargs['handlers']
            self.assertEqual(len(handlers), 1)
            self.assertIsInstance(handlers[0], logging.FileHandler)
            handlers[0].close()

    def test_console_launch_uses_original_console_stream(self):
        console = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            with patch('sys.__stdout__', console), patch('logging.basicConfig') as setup:
                configure_logging(Path(directory)/'app.log')
            handlers = setup.call_args.kwargs['handlers']
            self.assertEqual(len(handlers), 2)
            self.assertIs(handlers[1].stream, console)
            for handler in handlers:
                handler.close()
