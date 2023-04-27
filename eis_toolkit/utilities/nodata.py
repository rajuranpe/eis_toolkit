import functools
from numbers import Number
from typing import Any, Callable, Iterable, List, Optional

import numpy as np
import pandas as pd
from beartype import beartype
from beartype.typing import Dict

from eis_toolkit.checks.dataframe import check_columns_valid
from eis_toolkit.exceptions import InvalidColumnException, InvalidRasterBandException


@beartype
def set_nodata_raster_meta(raster_meta: Dict, nodata_value: Number) -> Dict:
    """
    Set new nodata value for raster metadata.

    Note that this function does not convert any data values, only changes/fixes metadata.

    Args:
        raster_meta: Raster metadata to be updated.
        nodata_value: Nodata value to be set.

    Returns:
        Raster metadata with updated nodata value.
    """
    out_meta = raster_meta.copy()
    out_meta.update({"nodata": nodata_value})
    return out_meta


@beartype
def replace_raster_nodata_each_band(
    raster_data: np.ndarray, nodata_per_band: Dict[int, Number | Iterable[Number]], new_nodata: Number = -9999
) -> np.ndarray:
    """
    Replace old nodata values with a new nodata value in a raster for each band separately.

    Args:
        raster_data: Multiband raster's data.
        nodata_per_band: Mapping of bands and their current nodata values.
        new_nodata: A new nodata value that will be used for all old nodata values and all bands. Defaults to -9999.

    Returns:
        The original raster data with replaced nodata values.

    Raises:
        InvalidRasterBandException: Invalid band index in nodata mapping.
    """
    if any(band > len(raster_data) or band < 1 for band in nodata_per_band.keys()):
        raise InvalidRasterBandException("Invalid band index in nodata mapping.")

    out_raster_data = raster_data.copy()

    for band, nodata_values in nodata_per_band.items():
        index = band - 1
        band_data = raster_data[index]
        out_data = replace_values_with_nodata(band_data, nodata_values, new_nodata)
        out_raster_data[index] = out_data

    return out_raster_data


@beartype
def replace_values_with_nodata(
    data: np.ndarray, values_to_replace: Number | Iterable[Number], new_nodata: Number = np.nan
) -> np.ndarray:
    """
    Replace multiple nodata values in a raster numpy array with a new nodata value.

    Args:
        in_data: Input raster data as a numpy array.
        values_to_replace: Values to be replaced with new_nodata.
        new_nodata: New nodata value to be set. Defaults to np.nan.

    Returns:
        Raster data with updated nodata values.
    """
    return np.where(np.isin(data, values_to_replace) | np.isinf(data), new_nodata, data)


@beartype
def replace_nodata_dataframe(
    df: pd.DataFrame,
    old_nodata: Number | Iterable[Number],
    new_nodata: Number = np.nan,
    columns: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Replace the nodata value in specified columns of a DataFrame.

    Args:
        df: Input DataFrame data.
        old_nodata: Current nodata value(s) to be replaced.
        new_nodata: New nodata value to be set. Defaults to np.nan.
        columns: List of column names to replace nodata values. Defaults to None (all columns).

    Returns:
        DataFrame with updated nodata values.
    """
    if columns is None:
        columns = df.columns
    else:
        if not check_columns_valid(df, columns):
            raise InvalidColumnException("All columns were not found in input dataframe.")

    out_df = df.copy()

    for col in columns:
        out_df[col] = out_df[col].replace(old_nodata, new_nodata)

    return out_df


def handle_nodata_as_nan(func: Callable):
    """Replace nodata_values with np.nan for function execution and reverses the replacement afterwards."""

    @functools.wraps(func)
    def wrapper(in_data: np.ndarray, *args: Any, nodata_values: List[np.number], **kwargs: Any) -> np.ndarray:
        replaced_data = replace_values_with_nodata(in_data, nodata_values, np.nan)
        result = func(replaced_data, *args, **kwargs)
        out_data = replace_values_with_nodata(result, np.nan, nodata_values)
        return out_data

    return wrapper
