import pandas as pd
import numpy as np

from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


engine = create_engine("sqlite:///Resources/hawaii.sqlite?check_same_thread=False")

# Create our session (link) from Python to the DB
session = Session(engine)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

#### Routes
# Mainpage:

@app.route("/")
def default():
    """List all available api routes."""
    return (
        f"For Last 12 Months Precipitation Data:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"For List of All Stations:<br/>"
        f"/api/v1.0/stations<br/>"
        f"For Last 12 Months Temperature Data:<br/>"
        f"/api/v1.0/tobs<br/>"
        f"For Minimum, Average, and Maximum Temperature Calculated From Start Point to End of Data:<br/>"
        f"After pasting the following URL, enter a start date with a four number year, two number month and two number day: <br/>"
        f"/api/v1.0/<start_date><br/>"
        f"For Minimum, Average, and Maximum Temperature Calculated From Start Point to Specific End Point:<br/>"
        f"After pasting the following URL, enter a start date/end date (separated by the second forward slash),<br/>"
        f"each with a four number year, two number month and two number day: <br/>"
        f"/api/v1.0/<start_day>/<end_day>"
    )
# Save the query results as a Pandas DataFrame and set the index to the appropriate column:
data_12mo = session.query(Measurement.date, Measurement.tobs, Measurement.prcp).\
    filter(Measurement.date >= '2016-08-23').\
    order_by(Measurement.date).all()
data_12mo_df = pd.DataFrame(data_12mo, columns = ['Date', 'Temperature','Precipitation'])
data_12mo_df.set_index('Date', inplace = True)

station_info = session.query(Station.id, Station.station, Station.name).all()
station_info_df = pd.DataFrame(station_info, columns = ['Station ID','Station','Name'])
station_info_df .set_index('Station ID', inplace = True)

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Display dict of date:prcp values"""
    # Convert dataframe column to dict and jsonify

    precip_dict = data_12mo_df['Precipitation'].to_dict()

    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Display a list of all stations from the dataset"""
    # Convert to dict and jsonify

    station_info_dict = station_info_df.to_dict()
    
    return jsonify(station_info_dict)

@app.route("/api/v1.0/tobs")
def temperature():
    """Display the dates and temperature observations from a year from the last data point."""
    # Convert dataframe column to dict and jsonify

    temp_dict = data_12mo_df['Temperature'].to_dict()

    return jsonify(temp_dict)

@app.route("/api/v1.0/<start_date>")
def start_calc_temps(start_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    start_date = start_date.replace(" ", "-")
    if start_date >= '2010-01-01' and start_date <= '2017-08-23':
        output = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).filter(Measurement.date <= '2017-08-23').all()
        temperatures = output[0]

        return jsonify([temperatures[0],temperatures[1],temperatures[2]])

    else:
        return jsonify({"ERROR": f"Temperature data from date: {start_date} not found."}), 404
    

@app.route("/api/v1.0/<start_day>/<end_day>")
def start_to_end_temps(start_day, end_day):

    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_day (string): A date string in the format %y-%m-%d
        end_day (string): A date string in the format %y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    start_day = start_day.replace(" ", "-")
    if start_day >= '2010-01-01' and start_day <= '2017-08-23' and end_day >=  '2010-01-01'  and end_day <= '2017-08-23':
        output = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_day).filter(Measurement.date <= end_day).all()
        temperatures = output[0]

        return jsonify([temperatures[0],temperatures[1],temperatures[2]])

    else:
        return jsonify({ f"ERROR: Temperature data from date: {start_day} to: {end_day} not found."}), 404


#### Last Config for Running App
if __name__ == '__main__':
    app.run(debug=True)