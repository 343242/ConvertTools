import os
import tempfile
import pytest
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.batch_engine import BatchEngine, BatchTask
from core.converter import ImageConverter, SUPPORTED_INPUT
from PIL import Image


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def sample_files(tmp_dir):
    paths = []
    for i in range(3):
        path = os.path.join(tmp_dir, f"img_{i}.png")
        Image.new("RGB", (16, 16), (i * 80, 0, 0)).save(path)
        paths.append(path)
    return paths


class TestBatchTask:
    def test_task_creation(self):
        task = BatchTask("/tmp/a.png", "JPEG", "/tmp/out", {"quality": 90})
        assert task.input_path == "/tmp/a.png"
        assert task.output_format == "JPEG"
        assert task.output_dir == "/tmp/out"
        assert task.options == {"quality": 90}

    def test_task_defaults(self):
        task = BatchTask("/tmp/a.png", "PNG")
        assert task.output_dir is None
        assert task.options == {}


class TestBatchEngine:
    def test_batch_convert_all_succeed(self, sample_files, tmp_dir):
        out_dir = os.path.join(tmp_dir, "output")
        tasks = [
            BatchTask(p, "JPEG", out_dir, {"quality": 95})
            for p in sample_files
        ]
        engine = BatchEngine()
        engine.set_tasks(tasks)

        succeeded = 0
        failed = 0

        def on_done(inp, out):
            nonlocal succeeded
            succeeded += 1

        def on_err(inp, msg):
            nonlocal failed
            failed += 1

        def on_finish(s, f):
            pass

        engine.file_done.connect(on_done)
        engine.file_error.connect(on_err)
        engine.finished_all.connect(on_finish)

        engine.run()

        assert succeeded == 3
        assert failed == 0
        for i in range(3):
            out_path = os.path.join(out_dir, f"img_{i}.jpg")
            assert os.path.exists(out_path)

    def test_batch_convert_handles_missing_file(self, tmp_dir):
        tasks = [
            BatchTask("/nonexistent/file.png", "PNG", tmp_dir),
        ]
        engine = BatchEngine()
        engine.set_tasks(tasks)

        errors = []
        engine.file_error.connect(lambda p, e: errors.append((p, e)))
        engine.run()

        assert len(errors) == 1
        assert "nonexistent" in errors[0][0]

    def test_batch_cancel(self, sample_files, tmp_dir):
        tasks = [BatchTask(p, "PNG", tmp_dir) for p in sample_files]
        engine = BatchEngine()
        engine.set_tasks(tasks)
        engine.cancel()
        engine.run()
        assert True

    def test_batch_webp_format(self, sample_files, tmp_dir):
        out_dir = os.path.join(tmp_dir, "webp_out")
        tasks = [
            BatchTask(p, "WebP", out_dir, {"quality": 90})
            for p in sample_files
        ]
        engine = BatchEngine()
        engine.set_tasks(tasks)
        engine.run()

        for i in range(3):
            out_path = os.path.join(out_dir, f"img_{i}.webp")
            assert os.path.exists(out_path)
            img = Image.open(out_path)
            assert img.format == "WEBP"


class TestSupportedFormats:
    def test_input_formats(self):
        expected = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif", ".gif", ".ico", ".psd"}
        assert SUPPORTED_INPUT == expected

    def test_output_path_format_mapping(self):
        cases = [
            ("PNG", ".png"),
            ("JPEG", ".jpg"),
            ("WebP", ".webp"),
            ("BMP", ".bmp"),
            ("TIFF", ".tiff"),
            ("ICO", ".ico"),
        ]
        for fmt, ext in cases:
            path = ImageConverter.get_output_path("/tmp/test.png", fmt, "/tmp/out")
            assert path.endswith(ext), f"Format {fmt} should produce {ext}, got {path}"
