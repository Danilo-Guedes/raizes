from dataclasses import dataclass
import datetime
import pandas as pd


@dataclass
class DailyInfo:
    general_total: int
    in_place_meals: int
    in_place_delivery: int
    third_party_delivery: int
    top_7_sales_df: pd.DataFrame
    total_sales: float
