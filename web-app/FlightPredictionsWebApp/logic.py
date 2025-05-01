import pandas as pd
from datetime import datetime, timedelta
import csv


def load_distances(filename="models/distances.csv"):
    distances = {}
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = tuple(sorted([row["departure"], row["arrival"]]))
            distances[key] = int(row["distance"])
    return distances


DISTANCES = load_distances()


def get_distance(dep, arr):
    if dep == arr:
        return 0
    return DISTANCES.get(tuple(sorted([dep, arr])), None)


def validate_input(data, dep_options, arr_options):
    if data['departure_airport'] == data['arrival_airport']:
        return "Departure and arrival airports must be different."

    if data['departure_date'].date() <= datetime.today().date():
        return "Departure date must be in the future."

    return None


def prepare_prediction_inputs(data, le_dep, le_arr):
    today = datetime.today()
    departure_date = data['departure_date']
    price = float(data['price'])

    near_holiday = data['near_holiday']
    dep_airport = data['departure_airport']
    arr_airport = data['arrival_airport']

    distance = get_distance(dep_airport, arr_airport)

    features = {
        'price': price,
        'airport_distance_km': distance,
        'near_holiday_-1.0': int(near_holiday == '-1'),
        'near_holiday_0.0': int(near_holiday == '0'),
        'near_holiday_1.0': int(near_holiday == '1'),
        'departure_airport': le_dep.transform([dep_airport])[0],
        'arrival_airport': le_arr.transform([arr_airport])[0],
        'daysAgo': (departure_date - today).days,
        'departure_weekday': departure_date.weekday()
    }

    return pd.DataFrame([features]), {
        "price": price,
        "dep_airport_encoded": features["departure_airport"],
        "arr_airport_encoded": features["arrival_airport"],
        "flight_date": departure_date,
        "today_date": today,
        "distance": distance,
        "holiday_flags": {
            -1.0: features["near_holiday_-1.0"],
            0.0: features["near_holiday_0.0"],
            1.0: features["near_holiday_1.0"]
        }
    }


def generate_feature_vector(ctx, candidate_purchase_date):
    daysAgo = (ctx["flight_date"] - candidate_purchase_date).days
    departure_weekday = ctx["flight_date"].weekday()
    return [
        ctx["price"],
        ctx["distance"],
        ctx["holiday_flags"].get(-1.0, 0),
        ctx["holiday_flags"].get(0.0, 0),
        ctx["holiday_flags"].get(1.0, 0),
        ctx["dep_airport_encoded"],
        ctx["arr_airport_encoded"],
        daysAgo,
        departure_weekday
    ]


def predict_best_day(ctx, model):
    best_daysAgo = None
    best_prediction = float('inf')
    days_until_flight = (ctx["flight_date"] - ctx["today_date"]).days

    for daysAgo_candidate in range(days_until_flight, -1, -1):
        candidate_purchase_date = ctx["flight_date"] - \
            timedelta(days=daysAgo_candidate)

        if candidate_purchase_date < ctx["today_date"]:
            continue

        features = generate_feature_vector(ctx, candidate_purchase_date)
        prediction_candidate = model.predict([features])[0]

        if prediction_candidate < best_prediction:
            best_prediction = prediction_candidate
            best_daysAgo = daysAgo_candidate

    if best_daysAgo is None:
        return None, None

    best_date = ctx["flight_date"] - timedelta(days=best_daysAgo)
    return best_prediction, best_date.strftime('%d-%m-%Y')
