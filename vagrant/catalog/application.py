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
        categories = session.query(Category).all()
        return render_template('newItem.html', categories=categories)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000, threaded=False)
