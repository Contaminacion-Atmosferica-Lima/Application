from src.data_loader import load_clean_data, latest_date, slice_by_date

CSV_PATH = "data/dataset.csv"

def test_load_clean_data():
    df = load_clean_data(CSV_PATH)

    assert not df.empty
    assert "distrito" in df.columns
    assert "fecha" in df.columns
    assert "latitud" in df.columns
    assert "longitud" in df.columns
    assert "pm2_5" in df.columns

def test_latest_date():
    df = load_clean_data(CSV_PATH)
    d = latest_date(df)
    assert d is not None

def test_slice_by_date():
    df = load_clean_data(CSV_PATH)
    d = str(latest_date(df))
    df_day = slice_by_date(df, d)

    assert not df_day.empty
    assert all(df_day["fecha"] == d)
