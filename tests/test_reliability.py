import pytest

from scorify import reliability
import numpy as np
import pandas as pd


def test_alpha():


    # https://www.youtube.com/watch?v=G0RblT5qkFQ
    df = pd.DataFrame(data=[[2, 1, 1],
                            [6, 5, 5],
                            [8, 6, 9],
                            [3, 2, 4],
                            [2, 3, 2],
                            [8, 6, 6],
                            [5, 6, 4]])
    assert abs(reliability.get_alpha(df) - 0.94) < 0.01


    # https://www.youtube.com/watch?v=G0RblT5qkFQ
    df = pd.DataFrame(data=[[4, 4, 3, 5, 3],
                            [3, 5, 1, 4, 1],
                            [3, 4, 4, 4, 4],
                            [3, 3, 5, 2, 1],
                            [3, 4, 5, 4, 3],
                            [4, 5, 5, 3, 2],
                            [2, 5, 5, 3, 4],
                            [3, 4, 4, 2, 4],
                            [3, 5, 4, 4, 3],
                            [3, 3, 2, 3, 2],
                            [3, 3, 2, 3, 2],
                            [3, 4, 1, 4, 2],
                            [2, 5, 3, 3, 1],
                            [4, 4, 4, 4, 2],
                            [3, 3, 5, 5, 1],
                            [3, 4, 5, 4, 3],
                            [4, 4, 1, 3, 1],
                            [3, 3, 5, 4, 4],
                            [2, 5, 3, 4, 2],
                            [3, 3, 2, 3, 2]])
    assert abs(reliability.get_alpha(df) - 0.289826) < 0.000001



def test_mahalanobis():


    # https://www.geeksforgeeks.org/how-to-calculate-mahalanobis-distance-in-python/
    df = pd.DataFrame(data=[[100000, 800000, 650000, 700000, 860000, 730000, 400000, 870000, 780000, 400000], 
                            [16000, 60000, 300000, 10000,  252000, 350000, 260000, 510000, 2000, 5000], 
                            [300, 400, 1230, 300, 400, 104, 632, 221, 142, 267],
                            [60, 88, 90, 87, 83, 81, 72, 91, 90, 93], 
                            [76, 89, 89, 57, 79, 84, 78, 99, 97, 99]])
    df = df.T
    mahal = reliability.get_mahalanobis(df)
    expected = [6.055764,
                2.579036,
                6.762529,
                7.482670,
                2.027900,
                2.380654,
                2.147466,
                4.915337,
                4.025548,
                6.623069]
    assert np.sum(np.abs(np.subtract(mahal, expected))) < 0.0001



