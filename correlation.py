import numpy as np
from typing import List

def covariance(matrix_1: np.ndarray, matrix_2: np.ndarray) -> float:
    return np.einsum("ij,ij->", matrix_1 - matrix_1.mean(), matrix_2 - matrix_2.mean()) / (np.prod(matrix_1.shape) + 1)

def covarianceMatrix(matrixes: List[np.ndarray]) -> np.ndarray:
    n = len(matrixes)
    covariances = np.zeros((n, n))
    for i in range(n):
        for j in range(i, n):
            covariances[i][j] = covariance(matrixes[i], matrixes[j])
            covariances[j][i] = covariances[i][j]

    return covariances


if __name__ == "__main__":
    from DataExtractor import DataExtractor

    file = "MERRA-2.nc4"
    extractor = DataExtractor(file)
    data = extractor.getData()
    keys = list(data.keys())
    n = len(data.keys())

    matrices = [i[0, 0, :, :] for i in data.values()]
    covariances = covarianceMatrix(matrices)

    for i in range(5):
        covariances[i][i] = 0

    max_covariance_index = np.argmax(covariances)
    max_covariance_var_1 = keys[max_covariance_index % n]
    max_covariance_var_2 = keys[max_covariance_index // n]
    print(f"Maximal covariance: {covariances.max()} between {max_covariance_var_1} and {max_covariance_var_2}")

    min_covariance_index = np.argmin(covariances)
    min_covariance_var_1 = keys[min_covariance_index % n]
    min_covariance_var_2 = keys[min_covariance_index // n]
    print(f"Minimal covariance: {covariances.min()} between {min_covariance_var_1} and {min_covariance_var_2}")
