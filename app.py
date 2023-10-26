from werkzeug.middleware.proxy_fix import ProxyFix
import csv
import schedule
import time
from flask import Flask, render_template

app = Flask(__name__)
app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

# Function to determine the Haze color class based on the Haze number
def haze_color(haze_number):
    if haze_number < 50:
        return 'light-green'
    elif 50 <= haze_number < 100:
        return 'blue'
    elif 100 <= haze_number < 200:
        return 'orange'
    elif 200 <= haze_number < 300:
        return 'red'
    else:
        return 'dark-red'

# Function to read the last 4 rows from the CSV file
def read_csv_data():
    data = []
    with open('/home/adwilson99/scripts/haze/haze.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        rows = list(csv_reader)[-4:]  # Get the last 4 rows
        for row in rows:
            data.append({
                'HazeNumber': int(row['Haze']),
                'Hour': row['Hour'],
                'Date': row['Date'],
                'Message': row['Message']
            })
    return data

# Custom context processor to make haze_color available to templates
@app.context_processor
def inject_functions():
    return dict(haze_color=haze_color)

# Function to update data periodically (every hour)
def update_data():
    global air_quality_data
    air_quality_data = read_csv_data()

# Initial data read
air_quality_data = read_csv_data()

# Schedule data update every hour
schedule.every(1).hour.do(update_data)

# Start the scheduler in a separate thread
def schedule_run():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    from threading import Thread
    scheduler_thread = Thread(target=schedule_run)
    scheduler_thread.start()

    @app.route('/haze')
    def dashboard():
        return render_template('dashboard.html', data=air_quality_data)

    app.run(debug=True)

