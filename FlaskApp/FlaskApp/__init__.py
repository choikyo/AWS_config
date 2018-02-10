from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from FlaskApp.categoryitem import Base, Category, Item
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
app = Flask(__name__)
app.secret_key = 'some random generated key'
CLIENT_ID = json.loads(
    open('/var/www/FlaskApp/FlaskApp/client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "ITEM CATALOG"

engine = create_engine('postgresql://catalog:password@localhost/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Print value of state token for debbuging
    print ("***********request.args:")
    print (request.args.get('state'))
    print ("**********end of request.args")

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
    print ("connect setup===> access_token : %s" % access_token)
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
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
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    print ("Access token: %s" % stored_access_token)
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'),
            200)
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
    output += ''' " style = "width: 300px;
                            height: 300px;
                            border-radius: 150px;
                            -webkit-border-radius: 150px;
                            -moz-border-radius: 150px;"> '''
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output


# Validate Session Token
def ValidateAccessToken():
    access_token = login_session.get('access_token')
    if access_token is None:
        return false
    else:
        return true


# Log out - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print ('Access Token is None')
        response = make_response(
            json.dumps('Current user not connected.'),
            401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s'
    url = url % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print ('result is ')
    print (result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(
            json.dumps('Successfully disconnected.'),
            200)
        response.headers['Content-Type'] = 'application/json'
        return redirect("/")
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Return username if exists
def GetEmail():
    email = None
    if 'email' in login_session:
        email = login_session['email']
    return email


# Authorizing on item
def GetAuthor(item_name):
    item = session.query(Item).filter(
        Item.name == item_name).first()
    return item.created_by


# Add item form
@app.route('/catalog/newItem', methods=['GET', 'POST'])
def AddItemForm():
    username = GetEmail()
    if username is None:
            flash("Please login with your Google Account")
            return redirect("/")

    # rendering new item form html UI
    if request.method == 'GET':
        category = session.query(Category).order_by(Category.name)
        return render_template('new_item.html',
                               category=category,
                               username=username)

    # adding item to database, then redirect
    if request.method == 'POST':
        itemname = request.form['itemname']
        itemdescription = request.form['itemdescription']
        categoryid = request.form['categoryid']
        item = Item(name=itemname,
                    description=itemdescription,
                    category_id=categoryid,
                    created_by=username)
        flash("New item %s has been added" % itemname)
        session.add(item)
        session.commit()
        return redirect("/")


# Edit item form
@app.route('/catalog/<string:item_name>/edit', methods=['GET', 'POST'])
def EditItemForm(item_name):
    username = GetEmail()
    # authentication check  & item authorization check
    if username is None or GetAuthor(item_name) != username:
        flash("Please login with your Google Account")
        return redirect("/")

    # render edit item form html UI
    if request.method == 'GET':
        category = session.query(Category).order_by(Category.name)
        item = session.query(Item).filter(
            Item.name == item_name).first()
        return render_template('edit_item.html',
                               item=item,
                               username=username,
                               category=category)

    # update existing item, then redirect
    if request.method == 'POST':
        itemname = request.form['itemname']
        itemdescription = request.form['itemdescription']
        categoryid = request.form['categoryid']
        update_item = session.query(Item).filter(
            Item.name == item_name).one()
        update_item.name = itemname
        update_item.description = itemdescription
        update_item.category_id = categoryid
        session.add(update_item)
        session.commit()
        flash("%s has been updated" % item_name)
        return redirect("/")


# Delete an item
@app.route('/catalog/<string:item_name>/delete', methods=['GET', 'POST'])
def DeleteItem(item_name):
    username = GetEmail()
    # authentication check  & item authorization check
    if username is None or GetAuthor(item_name) != username:
        flash("""
    You do not have permission for this page.
    Please login with your Google Account
    """)
        return redirect("/")

    if request.method == 'GET':
        return render_template('delete_item.html', item_name=item_name)

    if request.method == 'POST':
        itemname = request.form['pitem_name']
        item = session.query(Item).filter(Item.name == itemname).one()
        session.delete(item)
        session.commit()
        flash("%s has been deleted" % itemname)
        return redirect("/")


# Show list of items of a selected category
@app.route('/catalog/<string:category_name>/<string:item_name>')
def ShowItemDesc(category_name, item_name):
    username = GetEmail()
    item = session.query(Item).join(Category).filter(
        Category.name == category_name
        ).filter(Item.name == item_name).first()
    return render_template('show_item_description.html',
                           item=item,
                           username=username)


# Show list of items of a selected category
@app.route('/catalog/<string:category_name>/items')
def CategoryItemList(category_name):
    username = GetEmail()
    category = session.query(Category).order_by(Category.name)
    item = session.query(Item).join(Category).filter(
        Category.name == category_name)
    count = item.from_self().count()
    if count > 1:
        count_str = str(count) + " items"
    else:
        count_str = str(count) + " item"

    return render_template('category_item.html',
                           category=category,
                           item=item,
                           category_name=category_name,
                           count_str=count_str,
                           username=username)


# Main page
@app.route('/')
@app.route('/main')
def MainPage():
    state = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    category = session.query(Category).order_by(Category.name)
    item = session.query(Item).join(Category).limit(8)
    item = item.from_self().order_by(Item.insert_date.desc())
    username = None
    if 'email' in login_session:
        username = login_session['email']
    return render_template('main.html',
                           category=category,
                           item=item,
                           username=username,
                           STATE=state)


# JSON all item
@app.route('/catalog.json')
def getAllItems():
    data = {}
    item_json = {}
    category = session.query(Category).all()
    for i in category:
        data[i.name] = i.serialize
        item = session.query(Item).filter(Item.category_id == i.id).all()
        item_json = [j.serialize for j in item]
        print ("*****start*******")
        print (item_json)
        print ("*****end*******")
        data[i.name]["items"] = item_json
    return jsonify(data)


@app.route('/catalog/<string:category_name>.json')
def getOneCategory(category_name):
    category = session.query(Category).filter(
        Category.name == category_name).first()
    return jsonify(category.serialize)


@app.route('/catalog/<string:item_name>.json')
def getOneItem(item_name):
    item = session.query(Item).filter(Item.name == item_name).all()
    return jsonify(item.serialize)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)

