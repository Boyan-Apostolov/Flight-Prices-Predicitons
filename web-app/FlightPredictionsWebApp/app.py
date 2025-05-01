from flask import Flask, render_template, request
import joblib
import pandas as pd
from datetime import datetime
from logic import validate_input, prepare_prediction_inputs, predict_best_day

app = Flask(__name__)

AIRPORTS_DEPARTURE = ['Eindhoven', 'Sofia', 'İstanbul', 'New York']
AIRPORTS_ARRIVAL = ['Athens', 'Eindhoven',
                    'Amsterdam', 'Sofia', 'Washington, D.C.']

# Load model and encoders
model = joblib.load('models/flight_model.pkl')
le_dep = joblib.load('models/departure_encoder.pkl')
le_arr = joblib.load('models/arrival_encoder.pkl')


@app.route('/', methods=['GET', 'POST'])
def index():
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
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
        input_data = {
            "departure_airport": form['departure_airport'],
            "arrival_airport": form['arrival_airport'],
            "departure_date": datetime.strptime(form['departure_date'], '%Y-%m-%d'),
            "near_holiday": form['near_holiday'],
            "price": form['price']
        }

        # Update display values
        page_data.update({
            "price": input_data["price"],
            "departure_airport": input_data["departure_airport"],
            "arrival_airport": input_data["arrival_airport"],
            "departure_date": input_data["departure_date"].strftime('%Y-%m-%d'),
            "near_holiday": input_data["near_holiday"]
        })

        # Validate input
        error = validate_input(
            input_data, AIRPORTS_DEPARTURE, AIRPORTS_ARRIVAL)
        if error:
            page_data["error"] = error
            return render_template('index.html', page_data=page_data)

        # Build features and predict
        df, context = prepare_prediction_inputs(input_data, le_dep, le_arr)
        prediction, best_date_to_buy = predict_best_day(context, model)

        page_data.update({
            "prediction": prediction,
            "best_date_to_buy": best_date_to_buy
        })

    return render_template('index.html', page_data=page_data)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
