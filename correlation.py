import numpy as np
from typing import List

def covariance(matrix_1: np.ndarray, matrix_2: np.ndarray) -> float:
    return np.einsum("ij,ij->", matrix_1 - matrix_1.mean(), matrix_2 - matrix_2.mean()) / np.prod(matrix_1.shape)

def covarianceMatrix(matrixes: List[np.ndarray]) -> np.ndarray:
    n = len(matrixes)
    covariances = np.zeros((n, n))
    for i in range(n):
        for j in range(i, n):
            covariances[i][j] = covariance(matrixes[i], matrixes[j])
            covariances[j][i] = covariances[i][j]

    return covariances

if __name__ == "__main__":
    m1 = np.array([
        [1, 2],
        [2, 3],
    ])

    m2 = np.random.random((2,2))

    print(covariance(m1, m2))
