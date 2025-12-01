import os
from flask import Flask, request, render_template, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

# ===== MongoDB Atlas Connection =====
MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI environment variable is not set")

# standard MongoClient – Atlas Python URI handles TLS for us
client = MongoClient(MONGO_URI)

db = client["hw3db"]
collection = db["flight_logs"]


@app.route("/")
def index():
    """Show the multi-entry flight log form and list stored flights."""
    flights = list(collection.find())

    # Compute total logged time from numeric field
    total_hours = 0.0
    for f in flights:
        hours = f.get("flight_time_hours")
        if isinstance(hours, (int, float)):
            total_hours += hours

    return render_template("index.html",
                           flights=flights,
                           total_hours=round(total_hours, 2))


@app.route("/add", methods=["POST"])
def add():
    """
    Handle multi-row insert from the HTML form.
    Each row has date, aircraft, tail, flight_time, remarks.
    """
    dates = request.form.getlist("date")
    aircraft_types = request.form.getlist("aircraft")
    tail_numbers = request.form.getlist("tail")
    flight_times = request.form.getlist("flight_time")
    remarks_list = request.form.getlist("remarks")

    docs = []

    for i in range(len(dates)):
        date = dates[i].strip()
        ac_type = aircraft_types[i].strip()
        tail = tail_numbers[i].strip()
        ft_str = flight_times[i].strip()
        remark = remarks_list[i].strip()

        # Skip completely empty rows
        if not (date or ac_type or tail or ft_str or remark):
            continue

        # Parse flight time as float, if possible
        ft_hours = None
        if ft_str:
            try:
                ft_hours = float(ft_str)
            except ValueError:
                ft_hours = None

        doc = {
            "date": date,
            "aircraft_type": ac_type,
            "tail_number": tail,
            "flight_time": ft_str,          # original string
            "flight_time_hours": ft_hours,  # numeric version
            "remarks": remark
        }
        docs.append(doc)

    if docs:
        collection.insert_many(docs)

    return redirect(url_for("index"))


if __name__ == "__main__":
    # host=0.0.0.0 makes it reachable from Windows through localhost
    app.run(host="0.0.0.0", port=5000, debug=True)