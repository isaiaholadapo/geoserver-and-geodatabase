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
app.config['UPLOADED_FILES'] = UPLOADED_FILES

db = SQLAlchemy(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    all_coordinates = AoiCoordinate.query.all()
    # for coordinate in all_coordinates:
    #     coordinate = wkb.loads(coordinate, hex=True)
    #     print(coordinate)
    all_cord = []
    for location in all_coordinates:
        location_coordinate = to_shape(location.coordinate)
        location_aoi = location.aoi
        location = {
            'coordinate': location_coordinate,
            'location_aoi': location_aoi
        }
        all_cord.append(location)
        print(location)

    return render_template('all.html', all_coordinat=all_cord)

@app.route('/test', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Please select a file')
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOADED_FILES'], filename))

            return redirect(url_for('download_file', name=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/download_file', methods=['GET'])
def download_file():
    return 'done'



if __name__ == "__main__":
    app.run(host="127.0.0.1", port="5000", debug=True)
