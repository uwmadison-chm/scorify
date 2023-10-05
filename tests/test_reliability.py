import pytest

from scorify import reliability


def test_alpha():


    # https://www.youtube.com/watch?v=G0RblT5qkFQ
    data = [[2, 6, 8, 3, 2, 8, 5],
            [1, 5, 6, 2, 3, 6, 6],
            [1, 5, 9, 4, 2, 6, 4]]
    assert abs(reliability.alpha(data) - 0.94) < 0.01

    # https://www.youtube.com/watch?v=G0RblT5qkFQ
    data = [[4, 4, 3, 5, 3],
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
            [3, 3, 2, 3, 2]]
    transpose = [list(x) for x in zip(*data)]
    assert abs(reliability.alpha(transpose) - 0.289826) < 0.000001





