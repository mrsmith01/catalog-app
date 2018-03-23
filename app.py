from flask import Flask, render_template, url_for, request, redirect, flash, jsonify

from catalog_db_setup import Base, Users, Category, Items
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Udacity Catalog App"

engine = create_engine('sqlite:///catalogappusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)


########################### Registration #####################################
@app.route('/register/')
def showRegister():
    return render_template('register.html')

########################### Sign In ###########################################

@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/logout/')
def showLogout():
    return "This will be the logout function! </br></br> <a href='/home'>Home</a>"

########################### Google 3rd-party Authorization #####################
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
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'% access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']


    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# DISCONNECT - Revoke a current user's token and reset their login_session.
@app.route('/gdisconnect/')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return redirect('/')
    # Execute HTTP GET request to revoke current token.
    print 'In gdisconnect access token is %s', access_token
    print 'User name is:'
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        # Reset the users session.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('User Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect('/')
    else:
        # For whatever reason, the given token was invaild.
        response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


################################### FB Connect ################################


################################### Users ######################################

def createUser(login_session):
    newUser = Users(name = login_session['username'], email = login_session['email'], picture = login_session['picture'])
    session.add(newUser)
    session.commit()
    users = session.query(Users).filter_by(email = login_session['email']).one()
    return users.id

def getUserInfo(users_id):
    users = session.query(Users).filter_by(id=users_id).one()
    return users

def getUserID(email):
    try:
        users = session.query(Users).filter_by(email=email).one()
        return users.id
    except:
        return None

    # see if user exists, if not, create new user
    users_id = getUserInfo(login_session['email'])
    if not users_id:
        users_id = createUser(login_session)
        login_session['users_id'] = users_id


######################### All Categories (PUBIC) ##############################

# Show Home Page
@app.route('/')
@app.route('/home/')
def Home():
    return render_template('home.html')

# Show Full Catalog
@app.route('/catalog/')
def allCategories():
    category = session.query(Category).order_by(asc(Category.name))
    if 'username' not in login_session:
        return render_template('publiccatalog.html', category=category)
    else:
        return render_template('catalog.html', category=category)

######################### Catalog Edits (PRIVATE) ############################

# New Catalog
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCatalog():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'],
        users_id=login_session['users_id'])
        session.add(newCategory)
        session.commit()
        flash('%s Created Successfully!' % newCategory.name)
        return redirect(url_for('allCategories'))
    else:
        return render_template('newCat.html')

# Edit Catalog
@app.route('/catalog/<int:category_id>/edit/', methods=['GET','POST'])
def editCatalog(category_id):
    editedCategory = session.query(Category).filter_by(id=category_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedCategory.users_id != login_session['users_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this Category!');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
            if request.form['name']:
                editedCategory.name = request.form['name']
            session.add(editedCategory)
            session.commit()
            flash('%s Edit Successful!' % editedCategory.name)
            return redirect(url_for('allCategories', category_id=category_id))
    else:
            return render_template('editCat.html', category=editedCategory)

# Delete Catalog
@app.route('/catalog/<int:category_id>/delete/', methods=['GET','POST'])
def deleteCatalog(category_id):
    cattoDelete = session.query(Category).filter_by(id=category_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if cattoDelete.users_id != login_session['users_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this Category!');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(cattoDelete)
        session.commit()
        flash('%s Successfully Deleted!' % cattoDelete.name)
        return redirect(url_for('allCategories', category_id=category_id))
    else:
        return render_template('deleteCat.html', category=cattoDelete)

####################### Category Items (PUBLIC) ###############################

# Show items in Category
@app.route('/catalog/<int:category_id>/items/')
@app.route('/catalog/<int:category_id>/')
def showCategoryItems(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    creator = getUserInfo(category.users_id)
    items = session.query(Items).filter_by(category_id=category.id)
    if 'username' not in login_session or creator.id != login_session['users_id']:
        return render_template('publicitems.html', category=category, items=items, creator=creator)
    else:
        return render_template('items.html', category = category, items = items, creator=creator)



#Show individual category item
@app.route('/catalog/<int:category_id>/<int:items_id>/')
def showCatalogItem(category_id,items_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Items).filter_by(id=items_id).one()
    creator = getUserInfo(items.users_id)
    if 'username' not in login_session or creator.id != login_session['users_id']:
        return render_template('publicitem.html', category_id=category_id, items=items, creator=creator)
    else:
        return render_template('item.html', category_id = category_id, items=items, creator=creator)


######################### Category Edits (PRIVATE) ############################

# New Category item
@app.route('/catalog/<int:category_id>/new/', methods=['GET', 'POST'])
def newCategoryItem(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
            newItem = Items(name=request.form['name'],
            description=request.form['description'], category_id=category_id,
                users_id=category.users_id)
            session.add(newItem)
            session.commit()
            flash('%s Item created Successfully!' % newItem.name)
            return redirect(url_for('showCategoryItems', category_id = category_id))
    else:
            return render_template('newCatItem.html', category_id = category_id)

# Edits Category Item
@app.route('/catalog/<int:category_id>/<int:items_id>/edititem', methods=['GET', 'POST'])
def editCategoryItem(category_id,items_id):
        editedItems = session.query(Items).filter_by(id=items_id).one()
        category = session.query(Category).filter_by(id=category_id).one()
        if 'username' not in login_session:
            return redirect('/login')
            if editedItems.users_id != login_session['users_id']:
                return "<script>function myFunction() {alert('You are not authorized to edit this item!');}</script><body onload='myFunction()''>"
        if request.method == 'POST':
            if request.form['name']:
                editedItems.name = request.form['name'],
            if request.form['description']:
                editedItems.description = request.form['description']
            session.add(editedItems)
            session.commit()
            flash('%s Item edited!' % editedItems.name)
            return redirect(url_for('showCatalogItem', category_id = category_id, items_id=items_id))
        else:
            return render_template('editItem.html', category_id=category_id, items_id=items_id, items=editedItems)

# Delete Category Item
@app.route('/catalog/<int:category_id>/<int:items_id>/delete/', methods=['GET', 'POST'])
def deleteCategoryItem(category_id,items_id):
        category = session.query(Category).filter_by(id=category_id).one()
        itemToDelete = session.query(Items).filter_by(id=items_id).one()
        if 'username' not in login_session:
                return redirect('/login')
                if itemtoDelete.users_id != login_session['users_id']:
                    return "<script>function myFunction() {alert('You are not authorized to delete this item!');}</script><body onload='myFunction()''>"
        if request.method == 'POST':
            session.delete(itemToDelete)
            session.commit()
            flash('Category Item deleted! ')
            return redirect(url_for('showCatalogItem', category_id=category_id, items_id=items_id))
        else:
            return render_template('deleteItem.html', category_id = category_id, items_id=items_id, items=itemToDelete)

######################### JSON API (PUBLIC) ###################################

@app.route('/catalog/JSON/')
def allCategoriesJSON():
    category = session.query(Category).all()
    return jsonify(Category=[category.serialize for category in category])


@app.route('/catalog/<int:category_id>/items/JSON')
def showCategoryItemsJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Items).filter_by(category_id=category_id).all()
    return jsonify(Items=[items.serialize for items in items])


###############################################################################

if __name__ == '__main__':
    app.secret_key = 'superduper_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)
