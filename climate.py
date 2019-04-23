import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# Define what to do when a user hits the index route 
@app.route("/")
def home():
    return (
        f"Home page<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2016-08-23<br/>"
        f"/api/v1.0/2016-08-23/2017-08-23"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a Dictionary of date and prcp"""
    # Query all data
    results = session.query(Measurement.date, Measurement.prcp).\
        order_by(Measurement.date).all()

    # Create a dictionary from the row data and append to a list of all_precipitation
    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all stations"""
    # Query all stations
    results = session.query(Station.name).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """query for the dates and temperature observations from a year from the last data point"""
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    for date in last_date:
        split_last_date=date.split('-')
    last_year=int(split_last_date[0])
    last_month=int(split_last_date[1])
    last_day=int(split_last_date[2])

    query_date = dt.date(last_year, last_month, last_day) - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= query_date).order_by(Measurement.date).all()
    
    # Create a dictionary from the row data and append to a list of year_tobs
    year_tobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        year_tobs.append(tobs_dict)

    # Return a JSON list of Temperature Observations (tobs) for the previous year
    return jsonify(year_tobs)

@app.route("/api/v1.0/<start>")
def start_date(start):
    """query TMIN, TAVG, and TMAX for all dates greater than and equal to the start date
        start (string): A date string in the format %Y-%m-%d"""

    tem = [func.min(Measurement.tobs), 
            func.avg(Measurement.tobs), 
            func.max(Measurement.tobs)]
    results = session.query(*tem).\
        filter(Measurement.date >= start).all()
    tem_calc = list(np.ravel(results))
   
    return jsonify(tem_calc)
   
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    """query TMIN, TAVG, and TMAX for for dates between the start and end date inclusive
    start (string): A date string in the format %Y-%m-%d
    end (string): A date string in the format %Y-%m-%d"""

    tem = [func.min(Measurement.tobs), 
            func.avg(Measurement.tobs), 
            func.max(Measurement.tobs)]
    results = session.query(*tem).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    tem_calc = list(np.ravel(results))
   
    return jsonify(tem_calc)
    

# if not debug=True, anytime we make changes, we have to control+c to quit and rerun it
if __name__ == "__main__":
    app.run(debug=True)
