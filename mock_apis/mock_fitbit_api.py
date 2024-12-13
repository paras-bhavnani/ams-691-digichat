from flask import Flask, jsonify
import pandas as pd
from datetime import datetime, timedelta
import random

app = Flask(__name__)

# Load the Fitbit-like dataset
# Replace 'path_to_your_dataset.csv' with the actual path to your dataset
df = pd.read_csv('mock_apis/FitBit Fitness Tracker Data/Fitabase Data 4.12.16-5.12.16/dailyActivity_merged.csv')

@app.route('/api/user/<user_id>/activities/date/<date>')
def get_user_activities(user_id, date):
    parsed_date = datetime.strptime(date, '%Y-%m-%d').strftime('%m/%d/%Y').lstrip('0')
    user_data = df[(df['Id'] == int(user_id)) & (df['ActivityDate'] == parsed_date)]
    if user_data.empty:
        return jsonify({'error': 'No data found'}), 404
    return jsonify(user_data.to_dict(orient='records')[0])

@app.route('/api/user/<user_id>/sleep/date/<date>')
def get_user_sleep(user_id, date):
    # Simulate sleep data
    sleep_data = {
        'totalMinutesAsleep': random.randint(300, 540),
        'totalTimeInBed': random.randint(360, 600)
    }
    return jsonify(sleep_data)

@app.route('/api/user/<user_id>/heart/date/<date>')
def get_user_heart_rate(user_id, date):
    # Simulate heart rate data
    heart_rate_data = {
        'restingHeartRate': random.randint(60, 80),
        'outOfRange': random.randint(100, 200),
        'fatBurn': random.randint(200, 300),
        'cardio': random.randint(50, 150),
        'peak': random.randint(10, 50)
    }
    return jsonify(heart_rate_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)