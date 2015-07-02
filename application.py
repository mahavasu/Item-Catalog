from flask import Flask, render_template, request, redirect
from flask import url_for, jsonify, flash

# setup sqlalchemy
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

#import statments
import httplib2
import json
import random
import string
from flask import make_response
import requests

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog"

app = Flask(__name__)
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

# flask functions
# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


#Function to connect third party gmail account
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials.access_token')
    stored_gplus_id = login_session.get('gplus_id')

    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.')
                                            , 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials.access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'
    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    print user_id
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1> '
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


#function to disconnect third party gmail account
@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    access_token = login_session.get('credentials.access_token')
    
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    
    if result['status'] == '200' or result['status'] == '400':
        # Reset the user's sesson.
        del login_session['credentials.access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        flash('Successfully disconnected.')
        return redirect(url_for('showCatalog'))
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# helper functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    db_session.add(newUser)
    db_session.commit()
    user = db_session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = db_session.query(User).filter_by(email=user_id).one()
    return user


def getUserID(email):
    try:
        user = db_session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None
        
        
#Function to show catalog
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    categories = db_session.query(Category).all()
    items = db_session.query(Item).order_by(Item.created.desc()).all()
    return render_template('catalog.html', categories=categories, items=items)


#Function to show the user details
@app.route('/user/')
def showUser():
    users = db_session.query(User).all()
    output = ''
    output += '<html> <body>'
    for i in users:
        output += i.name
        output += '</br>'
        output += i.email
        output += '</br>'
        output += '</body> </html>'
    return output


#Function to display the cataegories
@app.route('/catalog/<string:category_name>/')
def showCategory(category_name):
	categories = db_session.query(Category).all()
	category = db_session.query(Category).filter_by(name=category_name).one()
	items = db_session.query(Item).filter_by(category=category).all()
	return render_template('catalog.html', categories=categories, items=items, category=category)


#Function to display the items
@app.route('/item/<int:item_id>/')
def showItem(item_id):
	item = db_session.query(Item).filter_by(id=item_id).one()
	if 'username' not in login_session:
	    return redirect('/login')
	return render_template('item.html', item=item)


#Function to add items to the catalog database
@app.route('/catalog/<string:category_name>/add/', methods=['GET', 'POST'])
def addItem(category_name):
	
	# check if user is connected
        if 'username' not in login_session:
	    return redirect('/login')
	user = login_session['username']
	
	categories = db_session.query(Category).all()
	category = db_session.query(Category).filter_by(name=category_name).one()
	
	if request.method == 'POST':
		# check if an item name was entered
		if request.form['name'] != "":
			mycategory = db_session.query(Category).filter_by(name=request.form['category']).one()
			myuser = db_session.query(User).filter_by(name=user).one()
			item = Item(name=request.form['name'],
				description=request.form['description'],
				category=mycategory,
				owner=myuser
				)
			db_session.add(item)
			db_session.commit()
			flash("Item " + item.name + " added to " + item.category.name)
			return redirect(url_for('showCategory', category_name=mycategory.name))
		else:
			flash("Item name must not be empty")
			return redirect(url_for('addItem', category_name=category_name))
	else:
		return render_template('additem.html', category=category, categories=categories)


#Function to edit a item
@app.route('/item/<int:item_id>/edit/', methods=['GET', 'POST'])
def editItem(item_id):
	
	
	# check if user is connected
        if 'username' not in login_session:
	    return redirect('/login')

	item = db_session.query(Item).filter_by(id = item_id).one()
	if item.owner_id != login_session['user_id']:
	    return "<script>function myFunction() {alert('You are not authorized to edit this item. Please create your own item in order to edit.');}</script><body onload='myFunction()''>"
	if request.method == 'POST':
		# check if an item name was entered
		if request.form['name'] != "":
			item.name = request.form['name']
			item.description = request.form['description']
			if request.form['category']:
				category = db_session.query(Category).filter_by(name=request.form['category']).one()
				item.category = category

			db_session.add(item)
			db_session.commit()
			flash("Item " + item.name + " saved")
			return redirect(url_for('showItem', item_id=item.id))
		else:
			flash("Item name must not be empty")
			return redirect(url_for('editItem', item_id=item.id))
	else:
		categories = db_session.query(Category).all()
		return render_template('edititem.html', item = item, categories=categories)

	return redirect(url_for('showCatalog'))


#Function to delete an item
@app.route('/item/<int:item_id>/delete/', methods = ['GET', 'POST'])
def deleteItem(item_id):
	# check if user is connected
	if 'username' not in login_session:
	    return redirect('/login')
	item = db_session.query(Item).filter_by(id = item_id).one()
	category = item.category
	if item.owner_id != login_session['user_id']:
	    return "<script>function myFunction() {alert('You are not authorized to delete this item. Please create your own item in order to delete.');}</script><body onload='myFunction()''>"
	
	if request.method == 'POST':
		flash("Item " + item.name + " deleted")
		db_session.delete(item)
		db_session.commit()
		return redirect(url_for('showCategory', category_name=category.name))
	else:
		return render_template('deleteitem.html', item = item)


#Function to display items in Json format
@app.route('/json')
def catalogjson():
	list = []
	items = db_session.query(Item).all()
	for item in items:
		list.append({"name": item.name,
			"id": item.id,
			"category": item.category.name,
            "description": item.description,
		     })
	return jsonify({"items": list})

# run flask server if script is started directly
if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=8000)
