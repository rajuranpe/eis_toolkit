import numpy as np
import pandas as pd
import pytest

from eis_toolkit.exceptions import InvalidColumnException, NumericValueSignException
from eis_toolkit.transformations.coda.clr import CLR_transform

SINGLE_ROW_DATAFRAME = pd.DataFrame(np.array([1, 1, 1, 2])[None], columns=["a", "b", "c", "d"])

ONES_DATAFRAME_4x4 = pd.DataFrame(np.ones((4, 4)), columns=["a", "b", "c", "d"])

ZEROS_DATAFRAME_4x4 = pd.DataFrame(np.zeros((4, 4)), columns=["a", "b", "c", "d"])

sample_array = np.array([[65, 12, 18, 5], [63, 16, 15, 6]])
SAMPLE_DATAFRAME = pd.DataFrame(sample_array, columns=["a", "b", "c", "d"])


def test_CLR_transform_subcomposition():
    """Test CLR transformation with a subcomposition."""
    arr = np.array([1, 1, 1, 2])
    df = pd.DataFrame(arr[None], columns=["a", "b", "c", "d"])
    subcomposition = ["a", "b", "c"]
    result = CLR_transform(df, subcomposition)
    pd.testing.assert_frame_equal(pd.DataFrame(np.zeros((1, 3)), columns=subcomposition), result)


def test_CLR_transform_subcomposition_single_component():
    """Test CLR transformation with a single component."""
    arr = np.array([1, 1, 1, 2])
    df = pd.DataFrame(arr[None], columns=["a", "b", "c", "d"])
    result = CLR_transform(df, ["d"])
    pd.testing.assert_frame_equal(pd.DataFrame(np.zeros((1, 1)), columns=["d"]), result)


def test_CLR_transform_simple():
    """Test CLR transform core functionality."""
    result = CLR_transform(ONES_DATAFRAME_4x4)
    pd.testing.assert_frame_equal(result, ZEROS_DATAFRAME_4x4)


def test_CLR_transform_subset_returns_correct_size():
    """Test that the output dataframe contains the same amount of columns as was specified in the parameters."""
    result = CLR_transform(SAMPLE_DATAFRAME, ["a", "c", "d"])
    assert result.shape == (2, 3)


def test_CLR_transform_contains_zeros():
    """Test that running the transformation for a dataframe containing zeros raises the correct exception."""
    with pytest.raises(NumericValueSignException):
        df = SAMPLE_DATAFRAME.copy()
        df.iloc[0, 0] = 0
        CLR_transform(df)


def test_CLR_transform_with_unexpected_column_name():
    """Test that providing an invalid column name raises the correct exception."""
    with pytest.raises(InvalidColumnException):
        CLR_transform(SAMPLE_DATAFRAME, ["a", "e"])


# TODO: test with unnamed columns


# def test_inverse_CLR_simple():
#     """TODO: docstring."""
#     result, scale = inverse_CLR(ZEROS_DATAFRAME_4x4)
#     pd.testing.assert_frame_equal(_scale(result, scale), ONES_DATAFRAME_4x4)  # TODO: call each row with its scale


# TODO: test inverse subcomposition
