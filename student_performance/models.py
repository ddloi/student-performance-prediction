"""Self-implemented estimators used by runtime and saved model caches."""

import numpy as np


class LinearRegressionScratch:
    """Mô hình Hồi quy Tuyến tính tự cài đặt bằng Gradient Descent."""
    def __init__(self, learning_rate: float = 0.01, n_iterations: int = 5000):
        self.lr = learning_rate
        self.n_iter = n_iterations
        self.weights = None
        self.bias = None
        self.loss_history = []

    def fit(self, X: np.ndarray, y: np.ndarray):
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        n_samples, n_features = X.shape

        self.weights = np.zeros(n_features)
        self.bias = 0.0
        self.loss_history = []

        for _ in range(self.n_iter):
            y_pred = X @ self.weights + self.bias
            error = y_pred - y
            loss = np.mean(error ** 2) / 2
            self.loss_history.append(loss)

            dw = (1 / n_samples) * (X.T @ error)
            db = (1 / n_samples) * np.sum(error)

            self.weights -= self.lr * dw
            self.bias -= self.lr * db
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=np.float64)
        return X @ self.weights + self.bias

