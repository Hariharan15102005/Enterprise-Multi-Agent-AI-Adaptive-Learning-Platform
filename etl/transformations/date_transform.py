import pandas as pd
from datetime import date, timedelta

BRAZIL_HOLIDAYS = {
    # 2016
    "2016-01-01": "Confraternização Universal (Ano Novo)",
    "2016-04-21": "Tiradentes",
    "2016-05-01": "Dia do Trabalho",
    "2016-09-07": "Independência do Brasil",
    "2016-10-12": "Nossa Senhora Aparecida",
    "2016-11-02": "Finados",
    "2016-11-15": "Proclamação da República",
    "2016-11-25": "Black Friday Brasil 2016",
    "2016-12-25": "Natal",
    # 2017
    "2017-01-01": "Confraternização Universal (Ano Novo)",
    "2017-04-21": "Tiradentes",
    "2017-05-01": "Dia do Trabalho",
    "2017-09-07": "Independência do Brasil",
    "2017-10-12": "Nossa Senhora Aparecida",
    "2017-11-02": "Finados",
    "2017-11-15": "Proclamação da República",
    "2017-11-24": "Black Friday Brasil 2017",
    "2017-12-25": "Natal",
    # 2018
    "2018-01-01": "Confraternização Universal (Ano Novo)",
    "2018-04-21": "Tiradentes",
    "2018-05-01": "Dia do Trabalho",
    "2018-09-07": "Independência do Brasil",
    "2018-10-12": "Nossa Senhora Aparecida",
    "2018-11-02": "Finados",
    "2018-11-15": "Proclamação da República",
    "2018-11-23": "Black Friday Brasil 2018",
    "2018-12-25": "Natal"
}

def generate_date_dimension(start_date: str = "2016-01-01", end_date: str = "2019-12-31") -> pd.DataFrame:
    """
    Generates a comprehensive fiscal/calendar date dimension table.
    """
    dt_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    records = []
    for dt in dt_range:
        d_str = dt.strftime("%Y-%m-%d")
        holiday = BRAZIL_HOLIDAYS.get(d_str, None)
        
        records.append({
            'date_key': int(dt.strftime("%Y%m%d")),
            'full_date': dt.date(),
            'year': dt.year,
            'quarter': dt.quarter,
            'month': dt.month,
            'month_name': dt.strftime("%B"),
            'week_of_year': int(dt.strftime("%W")),
            'day_of_month': dt.day,
            'day_of_week': dt.dayofweek + 1, # 1 = Monday, 7 = Sunday
            'day_name': dt.strftime("%A"),
            'is_weekend': dt.dayofweek in [5, 6],
            'is_holiday_br': holiday is not None,
            'holiday_name': holiday
        })

    return pd.DataFrame(records)
