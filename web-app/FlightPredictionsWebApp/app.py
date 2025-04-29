from flask import Flask, render_template, request
import joblib
import pandas as pd
from datetime import datetime
import csv

app = Flask(__name__)

AIRPORTS_DEPARTURE = ['Eindhoven', 'Sofia', 'İstanbul', 'New York']
AIRPORTS_ARRIVAL = ['Athens', 'Eindhoven',
                    'Amsterdam', 'Sofia', 'Washington, D.C.']

model = joblib.load('models/flight_model.pkl')
le_dep = joblib.load('models/departure_encoder.pkl')
le_arr = joblib.load('models/arrival_encoder.pkl')


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


def build_features(price, dep_airport, arr_airport, departure_date, near_holiday):
    today = datetime.today()
    return {
        'price': price,
        'airport_distance_km': get_distance(dep_airport, arr_airport),
        'near_holiday_-1.0': int(near_holiday == '-1'),
        'near_holiday_0.0': int(near_holiday == '0'),
        'near_holiday_1.0': int(near_holiday == '1'),
        'departure_airport': le_dep.transform([dep_airport])[0],
        'arrival_airport': le_arr.transform([arr_airport])[0],
        'daysAgo': (departure_date - today).days,
        'departure_date_unix': int(departure_date.timestamp()),
        'departure_weekday': departure_date.weekday()
    }


@app.route('/', methods=['GET', 'POST'])
def index():
    today = datetime.today()
    page_data = {
        "price": '',
        "departure_airport": '',
        "arrival_airport": '',
        "departure_date": today.strftime('%Y-%m-%d'),
        "near_holiday": '-2',
        "today": today.strftime('%Y-%m-%d'),
        "prediction": None,
        "best_date_to_buy": None,
        "airports_departure": AIRPORTS_DEPARTURE,
        "airports_arrival": AIRPORTS_ARRIVAL,
        "error": None
    }

    if request.method == 'POST':
        form = request.form
        dep_airport = form['departure_airport']
        arr_airport = form['arrival_airport']
        departure_date_str = form['departure_date']
        near_holiday = form['near_holiday']
        price_str = form['price']
        departure_date = datetime.strptime(departure_date_str, '%Y-%m-%d')

        page_data.update({
            "price": price_str,
            "departure_airport": dep_airport,
            "arrival_airport": arr_airport,
            "departure_date": departure_date_str,
            "near_holiday": near_holiday
        })

        if dep_airport == arr_airport:
            page_data["error"] = "Departure and arrival airports must be different."
            return render_template('index.html', page_data=page_data)

        if departure_date.date() < today.date():
            page_data["error"] = "Departure date must be in the future."
            return render_template('index.html', page_data=page_data)

        distance = get_distance(dep_airport, arr_airport)
        if distance is None:
            page_data["error"] = f"No distance data available for {dep_airport} to {arr_airport}."
            return render_template('index.html', page_data=page_data)

        price = float(price_str)
        features = build_features(
            price, dep_airport, arr_airport, departure_date, near_holiday)
        df = pd.DataFrame([features])
        prediction = model.predict(df)[0]
        best_date_to_buy = (
            departure_date - pd.Timedelta(days=round(prediction))).strftime('%d-%m-%Y')

        page_data.update({
            "prediction": prediction,
            "best_date_to_buy": best_date_to_buy
        })

    return render_template('index.html', page_data=page_data)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
