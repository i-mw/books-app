from flask import Flask, render_template, url_for, request, redirect, jsonify, flash, session as login_session
import random, string
from database_setup import Base, Category, Book, User
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from flask import make_response
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import json
import requests

engine = create_engine('sqlite:///booksapp.db')
Base.metadata.bind = engine

app = Flask(__name__)

CLIENT_ID = "150625342836-362i0s186aqmhuf06du3eoogs2t40qna.apps.googleusercontent.com"

@app.route('/login')
def show_login():
    state = ''.join([random.choice(string.ascii_uppercase+string.digits) for i in range(32)])
    login_session['state'] = state
    print(login_session)
    return render_template('login.html', STATE=login_session['state'])


@app.route('/gconnect', methods=['POST'])
def gconnect():
    #1st check - state token
    if request.args['state'] != login_session['state']:
        response = make_response(json.dumps("Invalid state parameter"), 401)
        response.headers['content-type'] = 'application/json'
        return response


    try:
        code = request.data
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to exchanged authorization code'), 401)
        response.headers['content-type'] = 'application/json'
        return response

    access_token = credentials.access_token
    google_id = credentials.id_token['sub']
    r = requests.get('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'.format(access_token))
    token_info = r.json()

    #2nd check - credentials access token is valid?
    if token_info.get('error') is not None:
        response = make_response(json.dumps('Access token is not valid'), 401)
        response.headers['content-type'] = 'application/json'
        return response

    #3rd check - credentials user_id is the intended user?
    if token_info['user_id'] != google_id:
        response = make_response(json.dumps('Access token for different user'), 401)
        response.headers['content-type'] = 'application/json'
        return response

    #4th check - credentials client_id is the intended app client?
    if CLIENT_ID != token_info['issued_to']:
        response = make_response(json.dumps('Access token for different app'), 401)
        response.headers['content-type'] = 'application/json'
        return response        

    #5th check - not already logged in
    stored_access_token = login_session.get('access_token')
    stored_google_id = login_session.get('google_id')
    if stored_access_token is not None and stored_google_id==google_id:
        response = make_response(json.dumps('Already logged in'), 200)
        response.headers['content-type'] = 'application/json'
        return response

    login_session['access_token'] = access_token
    login_session['google_id'] = google_id

    params = {
        'access_token': access_token,
        'alt': 'json'
    }
    r = requests.get('https://www.googleapis.com/oauth2/v1/userinfo', params=params)
    user_info = r.json()

    login_session['name'] = user_info['name']
    login_session['picture'] = user_info['picture']
    login_session['email'] = user_info['email']

    #Check the user in the database
    user_id = get_user_id(login_session['email'])
    if user_id is None:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id


    output = ''
    output += '<h1>Welcome, '
    output += login_session['name']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['name'])
    print("done!")
    return output


def create_user(login_session):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    new_user = User(name=login_session['name'], email=login_session['email'], picture=login_session['picture'])

    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id
    

def get_user_info(user_id):    
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    user = session.query(User).filter_by(id=user_id).one()
    return user


def get_user_id(email):
    try:
        DBSession = sessionmaker(bind=engine)
        session = DBSession()

        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

@app.route('/gdisconnect')
def gdisconnect():
    if login_session.get('access_token') is None:
        response = make_response(json.dumps('no user logged in'), 401)
        response.headers['content-type'] = 'application/json'
        return response

    r = requests.get('https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token'])

    if r.status_code == 200:
        del login_session['access_token']
        del login_session['google_id']
        del login_session['name']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('successfully logged out'), 200)
        response.headers['content-type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps("couldn't log you out"), 400)
        response.headers['content-type'] = 'application/json'
        return response        


@app.route('/')
def show_categories():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    categories = session.query(Category).all()
    # if 'name' not in login_session:
    #     return render_template('public-categories-list.html', categories=categories)        
    return render_template('categories-list.html', categories=categories)


@app.route('/category/new', methods=['GET', 'POST'])
def add_category():
    # if 'name' not in login_session:
    #     return redirect('/login')
    if request.method == 'POST':
        DBSession = sessionmaker(bind=engine)
        session = DBSession()

        #, user_id=login_session['user_id']
        new_category = Category(name=request.form['category_name'])
        session.add(new_category)
        session.commit()
        flash('New category added successfully!')

        return redirect(url_for('show_categories'))
    else:
        return render_template('new-category.html')


@app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
def edit_category(category_id):
    # if 'name' not in login_session:
    #     return redirect('/login')    
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    if request.method == 'POST':
        category = session.query(Category).filter_by(id=category_id).one()
        category.name = request.form['category_name']
        session.add(category)
        session.commit()
        flash('Category name changed successfully!')

        return redirect(url_for('show_categories'))
    else:
        category = session.query(Category).filter_by(id=category_id).one()
        return render_template('edit-category.html', category=category)


@app.route('/category/<int:category_id>/delete', methods=['GET', 'POST'])
def delete_category(category_id):
    # if 'name' not in login_session:
    #     return redirect('/login')    
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    if request.method == 'POST':
        category = session.query(Category).filter_by(id=category_id).one()
        session.delete(category)
        session.commit()
        flash('Category deleted successfully!')

        return redirect(url_for('show_categories'))
    else:
        category = session.query(Category).filter_by(id=category_id).one()
        return render_template('delete-category.html', category=category)


@app.route('/category/<int:category_id>/books')
def show_books(category_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    category = session.query(Category).filter_by(id=category_id).one()
    books=session.query(Book).filter_by(category_id=category_id)
    return render_template('category-books.html', category=category, books=books)

    
@app.route('/category/<int:category_id>/books/new', methods=['GET', 'POST'])
def add_book(category_id):
    # if 'name' not in login_session:
    #     return redirect('/login')    
    DBSession = sessionmaker(bind=engine)
    session = DBSession()    
    if request.method == 'POST':
        new_book = Book(name=request.form['book_name'],
                            description=request.form['book_description'],
                            author=request.form['book_author'],
                            category_id=category_id)
        session.add(new_book)
        session.commit()
        flash('Book added successfully!')
        return redirect(url_for('show_books', category_id=category_id))
    else:
        category = session.query(Category).filter_by(id=category_id).one()
        return render_template('new-book.html', category=category)


@app.route('/category/<int:category_id>/book/<int:book_id>/edit', methods=['GET', 'POST'])
def edit_book(category_id, book_id):
    # if 'name' not in login_session:
    #     return redirect('/login')    
    DBSession = sessionmaker(bind=engine)
    session = DBSession()    
    if request.method == 'POST':
        book = session.query(Book).filter_by(id=book_id).one()
        book.name = request.form['book_name']
        book.description = request.form['book_description']
        book.author = request.form['book_price']

        session.add(book)
        session.commit()
        flash('Book edited successfully!')
        return redirect(url_for('show_books', category_id=category_id))
    else:
        category = session.query(Category).filter_by(id=category_id).one()
        book = session.query(Book).filter_by(id=book_id).one()
        return render_template('edit-book.html', category=category, book=book)


@app.route('/category/<int:category_id>/book/<int:book_id>/delete', methods=['GET', 'POST'])
def delete_book(category_id, book_id):
    # if 'name' not in login_session:
    #     return redirect('/login')    
    DBSession = sessionmaker(bind=engine)
    session = DBSession()    
    if request.method == 'POST':
        book = session.query(Book).filter_by(id=book_id).one()
        session.delete(book)
        session.commit()
        flash('Book deleted successfully')
        return redirect(url_for('show_books', category_id=category_id))
    else:
        category = session.query(Category).filter_by(id=category_id).one()
        book = session.query(Book).filter_by(id=book_id).one()
        return render_template('delete-book.html', category=category, book=book)


#JSON endpoints
@app.route('/categories/JSON')
def list_categories():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    categories = session.query(Category).all()
    return jsonify(categories=[cat.serialize for cat in categories])


@app.route('/category/<int:category_id>/books/JSON')
def list_category(category_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    category = session.query(Category).filter_by(id=category_id).one()
    books=session.query(Book).filter_by(category_id=category_id)
    return jsonify(category=category.serialize, books=[book.serialize for book in books])


@app.route('/category/<int:category_id>/book/<int:book_id>/JSON')
def list_one_book(category_id, book_id):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    book=session.query(Book).filter_by(id=book_id).one()
    return jsonify(book=book.serialize)


if __name__ == '__main__':
    app.secret_key = 'momo'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)