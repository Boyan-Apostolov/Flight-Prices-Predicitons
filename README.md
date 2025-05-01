# ✈️ Flight Price Predictor

<p align="center">
  <img src="https://i.ibb.co/bxS53jh/SCR-20250425-oyxh.jpg" alt="Flight Price Logo" />
</p>

A machine learning-based system for predicting the **cheapest day to buy a flight ticket** based on historical flight price trends, departure dates, and holidays.
Project for ML&AI Semester 4 @ Fontys ICT, Netherlands

---

# 🛠 Built with:

- Python 3
- Jupyter Notebook
- Pandas, NumPy
- scikit-learn
- XGBoost
- Matplotlib & Seaborn
- Plotly
- Git & GitHub
- Google Flights (scraped data)
- Label & One-Hot Encoding
- Custom holiday feature engineering

---

# 🧠 Project Overview

This project aims to help travelers **save money** by predicting how many days in advance they should book a ticket to get the lowest price. It transforms raw flight data into a machine learning model capable of outputting the optimal booking window.

---

# 📊 Features

- Days before departure (`daysAgo`)
- Departure date & Unix timestamp
- Departure and arrival airports
- Holiday proximity indicators (before/during/after)
- Weekend indicator
- Distance between airports (km)

---

# 📘 Notebooks / Phases

| Phase                      | Description                                                            |
| -------------------------- | ---------------------------------------------------------------------- |
| **Provisioning**           | Data scraping, cleaning, and initial exploration                       |
| **Prediction Iteration 1** | Switched from classification to regression, added more features        |
| **Prediction Iteration 2** | Tried KNN and Linear Regression, added timestamp                       |
| **Prediction Iteration 3** | Final model evaluation, feature refinement, added explainability tools |

---

# 🤖 Models Evaluated

| Model                    | Status    | Notes                                                 |
| ------------------------ | --------- | ----------------------------------------------------- |
| K-Nearest Neighbors      | ✅ Tested | Worked poorly for classification                      |
| Linear Regression        | ✅ Used   | High R² = suspiciously perfect, possible data leakage |
| Random Forest Regression | ✅ Tested | Good for tabular data, used for final iteration       |

---

# 📏 Evaluation Metrics

- **Mean Absolute Error (MAE)**
- **Root Mean Squared Error (RMSE)**
- **R² Score**

Comparisons were done between training and test sets to detect overfitting and ensure generalization.

---

# 📈 Visuals & Explainability

- Correlation heatmaps
- Time series plots
- Distribution of prices and days
- SHAP values _(planned/future work)_

<p align="center">
  <img src="https://i.ibb.co/5WXk1KXT/comparison.png" alt="Comparison Models"/>
</p>

---

# 👤 Stakeholders

- **Kalina Bacheva** – Traveler looking for deals
- **Tanya Apostolova** – Parent seeking affordable options

---

# 🌐 Deployment Plans

- Web app interface where users input:
  - Departure & arrival airports
  - Date of travel
  - Preferred flexibility window
- The app will predict:
  - Best date to purchase
  - Expected price range

---

# ⚖️ Ethics & Data Use

- All data collected complies with legal scraping policies.
- No personal information is stored or used.
