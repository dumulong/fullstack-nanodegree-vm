from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem


from flask import session as login_session
import random, string

app = Flask(__name__)

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase+ string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

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
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
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
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# @app.route('/catalog.json')
# def restaurantMenuJSON():
#     catgories = session.query(Category).all()
#     for category in categories:
#         items = session.query(CatgoryItem).filter_by(category_id=category.id).all()

#     return jsonify(MenuItems=[i.serialize for i in items])


# Show all categories and the latest items
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    categories = session.query(Category).order_by(Category.name).all()
    items = session.query(CategoryItem).order_by(CategoryItem.id.desc()).all()
    # return "This page will show all my categories"
    page = render_template('header.html')
    page = page + render_template('catalog.html', categories=categories, items=items)
    page = page + render_template('footer.html')
    return page

@app.route('/catalog/<string:category>/items')
def showItems(category):
    categories = session.query(Category).all()
    cat = session.query(Category).filter_by(name=category).one()
    items = session.query(CategoryItem).filter_by(category_id=cat.id).order_by(CategoryItem.title.asc()).all()
    page = render_template('header.html')
    page = page + render_template('catalog.html', categories=categories, category=category, items=items)
    page = page + render_template('footer.html')
    return page

@app.route('/catalog/<string:category>/<string:item>')
def showItem(category, item):
    myItem = session.query(CategoryItem).filter_by(title=item).one()
    page = render_template('header.html')
    page = page + render_template('item.html', item=myItem)
    page = page + render_template('footer.html')
    return page

@app.route('/catalog/add/', methods=['GET', 'POST'])
def newItem():
    if request.method == 'POST':
        newItem = CategoryItem(
            title=request.form['title'],
            description=request.form['description'],
            category_id=request.form['category_id'])
        session.add(newItem)
        session.commit()

        return redirect(url_for('showCatalog'))
    else:
        categories = session.query(Category).order_by(Category.name).all()
        page = render_template('header.html')
        page = page + render_template('itemAdd.html', categories=categories)
        page = page + render_template('footer.html')
        return page

@app.route('/catalog/edit/<int:item>', methods=['GET', 'POST'])
@app.route('/catalog/edit/<string:item>', methods=['GET', 'POST'])
def editItem(item):

    # We want to allow sending an item id or name...
    try:
        val = int(item)
        myItem = session.query(CategoryItem).filter_by(id=val).one()
    except ValueError:
        myItem = session.query(CategoryItem).filter_by(title=item).one()

    if request.method == 'POST':
        myItem.title = request.form['title']
        myItem.description = request.form['description']
        myItem.category_id = request.form['category_id']
        session.commit()
        return redirect(url_for('showItem', category=myItem.category.name, item=myItem.title))
    else:
        categories = session.query(Category).order_by(Category.name).all()
        page = render_template('header.html')
        page = page + render_template('itemEdit.html', item=myItem, categories=categories)
        page = page + render_template('footer.html')
        return page

@app.route('/catalog/delete/<int:item>', methods=['GET', 'POST'])
@app.route('/catalog/delete/<string:item>', methods=['GET', 'POST'])
def deleteItem(item):

    # We want to allow sending an item id or name...
    try:
        val = int(item)
        myItem = session.query(CategoryItem).filter_by(id=val).one()
    except ValueError:
        myItem = session.query(CategoryItem).filter_by(title=item).one()

    if request.method == 'POST':
        session.delete(myItem)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        categories = session.query(Category).order_by(Category.name).all()
        page = render_template('header.html')
        page = page + render_template('itemDelete.html', item=myItem, categories=categories)
        page = page + render_template('footer.html')
        return page

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000, threaded=False)
