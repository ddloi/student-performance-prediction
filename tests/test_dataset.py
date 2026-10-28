"""Twelve existing dataset consistency checks, discoverable by unittest.

Run: python -m unittest tests.test_dataset -v
These checks preserve the original assertions. The declared-feature check alone
does not establish that the full training pipeline is free of data leakage.
"""

import unittest

import numpy as np
import pandas as pd

from student_performance.paths import DATASET_PATH, RAW_DATA_PATH


EXPECTED_COLS = [
    "stud_id",
    "status_K1", "gpa1", "Tin_Chi_K1", "So_Gio_Tu_Hoc_K1", "So_Lan_Tham_Gia_HD_K1", "Diem_Ren_Luyen_K1",
    "status_K2", "gpa2", "Tin_Chi_K2", "So_Gio_Tu_Hoc_K2", "So_Lan_Tham_Gia_HD_K2", "Diem_Ren_Luyen_K2",
    "status_K3", "gpa3", "Tin_Chi_K3", "So_Gio_Tu_Hoc_K3", "So_Lan_Tham_Gia_HD_K3", "Diem_Ren_Luyen_K3",
    "Tong_Tin_Chi", "cgpa", "Diem_Ren_Luyen_TB", "Xep_Loai_DRL", "Xep_Loai_Hoc_Luc",
]


class DatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = pd.read_csv(DATASET_PATH)
        cls.df_orig = pd.read_csv(RAW_DATA_PATH)

    def test_01_shape(self):
        self.assertEqual(self.df.shape, (500, 24))

    def test_02_columns(self):
        self.assertEqual(list(self.df.columns), EXPECTED_COLS)

    def test_03_no_nulls(self):
        self.assertEqual(self.df.isnull().sum().sum(), 0)

    def test_04_original_gpa_integrity(self):
        df, df_orig = self.df, self.df_orig
        gpa1_eq = np.allclose(df.loc[:99, "gpa1"], df_orig.loc[:99, "gpa1"])
        gpa2_eq = np.allclose(df.loc[:99, "gpa2"], df_orig.loc[:99, "gpa2"])
        raw_gpa3_filled = df_orig.loc[:99, "gpa3"].fillna(0.0)
        gpa3_eq = np.allclose(df.loc[:99, "gpa3"], raw_gpa3_filled)
        self.assertTrue(gpa1_eq and gpa2_eq and gpa3_eq)

    def test_05_first_semester_active_integrity(self):
        df = self.df
        k1_active = (df["status_K1"] == "Active").all() and (df["Tin_Chi_K1"] >= 15).all() and (df["gpa1"] > 0).all()
        self.assertTrue(k1_active)

    def test_06_second_semester_leave_consistency(self):
        leave_k2 = self.df[self.df["status_K2"] == "Leave"]
        leave_k2_valid = (
            (leave_k2["Tin_Chi_K2"] == 0).all()
            and (leave_k2["gpa2"] == 0.0).all()
            and (leave_k2["So_Gio_Tu_Hoc_K2"] == 0.0).all()
            and (leave_k2["Diem_Ren_Luyen_K2"] == 0).all()
        )
        self.assertTrue(leave_k2_valid)

    def test_07_third_semester_leave_consistency(self):
        leave_k3 = self.df[self.df["status_K3"] == "Leave"]
        leave_k3_valid = (
            (leave_k3["Tin_Chi_K3"] == 0).all()
            and (leave_k3["gpa3"] == 0.0).all()
            and (leave_k3["So_Gio_Tu_Hoc_K3"] == 0.0).all()
            and (leave_k3["Diem_Ren_Luyen_K3"] == 0).all()
        )
        self.assertTrue(leave_k3_valid)

    def test_08_credit_sum(self):
        df = self.df
        tc_sum_ok = (df["Tong_Tin_Chi"] == (df["Tin_Chi_K1"] + df["Tin_Chi_K2"] + df["Tin_Chi_K3"])).all()
        self.assertTrue(tc_sum_ok)

    def test_09_weighted_cgpa_formula(self):
        df = self.df
        calc_cgpa = np.where(
            df["Tong_Tin_Chi"] > 0,
            np.round(
                (df["gpa1"] * df["Tin_Chi_K1"] + df["gpa2"] * df["Tin_Chi_K2"] + df["gpa3"] * df["Tin_Chi_K3"])
                / df["Tong_Tin_Chi"],
                2,
            ),
            0.0,
        )
        cgpa_diff = (df["cgpa"] - calc_cgpa).abs()
        self.assertTrue((cgpa_diff < 0.0001).all(), f"Max difference: {cgpa_diff.max():.6f}")

    def test_10_drl_integer_rounding(self):
        df = self.df
        active_cnt = (df["status_K1"] == "Active").astype(int) + (df["status_K2"] == "Active").astype(int) + (df["status_K3"] == "Active").astype(int)
        calc_drl_tb = np.where(
            active_cnt > 0,
            np.round((df["Diem_Ren_Luyen_K1"] + df["Diem_Ren_Luyen_K2"] + df["Diem_Ren_Luyen_K3"]) / active_cnt).astype(int),
            0,
        )
        drl_diff = (df["Diem_Ren_Luyen_TB"] - calc_drl_tb).abs()
        is_integer = np.issubdtype(df["Diem_Ren_Luyen_TB"].dtype, np.integer) or (df["Diem_Ren_Luyen_TB"] % 1 == 0).all()
        self.assertTrue((drl_diff == 0).all() and is_integer)

    def test_11_classification_logic(self):
        def verify_drl(row):
            score = int(row["Diem_Ren_Luyen_TB"])
            expected = "Xuất sắc" if score >= 90 else ("Tốt" if score >= 80 else ("Khá" if score >= 65 else ("Trung bình" if score >= 50 else "Yếu")))
            return row["Xep_Loai_DRL"] == expected

        def verify_hoc_luc(row):
            gpa = row["cgpa"]
            expected = "Xuất sắc" if gpa >= 3.6 else ("Giỏi" if gpa >= 3.2 else ("Khá" if gpa >= 2.5 else ("Trung bình" if gpa >= 2.0 else "Yếu")))
            return row["Xep_Loai_Hoc_Luc"] == expected

        self.assertTrue(self.df.apply(verify_drl, axis=1).all() and self.df.apply(verify_hoc_luc, axis=1).all())

    def test_12_declared_features_exclude_future_columns(self):
        features_k1_k2 = [
            "status_K1", "gpa1", "Tin_Chi_K1", "So_Gio_Tu_Hoc_K1", "So_Lan_Tham_Gia_HD_K1", "Diem_Ren_Luyen_K1",
            "status_K2", "gpa2", "Tin_Chi_K2", "So_Gio_Tu_Hoc_K2", "So_Lan_Tham_Gia_HD_K2", "Diem_Ren_Luyen_K2",
        ]
        has_leakage = any(
            "k3" in feature.lower()
            or feature in ["cgpa", "Tong_Tin_Chi", "Diem_Ren_Luyen_TB", "Xep_Loai_Hoc_Luc", "Xep_Loai_DRL"]
            for feature in features_k1_k2
        )
        self.assertFalse(has_leakage)


if __name__ == "__main__":
    unittest.main()
