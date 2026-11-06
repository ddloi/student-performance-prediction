"""Self-implemented estimators used by runtime and saved model caches."""

import numpy as np


class LinearRegressionScratch:
    """Mô hình Hồi quy Tuyến tính tự cài đặt bằng Gradient Descent."""
    def __init__(self, learning_rate: float = 0.01, n_iterations: int = 5000, *, verbose: bool = False):
        self.lr = learning_rate
        self.n_iter = n_iterations
        self.verbose = verbose
        self.weights = None
        self.bias = None
        self.loss_history = []

    def fit(self, X: np.ndarray, y: np.ndarray):
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        self.weights = np.zeros(X.shape[1])
        self.bias = 0.0
        self.loss_history = []

        for iteration in range(self.n_iter):
            self._update_weights(X, y)
            if getattr(self, "verbose", False) and (iteration + 1) % max(1, self.n_iter // 10) == 0:
                print(f"  Iteration {iteration+1}/{self.n_iter} | Loss: {self.loss_history[-1]:.6f}")
        return self

    def _update_weights(self, X: np.ndarray, y: np.ndarray) -> None:
        sample_count = X.shape[0]
        error = self.predict(X) - y
        self.loss_history.append(np.mean(error ** 2) / 2)
        weight_gradient = (1 / sample_count) * (X.T @ error)
        bias_gradient = (1 / sample_count) * np.sum(error)
        self.weights -= self.lr * weight_gradient
        self.bias -= self.lr * bias_gradient

    def predict(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=np.float64)
        return X @ self.weights + self.bias

    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        residual_sum = np.sum((y - self.predict(X)) ** 2)
        total_sum = np.sum((y - np.mean(y)) ** 2)
        return float(1 - residual_sum / total_sum)


class LinearRegressionManual(LinearRegressionScratch):
    """Compare GD with the historical pseudoinverse implementation of OLS."""

    def __init__(self, method="gd", learning_rate=0.01, n_iterations=5000, verbose=False):
        super().__init__(learning_rate, n_iterations, verbose=verbose)
        self.method = method

    def fit(self, X: np.ndarray, y: np.ndarray):
        if self.method == "gd":
            return super().fit(X, y)
        if self.method != "normal_equation":
            raise ValueError("Method must be 'gd' or 'normal_equation'")
        features = np.asarray(X, dtype=np.float64)
        targets = np.asarray(y, dtype=np.float64)
        design = np.c_[np.ones((features.shape[0], 1)), features]
        parameters = np.linalg.pinv(design.T @ design) @ design.T @ targets
        self.bias = float(parameters[0])
        self.weights = parameters[1:]
        return self

