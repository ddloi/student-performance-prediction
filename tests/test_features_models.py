"""Guard shared feature contracts and scratch estimators during refactoring."""

import unittest

import numpy as np
import pandas as pd

from student_performance.features import (
    FEATURE_ORDER_CLF, FEATURE_ORDER_REG, build_classification_features,
    build_regression_features, engineer_features_dict,
)
from student_performance.models import LinearRegressionManual, LinearRegressionScratch
from student_performance.paths import DATASET_PATH


class FeatureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = pd.read_csv(DATASET_PATH)

    def test_batch_and_single_student_features_agree_without_mutation(self):
        original = self.data.copy(deep=True)
        batch_reg = build_regression_features(self.data)
        batch_clf = build_classification_features(self.data)
        self.assertEqual(list(batch_reg.columns), FEATURE_ORDER_REG)
        self.assertEqual(list(batch_clf.columns), FEATURE_ORDER_CLF)
        for student_id in (8, 98, 99, 491, 595):
            row = self.data[self.data.stud_id == student_id].iloc[0]
            reg, clf = engineer_features_dict(row.to_dict())
            np.testing.assert_array_equal(reg.values[0], batch_reg.loc[row.name].values)
            np.testing.assert_array_equal(clf.values[0], batch_clf.loc[row.name].values)
        pd.testing.assert_frame_equal(self.data, original)

    def test_known_student_derived_values(self):
        row = self.data[self.data.stud_id == 595]
        features = build_regression_features(row).iloc[0]
        expected = {"gpa_trend": -.09, "gpa_avg": 3.305, "gpa2_sq": 10.6276,
                    "gpa1_x_gpa2": 10.921, "study_hours_avg": 24.3,
                    "gpa2_x_drl": 2.8688, "gpa_trend_x_hours": -2.187}
        for name, value in expected.items():
            self.assertAlmostEqual(features[name], value, places=10)

    def test_classification_does_not_require_third_semester_data(self):
        data = self.data.drop(columns=[name for name in self.data if "K3" in name])
        pd.testing.assert_frame_equal(
            build_classification_features(data), build_classification_features(self.data),
        )


class ScratchModelTests(unittest.TestCase):
    def test_gradient_descent_learns_a_known_line(self):
        features = np.array([[-1.], [0.], [1.]])
        targets = np.array([1., 3., 5.])
        model = LinearRegressionScratch().fit(features, targets)
        np.testing.assert_allclose(model.predict(features), targets, atol=1e-10)
        self.assertAlmostEqual(model.bias, 3.)
        self.assertAlmostEqual(model.weights[0], 2.)
        self.assertGreater(model.loss_history[0], model.loss_history[-1])

    def test_manual_ols_handles_dependent_columns(self):
        features = np.array([[-1., -2.], [0., 0.], [1., 2.]])
        targets = np.array([1., 3., 5.])
        model = LinearRegressionManual(method="normal_equation").fit(features, targets)
        np.testing.assert_allclose(model.predict(features), targets, atol=1e-12)
        self.assertAlmostEqual(model.score(features, targets), 1.)

    def test_refitting_resets_learned_state(self):
        features = np.array([[-1.], [0.], [1.]])
        model = LinearRegressionScratch(n_iterations=50).fit(features, np.array([1., 3., 5.]))
        model.fit(features, np.zeros(3))
        np.testing.assert_array_equal(model.weights, [0.])
        self.assertEqual(model.bias, 0.)
        self.assertEqual(len(model.loss_history), 50)
