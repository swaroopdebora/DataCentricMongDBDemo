import json
import os
from flask import Flask, render_template, url_for, request, session, redirect
from datetime import datetime
from flask import Flask, json, redirect, render_template, request, session, url_for, flash, g
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import bcrypt

app = Flask(__name__)
app.secret_key = "randomstring123"
messages = []


app.config["MONGO_DBNAME"] = 'sample_airbnb_reservation'
app.config["MONGO_URI"] = 'mongodb+srv://root:RootUser@cluster0.yvawf.mongodb.net/sample_airbnb_reservation?retryWrites=true&w=majority'

mongo = PyMongo(app)


@app.route('/')
def index():
    return render_template("index.html", listings=mongo.db.listingsAndReviews.find(), new_list=[], new_country=[], new_suburb=[])


@app.route('/about')
def about():
    return render_template("about-us.html", page_title="Shop Online")


@app.route('/contact')
def contact():
    return render_template("contact-us.html", page_title="Shop Online")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'name': request.form['username']})
        if login_user:
            if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == login_user['password']:
                session['username'] = request.form['username']
                return redirect(url_for('viewlisting'))
        return 'Invalid username/password combination'
    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name': request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(
                request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert(
                {'name': request.form['username'], 'password': hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('login'))
        return 'That username already exists!'
    return render_template('register.html')


@app.route('/get_property_type')
def get_property_type():
    return render_template('get_property_type.html',
                           get_property_type=mongo.db.property_type.find())


@app.route('/addlisting')
def addlisting():
    return render_template("Ad-listing.html", listings=mongo.db.listingsAndReviews.find(),new_list=[])


@app.route('/adlistingform', methods=['POST'])
def adlistingform():
    listings = mongo.db.listingsAndReviews
    listings.insert_one(request.form.to_dict())
    return redirect(url_for('viewlisting'))


@app.route('/emailenquiry', methods=['POST'])
def emailenquiry():
    enquiry = mongo.db.emailenquiry
    enquiry.insert_one(request.form.to_dict())
    return render_template('index.html')


@app.route('/viewlisting')
def viewlisting():
    return render_template("ad-list-view.html",listings=mongo.db.listingsAndReviews.find(), new_list=[], new_country=[], page_title="View Listing")


@app.route('/edit_listing/<listing_id>')
def edit_listing(listing_id):
    the_listing = mongo.db.listingsAndReviews.find_one({"_id": ObjectId(listing_id)})
    return render_template('edit_listing.html', list=the_listing)


@app.route('/update_listing/<listing_id>', methods=["POST"])
def update_listing(listing_id):
    listingsAndReviews = mongo.db.listingsAndReviews
    listingsAndReviews.update({'_id': ObjectId(listing_id)},
    {
        'name': request.form.get('name'),
        'summary': request.form.get('summary'),
        'room_type': request.form.get('room_type'),
        'accommodates': request.form.get('accommodates'),
        'property_type': request.form.get('property_type'),
        'listing_url': request.form.get('listing_url'),
        'minimum_nights': request.form.get('minimum_nights'),
        'price': request.form.get('price'),
        'images_picture_url': request.form.get('images_picture_url'),
        'host_name': request.form.get('host_name'),
        'host_location': request.form.get('host_location')
    })
    return redirect(url_for('viewlisting'))


@app.route('/delete_listing/<listing_id>')
def delete_listing(listing_id):
    listingsAndReviews = mongo.db.listingsAndReviews
    listingsAndReviews.remove({'_id': ObjectId(listing_id)})
    return redirect(url_for('viewlisting'))


@app.route('/userprofile')
def userprofile():
    return render_template("user-profile.html", page_title="Shop Online")


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
