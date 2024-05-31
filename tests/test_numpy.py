import numpy as np


def test_eliminate_zeroed_columns():
    a = np.array([[1,0, 0, 2], [3,0,0,5]])
    b = np.array([1,2])
    a = a[ :, ~np.all(a == 0, axis= 0)]

    x = np.linalg.solve(a,b)

    assert np.array_equal(a, np.array([[1, 2], [3, 5]]))
