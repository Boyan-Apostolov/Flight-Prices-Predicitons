from flask import Flask, render_template, request
import joblib
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# ✅ Load model and encoders from 'models/' folder
model = joblib.load('models/flight_model.pkl')
le_dep = joblib.load('models/departure_encoder.pkl')
le_arr = joblib.load('models/arrival_encoder.pkl')


@app.route('/', methods=['GET', 'POST'])
def index():
    prediction = None
    today = datetime.today().strftime('%Y-%m-%d')
    if request.method == 'POST':
        price = float(request.form['price'])
        dep_airport = request.form['departure_airport']
        arr_airport = request.form['arrival_airport']
        departure_date = request.form['departure_date']
        record_date = request.form['record_date']
        near_holiday = request.form['near_holiday']  # -1, 0, 1

        # ✨ Feature Engineering
        departure_date = datetime.strptime(departure_date, '%Y-%m-%d')
        record_date = datetime.strptime(record_date, '%Y-%m-%d')
        daysAgo = (departure_date - record_date).days
        departure_date_unix = int(departure_date.timestamp())
        weekday = departure_date.weekday()

        features = {
            'price': price,
            'airport_distance_km': 1750,  # static or you can calculate
            'near_holiday_-1.0': int(near_holiday == '-1'),
            'near_holiday_0.0': int(near_holiday == '0'),
            'near_holiday_1.0': int(near_holiday == '1'),
            'departure_airport': le_dep.transform([dep_airport])[0],
            'arrival_airport': le_arr.transform([arr_airport])[0],
            'daysAgo': daysAgo,
            'departure_date_unix': departure_date_unix,
            'departure_weekday': weekday
        }

        df = pd.DataFrame([features])
        prediction = model.predict(df)[0]

    return render_template('index.html', today=today, prediction=prediction)


# ✅ Optional: run on port 5000
if __name__ == '__main__':
    app.run(debug=True, port=5000)
