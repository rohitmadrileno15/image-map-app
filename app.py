from flask import Flask,redirect, url_for,render_template, request,session,flash,request
import os
from PIL import Image
from flask_sqlalchemy import SQLAlchemy
import geocoder,requests,json
from flask_wtf import FlaskForm
from flask_wtf.file import FileField , FileAllowed
from wtforms import StringField , PasswordField,SubmitField
from wtforms.validators import DataRequired,Length, Email , EqualTo, ValidationError
from flask import jsonify
from check_script import get_data
from get_geo_data import geo_data_of_distance
from map_func import mainfunc
import random
import string

app = Flask(__name__)

app.config['SECRET_KEY'] = '450933c08c5ab75e79619102eddf47dee813a9d6'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

app.jinja_env.filters['zip'] = zip

db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer,primary_key= True)
    caption_ = db.Column(db.String(100), nullable = False)
    image_latitude = db.Column(db.String(100), nullable = False)
    image_longitude = db.Column(db.String(100), nullable = False)

    image_pic = db.Column(db.String(300), nullable = False)

    def __repr__(self):
        a=f"Post('{self.image_longitude}' , '{self.image_latitude}' )"
        return a


class UploadForm(FlaskForm):
    caption_field = StringField('Caption' , validators=[DataRequired()])
    image_url = FileField('Image File' , validators = [DataRequired()])
    submit = SubmitField ("Upload")



def save_picture(form_picture):
    
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(20)))
     
    hashed_caption = result_str
    f_name , f_ext = os.path.splitext(form_picture.filename)
    fn = hashed_caption+f_name
    picture_fn = fn + f_ext
    picture_path = os.path.join(app.root_path , 'static' , picture_fn)
    print(picture_fn)
    i = Image.open(form_picture)

    # width_ = i.size[0]
    # height_ = i.size[1]
    # aspect_ratio = float(width_ / height_)
    # new_height = float(1080 * aspect_ratio)

    # i = i.resize((1080, 450))

    i.save(picture_path)
    # form_picture.save(picture_path)
    return picture_fn




@app.route('/')
def home():

    return render_template('index.html')

@app.route('/upload', methods = ["GET" ,  "POST"] )
def upload():
    form = UploadForm()

    if (form.validate_on_submit()):
        img = form.image_url.data
        picture_file = save_picture(form.image_url.data)
        print("done")
        image_link_in_server = "static/" + picture_file
        map_results = get_data(image_link_in_server)
        if(map_results != "ERROR"):
            image_longitude = map_results.split(",")[1]
            image_latitude = map_results.split(",")[0]
            image_caption = form.caption_field.data
            newFile = Post(caption_  = image_caption ,image_longitude = image_longitude , image_latitude = image_latitude, image_pic = picture_file )
            db.session.add(newFile)
            db.session.commit()
            return "<div> <h1> DONE! <br>  <a href='/images_with_map'> See the map? </a> or <a href='/'> Go to home </a> </h1> </div>"
        else:
            image_caption = form.caption_field.data
            return render_template('mapNew.html', imagefilename = picture_file , imagecaption = image_caption )

    else:
        return render_template('upload.html', form = form )


@app.route('/linked_upload', methods = ["GET" ,  "POST"] )
def linked_upload():
    if(request.method == "POST"):
        print("post req")
        lat_value = request.form['lat_form'] 
        long_value = request.form['long_form'] 
        picture_name =  request.form['picture_name']
        image_caption = request.form['image_caption']
        newFile = Post(caption_  = image_caption ,image_longitude = long_value , image_latitude = lat_value, image_pic = picture_name )
        db.session.add(newFile)
        db.session.commit() 
        return "Uploaded"



@app.route('/images_with_map', methods=['GET', 'POST'])
def images_with_map():

    geo_data_info = Post.query.all()

    greet = "No images have been uploaded yet! Try uploading some!"
    print( "geo_data_info" , geo_data_info)
    if(len(geo_data_info) == 0):
        return render_template("getDistance.html" , data_alert = greet )


    empty_data_arr = []
    route_data = []

    if(request.method == 'POST'):
        def_lat = float(request.form.get("textlat"))

        def_long = float(request.form.get("textlon"))

        r = requests.get(url = f"https://api.opencagedata.com/geocode/v1/json?q={def_lat}+{def_long}&key=ba461a1ba3eb43dab95f73e5e684cd23" ) 
        get_city_user =  r.json()

        try:           
            initial_user_value = get_city_user['results'][0]['components']['county']
        except:
            initial_user_value = "local"

        distance = int(request.form.get("cars"))
        print("distance" , distance)
        def_data = [def_lat , def_long , distance * 1000]

        county_array = []
        for row in geo_data_info:
            print("")
            lat1= (row.image_latitude)
            long1 = (row.image_longitude)
             # print(lat1)
             # print(long1)
     
            displacement = geo_data_of_distance( float(def_lat) , float(def_long) , float(lat1) , float(long1) )
            print("displacement ",  displacement) 
            

            if (distance > displacement or distance == displacement):

                r = requests.get(url = f"https://api.opencagedata.com/geocode/v1/json?q={lat1}+{long1}&key=ba461a1ba3eb43dab95f73e5e684cd23" ) 
                get_city =  r.json()
                try:
                    county_value = get_city['results'][0]['components']['county']
                    county_array.append(county_value)
                    print("county_value" , county_value)

                    user_route_link = f"https://www.mapquestapi.com/directions/v2/route?key=UbH7DkjS05mBLP5lrTcqEiAGtsvq7tA6&from={initial_user_value}&to={county_value}&outFormat=json&ambiguities=ignore&routeType=fastest&doReverseGeocode=false&enhancedNarrative=false&avoidTimedConditions=false"
                    route_data.append(user_route_link)

                except:
                    county_array.append("local")
                    print("except" , county_array)
                    route_data.append("invalid")

                 
                print("appended" )
                empty_data_arr.append(row)

            print(empty_data_arr)
            print(county_array)
        return render_template('map.html' ,route_data = route_data , initial_user_value = initial_user_value ,  def_data = def_data , data_value_all_maps = empty_data_arr , county_array = county_array )

    return render_template("getDistance.html" )


@app.route('/success')
def success():
    return render_template("authenticity.html" )

@app.route('/admin')
def admin():
    all_vals = Post.query.all()
    return render_template("admin.html" , all_values = all_vals )

@app.errorhandler(404)
def not_found(e):
    return render_template("404error.html")


if __name__ == '__main__':
    app.run(debug= True)
