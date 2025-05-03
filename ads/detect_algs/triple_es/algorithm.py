import numpy as np
import pandas as pd

from dataclasses import dataclass
from sklearn.preprocessing import MinMaxScaler
from .model import TripleES


@dataclass
class CustomParameters:
    period: int = 1
    trend: str = "add"
    seasonality: str = "add"
    random_state: int = 42


def set_random_state(config: CustomParameters) -> None:
    seed = config.random_state
    import random

    random.seed(seed)
    np.random.seed(seed)


def triple_es_predict(
    data: np.ndarray,
    config: CustomParameters = CustomParameters(),
) -> np.float64:
    set_random_state(config)

    win = len(data)
    if len(data) >= 1000 and len(data) < 10000:
        win = 100
    if len(data) >= 10000:
        win = 1000

    # Change the data format from epoch to relative
    min_epoch = data[0]
    relative_data = data[len(data) - win :] - min_epoch

    triple_es: TripleES = TripleES(
        relative_data,
        config.period,
        config.trend,
        config.seasonality,
        use_boxcox=False,
    )
    model = triple_es.fit(relative_data)
    prediction = triple_es.predict(model)
    return prediction + min_epoch


def detect_anomalies(
    data: pd.DataFrame,
    config: CustomParameters = CustomParameters(),
):
    set_random_state(config)

    ts = (
        MinMaxScaler(feature_range=(0.1, 1.1)).fit_transform(data).reshape(-1)
    )  # data must be > 0
    triple_es: TripleES = TripleES(
        ts,
        config.period,
        config.trend,
        config.seasonality,
    )
    res = triple_es.detect_anomalies()

    # Check for NaN values
    nan_mask = np.isnan(res)

    if True in nan_mask:
        # logger.debug("Could not detect anomalies with TripleES")
        return []
    else:
        return res
