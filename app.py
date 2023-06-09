# Import the dependencies.
import numpy as np
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
the_engine=create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
e_db=automap_base()
# reflect the tables
e_db.prepare(the_engine, reflect=True)

# Save references to each table
Measure_ref=e_db.classes.measurement
Station_ref=e_db.classes.station

# Create our session (link) from Python to the DB
session_link=Session(the_engine)

#################################################
# Flask Setup
#################################################
app=Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return("Welcome to the 'Home' page")
#Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def percipitation():
    session_link=Session(the_engine)
    percipitation_results=session_link.query(Measure_ref.prcp,Measure_ref.date).all()
    session_link.close()

    percipt_val=[]
    for prcp,date in percipitation_results:
        prcp_dct={}
        prcp_dct["percipitation"]=prcp
        prcp_dct["date"]=date
        percipt_val.append(prcp_dct)
    return jsonify(percipt_val)
#return a json list of stations from the dataset
@app.route("/api/v1.0/stations")
def station():
    session_link=Session(the_engine)
    station_results=session_link.query(Station_ref.station, Station_ref.id).all()

    station_val=[]
    for station, id in station_results:
        station_dct={}
        station_dct["station"]=station
        station_dct["id"]=id
        station_val.append(station_dct)
    return jsonify (station_val)
#Query the dates and temperature observations of the most-active station for the previous year of data.

#Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    session_link=Session(the_engine)
    lastyr_temp=session_link.query(Measure_ref.date).\
        order_by(Measure_ref.date.desc()).first()
    print(lastyr_temp)
    Lastyr_val=[]
    for date in lastyr_temp:
        lastyr_dct={}
        lastyr_dct["date"]=date
        Lastyr_val.append(lastyr_dct)
    print(Lastyr_val)

    qstartd=dt.date(2017,8,23)-dt.timedelta(days=365)
    print(qstartd)
    active_stations=session_link.query(Measure_ref.station, func.count(Measure_ref.station)).\
        order_by(func.count(Measure_ref.station).desc()).\
        group_by(Measure_ref.station).first()
    stations_most_active=active_stations[0]
    session_link.close()
    print(stations_most_active)

    tobs_date=session_link.query(Measure_ref.date, Measure_ref.tobs, Measure_ref.station).\
        filter(Measure_ref.date >qstartd).\
        filter(Measure_ref.station ==stations_most_active).all()
    tobs_date_val=[]
    for date, tobs, station in tobs_date:
        tobs_date_dct={}
        tobs_date_dct["date"]=date
        tobs_date_dct["tobs"]=tobs
        tobs_date_dct["station"]=station
        tobs_date_val.append(tobs_date_dct)
    return jsonify(tobs_date_val)
@app.route("/api/v1.0/<start>")
def start_date(start):
    session_link=Session(the_engine)
    tobs_start_d=session_link.query(func.min(Measure_ref.tobs), func.avg(Measure_ref.tobs), func.max(Measure_ref.tobs)).\
        filter(Measure_ref.date >=start).all()
    session_link.close()

    tobs_start_val=[]
    for min, avg, max in tobs_start_d:
        tobs_start_dct={}
        tobs_start_dct["min"]=min
        tobs_start_dct["average"]=avg 
        tobs_start_dct["max"]=max
        tobs_start_val.append(tobs_start_dct)
    return jsonify(tobs_start_val)
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session_link=Session(the_engine)

    tobs_start_end_d=session_link.query(func.min(Measure_ref.tobs), func.avg(Measure_ref.tobs), func.max(Measure_ref.tobs)).\
        filter(Measure_ref.date >=start).\
        filter(Measure_ref.date <= end).all()
    session_link.close()

    tobs_sne_v=[]
    for min, avg, max in tobs_start_end_d:
        s_e_dct={}
        s_e_dct["min_temp"]=min
        s_e_dct["avg_temp"]=avg
        s_e_dct["max_temp"]=max
        tobs_sne_v.append(s_e_dct)
    return jsonify(tobs_sne_v)
        
    
if __name__ == '__main__': # Run flask when the file is called
    app.run(host="0.0.0.0", port=5000)
