"""Regression checks for the demo API. Run: python -m unittest tests.test_api -v.

Install test dependencies first: pip install -r requirements-dev.txt.
"""

import unittest
from unittest.mock import patch

import pandas as pd
from fastapi.testclient import TestClient

from student_performance import api


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(api.app)
        cls.payload = cls.client.get("/api/student-detail/491").json()

    def test_health_and_page(self):
        self.assertTrue(self.client.get("/api/health").json()["models_loaded"])
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn('lang="vi"', response.text)

    def test_each_model_matches_its_comparison(self):
        names = {
            "Linear Regression (Scratch GD)": "Linear Regression (Scratch GD)",
            "Linear Regression (sklearn)": "Linear Regression (sklearn OLS)",
            "Ridge Regression": "Ridge Regression",
            "Random Forest": "Random Forest Regressor",
        }
        for selected, comparison in names.items():
            with self.subTest(model=selected):
                response = self.client.post("/api/predict", json={**self.payload, "selected_model": selected})
                self.assertEqual(response.status_code, 200)
                result = response.json()
                self.assertEqual(result["predicted_gpa3"], result["model_comparison"][comparison])
                self.assertGreaterEqual(result["predicted_gpa3"], 0)
                self.assertLessEqual(result["predicted_gpa3"], 4)

    def test_unknown_model_rejected_instead_of_silent_fallback(self):
        response = self.client.post("/api/predict", json={**self.payload, "selected_model": "missing-model"})
        self.assertEqual(response.status_code, 422)

    def test_zero_drl_is_preserved_and_only_none_uses_average(self):
        response = self.client.post("/api/predict", json={**self.payload, "Diem_Ren_Luyen_K3": 0})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["features_summary"]["drl_eval"], 0)
        self.assertEqual(response.json()["rank_details"]["drl_rank"], "Yếu")
        response = self.client.post("/api/predict", json={**self.payload, "Diem_Ren_Luyen_K3": None})
        self.assertEqual(response.status_code, 200)
        expected = round((self.payload["Diem_Ren_Luyen_K1"] + self.payload["Diem_Ren_Luyen_K2"]) / 2, 1)
        self.assertEqual(response.json()["features_summary"]["drl_eval"], expected)

    def test_invalid_gpa_rejected(self):
        for gpa in (-0.1, 4.01, None):
            with self.subTest(gpa=gpa):
                response = self.client.post("/api/predict", json={**self.payload, "gpa1": gpa})
                self.assertEqual(response.status_code, 422)

    def test_search_is_literal_and_empty_state_is_page_one(self):
        for search in ("[", ".*", "999999"):
            with self.subTest(search=search):
                response = self.client.get("/api/test-samples", params={"search": search, "page": 999})
                self.assertEqual(response.status_code, 200)
                result = response.json()
                self.assertEqual(result["records"], [])
                self.assertEqual(result["pagination"]["page"], 1)
                self.assertEqual(result["pagination"]["total_pages"], 1)

    def test_search_filter_and_page_clamping(self):
        response = self.client.get("/api/test-samples", params={"page": 999})
        result = response.json()
        self.assertEqual(result["pagination"]["page"], result["pagination"]["total_pages"])
        self.assertTrue(result["records"])
        response = self.client.get("/api/test-samples", params={"filter_result": "LỆCH"})
        self.assertTrue(all(row["Ket_Qua_Hoc_Luc"] == "LỆCH" for row in response.json()["records"]))
        response = self.client.get("/api/test-samples", params={"search": "491"})
        self.assertEqual([row["stud_id"] for row in response.json()["records"]], [491])

    def test_empty_comparison_file_has_serializable_summary(self):
        frame = pd.DataFrame(columns=["stud_id", "Ket_Qua_Hoc_Luc", "Do_Lech_GPA"])
        with patch.object(api.pd, "read_csv", return_value=frame):
            response = self.client.get("/api/test-samples")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["summary"]["total_test_students"], 0)
        self.assertEqual(response.json()["summary"]["mean_gpa_error"], 0)

    def test_student_detail_preserves_zero_semester_three_values(self):
        frame = pd.read_csv(api.DATASET_CSV).iloc[:1].copy()
        student_id = int(frame.iloc[0]["stud_id"])
        frame.loc[:, "Tin_Chi_K3"] = 0
        frame.loc[:, "Diem_Ren_Luyen_K3"] = 0
        with patch.object(api.pd, "read_csv", return_value=frame):
            response = self.client.get(f"/api/student-detail/{student_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["Tin_Chi_K3"], 0)
        self.assertEqual(response.json()["Diem_Ren_Luyen_K3"], 0)

    def test_missing_student_and_downloads(self):
        self.assertEqual(self.client.get("/api/student-detail/999999").status_code, 404)
        for path in ("/download/report", "/download/compare-csv"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertIn("attachment", response.headers["content-disposition"])


if __name__ == "__main__":
    unittest.main()
