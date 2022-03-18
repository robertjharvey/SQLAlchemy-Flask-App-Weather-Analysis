import numpy as np 
import sqlalchemy
from sqlachemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#Database Setup 
engine = create_engine("sqlite:///Resources/Hawaii")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

#Flask Setup
app = Flask(__name__)

#Flask Routes
    #Home page
    #List all routes that are available
def welcome():
    """List all available api routes."""
    return (
        f"SQL-Alchemy API Homepage<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]/[end_date format:yyyy-mm-dd]<br/>"
    )

# /api/v1.0/precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    # Convert the query results to a dictionary using date as the key and prcp as the value
    results = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date).all()
    prcp_list = []
    for date,prcp  in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        prcp_list.append(prcp_dict)
    
    session.close()

    #Return the JSON representation of your dictionary
    return jsonify(prcp_list)

# /api/v1.0/stations
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    #Return a JSON list of stations from the dataset
    results = session.query(Station.station).order_by(Station.station).all()
    station_list = list(np.ravel(results))
    session.close()
    return jsonify(station_list)

# /api/v1.0/tobs
def tobs():
    session = Session(engine)

    #Query the dates and temperature observations of the most active station for the last year of data
    results = session.query(Measurement.date, Measurement.tobs, Measurement.prcp).filter(Measurement.date >= '2016-08-23').\
                filter(Measurement.station == 'USC00519281').order_by(Measurement.date).all()
    # Return a JSON list of temperature observations (TOBS) for the previous year
    tobs_list = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict[date] = tobs
        tobs_list.append(tobs_dict)
    
    session.close()
    return jsonify(tobs_list)

# /api/v1.0/<start>
def temp_start(start):
    session = Session(engine)

    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    starttemp_list = []

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start).all()

    for min, avg, max in results:
        start_list = {}
        start_list["MIN"] = min
        start_list["AVG"] = avg
        start_list["MAX"] = max
        start_list.append(start_list)
        
    session.close()
    return jsonify(start_list)

# /api/v1.0/<start> and /api/v1.0/<start>/<end>
def temp_all(start,end):
    session = Session(engine)
    
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive
    tempall_list = []
    for min, avg, max in results:
        temp_list = {}
        temp_list["TMIN"] = min
        temp_list["TAVG"] = avg
        temp_list["TMAX"] = max
        tempall_list.append(temp_list)

        session.close()
        return jsonify(tempall_list)

