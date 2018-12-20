from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

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
    categories = session.query(Category).all()
    items = session.query(CategoryItem).all()
    # return "This page will show all my categories"
    return render_template('catalog.html', categories=categories, items=items)


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
        categories = session.query(Category).all()
        return render_template('newItem.html', categories=categories)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000, threaded=False)
