class Item(object):
    def __init__(self, id = 0, title = "", description = "", category_id = 0):
        self.id = id
        self.title = title
        self.description = description
        self.category_id = category_id

class Category(object):
    def __init__(self, id = 0, name = "", items = []):
        self.id = id
        self.name = name
        self.items = items

class Catalog(object):
    def __init__(self, Categories = []):
        self.Categories = Categories