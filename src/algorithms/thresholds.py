LEVELS = {
    "OMS": {
        "PM2_5": [15, 35, 55, 150],
        "PM10": [45, 75, 125, 250],
        "NO2": [25, 50, 100, 200],
        "AVG": [28, 53, 93, 200]
    },
    "MINAM": {
        "PM2_5": [25, 50, 75, 125],
        "PM10": [50, 100, 150, 300],
        "NO2": [100, 200, 300, 500],
        "AVG": [60, 115, 175, 300]
    },
}

COLORS = ["green", "yellow", "orange", "red", "purple"]

def classify_pollution(value, pollutant, mode="OMS"):
    thresholds = LEVELS[mode][pollutant.upper()]
    for i, limit in enumerate(thresholds):
        if value <= limit:
            return COLORS[i]
    return COLORS[-1]  # Peligrosa
