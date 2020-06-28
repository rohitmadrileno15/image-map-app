from flask import Flask,redirect, url_for,render_template, request,session,flash,request
import os,secrets
from flask_sqlalchemy import SQLAlchemy
import geocoder,requests,json
from flask_wtf import FlaskForm
from flask_wtf.file import FileField , FileAllowed
from wtforms import StringField , PasswordField,SubmitField
from wtforms.validators import DataRequired,Length, Email , EqualTo, ValidationError
from flask import jsonify
from check_script import get_data
from get_geo_data import geo_data_of_distance

app = Flask(__name__)

app.config['SECRET_KEY'] = '450933c08c5ab75e79619102eddf47dee813a9d6'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer,primary_key= True)

    image_latitude = db.Column(db.String(100), nullable = False)
    image_longitude = db.Column(db.String(100), nullable = False)

    image_pic = db.Column(db.String(300), nullable = False)

    def __repr__(self):
        a=f"Post('{self.image_longitude}' , '{self.image_latitude}' )"
        return a


class UploadForm(FlaskForm):
    image_url = FileField('Image File' , validators = [DataRequired()])
    submit = SubmitField ("Upload")



def save_picture(form_picture):
    hashed_caption = secrets.token_hex(16)
    f_name , f_ext = os.path.splitext(form_picture.filename)
    fn = hashed_caption+f_name
    picture_fn = fn + f_ext
    picture_path = os.path.join(app.root_path , 'static' , picture_fn)
    form_picture.save(picture_path)
    return picture_fn




@app.route('/')
def home():

    return render_template('index.html')

@app.route('/upload', methods = ["GET" ,  "POST"] )
def upload():
    form = UploadForm()
    print("1")

    if (form.validate_on_submit()):
        print("2")
        img = form.image_url.data
        picture_file = save_picture(form.image_url.data)
        print("done")
        image_link_in_server = "static/" + picture_file
        map_results = get_data(image_link_in_server)
        if(map_results != "ERROR"):
            image_longitude = map_results.split(",")[1]
            image_latitude = map_results.split(",")[0]
            newFile = Post(image_longitude = image_longitude , image_latitude = image_latitude, image_pic = picture_file )
            db.session.add(newFile)
            db.session.commit()
            return "<h1> DONE! <br>  <a href='/'> Go to home </a> </h1>"
        else:
            return "<h1> CHECK IMAGE! UPLOAD IMAGES DIRECTLY TAKEN FROM YOUR PHONE AND NOT THE ONES SHARED ON SOCIAL MEDIA. THIS IS DONE AS FOR MAINTAINING AUTHENTICITY! </h1>"

    else:
        return render_template('upload.html', form = form )




@app.route('/images_with_map', methods=['GET', 'POST'])
def images_with_map():


    # print()
    #
    # import requests
    # import json
    # print("UI")
    # print(request.environ['REMOTE_ADDR'])
    #
    # url = "http://ip-api.com/json/" + request.environ['REMOTE_ADDR']
    # # url = f"http://ip-api.com/json/157.40.199.29"
    # print(url)
    # response = requests.get(url)
    # print((response.text))
    # get_tex = (response.text)
    # res = json.loads(get_tex)
    #
    # # print (res['latitude'])
    # # print (res['longitude'])


    geo_data_info = Post.query.all()


    empty_data_arr = []

    if(request.method == 'POST'):
        def_lat = float(request.form.get("textlat"))

        def_long = float(request.form.get("textlon"))


        print(def_lat)
        print(def_long)
        def_data = [def_lat , def_long]
        distance = int(request.form.get("cars"))
        print("distance" , distance)


        for row in geo_data_info:
             print("")
             lat1= (row.image_latitude)
             long1 = (row.image_longitude)
             # print(lat1)
             # print(long1)
             displacement = geo_data_of_distance( float(def_lat) , float(def_long) , float(lat1) , float(long1) )
             print(displacement)

             if (distance > displacement or distance == displacement):
                 print("appended")
                 empty_data_arr.append(row)

             print(empty_data_arr)
             return render_template('map.html' , def_data = def_data , data_value_all_maps = empty_data_arr )

    return render_template("getDistance.html" )

@app.errorhandler(404)
def not_found(e):
    return render_template("404error.html")


if __name__ == '__main__':
    app.run(debug= True)
