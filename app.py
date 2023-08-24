# Import the dependencies.
from flask import Flask, jsonify
import datetime as dt
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
stations_db_url = 'sqlite:///hawaii_stations.db'
stations_engine = create_engine(stations_db_url)
stations_metadata = MetaData()
stations_base = automap_base(metadata=stations_metadata)
stations_base.prepare()

Station = stations_base.classes.station

measurements_db_url = 'sqlite:///hawaii_measurements.db'
measurements_engine = create_engine(measurements_db_url)
measurements_metadata = MetaData()
measurements_base = automap_base(metadata=measurements_metadata)
measurements_base.prepare()

Measurement = measurements_base.classes.measurement
# reflect the tables
stations_metadata.reflect(bind=stations_engine)
measurements_metadata.reflect(bind=measurements_engine)
# Save references to each table


# Create our session (link) from Python to the DB
stations_session = sessionmaker(bind=stations_engine)
stations_session_instance = stations_session()

measurements_session = sessionmaker(bind=measurements_engine)
measurements_session_instance = measurements_session()

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route('/')
def homepage():
    """Homepage route"""
    return (
        "Welcome to the API!<br>"
        "Available routes:<br>"
        "/ - Homepage<br>"
        "/api/v1.0/precipitation - Precipitation data for the last 12 months<br>"
        "/api/v1.0/stations - List of stations<br>"
        "/api/v1.0/tobs - Temperature observations for the last year<br>"
        "/api/v1.0/&lt;start&gt; - Minimum, average, and maximum temperatures from start date onwards<br>"
        "/api/v1.0/&lt;start&gt;/&lt;end&gt; - Minimum, average, and maximum temperatures for a date range"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    # Calculate the date one year ago from the last date in the database
    last_date = measurements_session_instance.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query for precipitation data in the last 12 months
    results = measurements_session_instance.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    # Convert results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

@app.route('/api/v1.0/stations')
def stations():
    results = stations_session_instance.query(Station.station).all()
    station_list = list(np.ravel(results))

    return jsonify(station_list)

@app.route('/api/v1.0/tobs')
def tobs():
    # Calculate the date one year ago from the last date in the database
    last_date = measurements_session_instance.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query for temperature observations in the last 12 months from the most active station
    results = measurements_session_instance.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= one_year_ago).\
        filter(Measurement.station == 'your_most_active_station_id').all()

    tobs_data = {date: tobs for date, tobs in results}

    return jsonify(tobs_data)

@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def temperature_stats(start, end=None):
    # Query for temperature statistics based on the start and end dates
    if end:
        results = measurements_session_instance.query(func.min(Measurement.tobs),
                                                      func.avg(Measurement.tobs),
                                                      func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    else:
        results = measurements_session_instance.query(func.min(Measurement.tobs),
                                                      func.avg(Measurement.tobs),
                                                      func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
        
        stats = {
        "start_date": start,
        "end_date": end if end else "N/A",
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }

    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True)
