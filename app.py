import os

from flask import Flask, redirect, url_for, request, flash, json, render_template
from flask_sqlalchemy import SQLAlchemy
from shapely import wkb
from werkzeug.utils import secure_filename
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape

UPLOADED_FILES = './files'
ALLOWED_EXTENSIONS = {'csv', 'geojson', 'zip'}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissecret!'
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:password@localhost/geodata'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class AoiCoordinate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aoi = db.Column(db.String(50), nullable=False)
    coordinate = db.Column(Geometry('POLYGON'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        aoi = request.form.get('aoi')
        file = request.files['coordinate']
        read_file = file.read()
        file_json = json.loads(read_file)
        aoi_coordinate = file_json["features"][0]['geometry']
        coordinate = AoiCoordinate(aoi=aoi, coordinate=json.dumps(aoi_coordinate))
        db.session.add(coordinate)
        db.session.commit()

        return aoi
    return render_template('index.html')


@app.route('/all')
def all_coordinate():
    coordinates = AoiCoordinate.query.all()

    all_cord = []
    for location in coordinates:
        location_coordinate = to_shape(location.coordinate)
        location_aoi = location.aoi
        location = {
            'location_coordinate': location_coordinate,
            'location_aoi': location_aoi
        }
        all_cord.append(location)

    return render_template('all.html', all_coordinates=all_cord)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port="5000", debug=True)
