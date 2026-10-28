"""Regression checks for relocation, saved models and safe module imports."""

import importlib
import os
import pickle
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest

from fastapi.testclient import TestClient

from student_performance import api
from student_performance.models import LinearRegressionScratch
from student_performance.paths import PROJECT_ROOT


class StructureTests(unittest.TestCase):
    def test_legacy_pickle_class_still_resolves(self):
        legacy_module = importlib.import_module("model_engine")
        self.assertIs(legacy_module.LinearRegressionScratch, LinearRegressionScratch)
        # The existing cache records this original import path for its class.
        self.assertIs(pickle.loads(b"cmodel_engine\nLinearRegressionScratch\n."), LinearRegressionScratch)

    def test_resources_are_available_from_another_working_directory(self):
        original_directory = Path.cwd()
        with tempfile.TemporaryDirectory() as directory:
            try:
                os.chdir(directory)
                with TestClient(api.app) as client:
                    for url in (
                        "/",
                        "/static/app.js",
                        "/figures/scratch_lr_loss_curve.png",
                        "/api/student-detail/491",
                        "/api/test-samples",
                        "/download/report",
                        "/download/compare-csv",
                    ):
                        with self.subTest(url=url):
                            self.assertEqual(client.get(url).status_code, 200)
            finally:
                os.chdir(original_directory)

    def test_importing_modules_does_not_run_data_or_training_jobs(self):
        code = textwrap.dedent("""\
            import importlib
            from unittest.mock import patch
            import joblib
            import pandas as pd
            import matplotlib.pyplot as plt
            from docx.document import Document

            def unexpected_job(*args, **kwargs):
                raise AssertionError('Import attempted a data, model or report job')

            with patch.object(pd, 'read_csv', side_effect=unexpected_job), \\
                 patch.object(pd.DataFrame, 'to_csv', side_effect=unexpected_job), \\
                 patch.object(joblib, 'load', side_effect=unexpected_job), \\
                 patch.object(joblib, 'dump', side_effect=unexpected_job), \\
                 patch.object(plt, 'savefig', side_effect=unexpected_job), \\
                 patch.object(Document, 'save', side_effect=unexpected_job):
                for name in (
                    'student_performance.engine', 'student_performance.api',
                    'scripts.generate_dataset', 'scripts.train_models',
                    'scripts.compare_linear_regression', 'scripts.generate_report',
                    'tests.test_dataset',
                ):
                    importlib.import_module(name)
            print('SAFE_IMPORTS')
        """)
        environment = os.environ.copy()
        environment["PYTHONPATH"] = os.pathsep.join(
            filter(None, [str(PROJECT_ROOT), environment.get("PYTHONPATH")])
        )
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, "-c", code],
                cwd=directory,
                env=environment,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=60,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "SAFE_IMPORTS")


if __name__ == "__main__":
    unittest.main()
