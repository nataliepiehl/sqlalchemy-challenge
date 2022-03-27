# Import packages
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# ---------------------------------------------------
# Database Setup

# Create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
print(Station)

# ---------------------------------------------------
# Flask Setup
app = Flask(__name__)

# ---------------------------------------------------
# Flask Routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query date and prcp
    results = session.query(Measurement.date, Measurement.prcp).all()

    # Close session
    session.close()

    # Convert list of tuples into dictionary
    date_prcp = dict(results)
    print(date_prcp)

    return jsonify(date_prcp)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Identify most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.id)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.id).desc()).limit(1)[0][0]

    # Identify date one year from most recent
    one_year_date = dt.date(2017, 8, 23) - dt.timedelta(days = 365)

    # Query most activate station data
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_date).all()

    # Close session
    session.close()

    return jsonify([tup[1] for tup in results])


@app.route("/api/v1.0/<start>")
def time_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query data past given date
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= start).\
        with_entities(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).all()

    # Close session
    session.close()

    return jsonify(results)


@app.route("/api/v1.0/<start>/<end>")
def time_start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query data past start date and before end date
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).\
        with_entities(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).all()

    # Close session
    session.close()

    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
