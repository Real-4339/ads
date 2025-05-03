import warnings
import numpy as np

from statsmodels.tsa.holtwinters.model import ExponentialSmoothing, HoltWintersResults
from statsmodels.tools.sm_exceptions import ConvergenceWarning


warnings.simplefilter("ignore", ConvergenceWarning)
warnings.simplefilter("ignore", RuntimeWarning)


class TripleES:
    def __init__(
        self,
        ts: np.ndarray,
        period: int,
        trend: str,
        seasonality: str,
        use_boxcox: bool = True,
    ):
        self.ts = ts
        assert (
            len(ts) >= 10 + period
        ), """Cannot use heuristic method to compute initial seasonal and levels with less than periods + 10 datapoints."""
        self.trend = trend
        self.seasonality = seasonality
        self.seasonal_periods = period
        self.use_boxcox = use_boxcox

    def fit(self, X) -> HoltWintersResults:
        model = ExponentialSmoothing(
            X,
            trend=self.trend,
            use_boxcox=self.use_boxcox,
            initialization_method="estimated",
        )
        return model.fit()

    def predict(self, model: HoltWintersResults, predict_points=1) -> np.float64:
        return model.forecast(predict_points)[0]
