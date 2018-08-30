import os

from flask import Flask, request, redirect, url_for, render_template
from flask_restful import abort, reqparse, Resource, Api
from flask_restful.representations import json
from flask_uploads import UploadSet, IMAGES, configure_uploads, patch_request_class
from peewee import *
from playhouse.shortcuts import model_to_dict


app = Flask(__name__)
api = Api(app)

app.config['UPLOADED_PHOTOS_DEST'] = os.path.dirname(os.path.abspath(__file__))
photos = UploadSet('photos',IMAGES)
configure_uploads(app,photos)
patch_request_class(app,12*1024*1024)


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST' and 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        return redirect(url_for('show', name=filename))
    return render_template('upload.html')


@app.route('/photo/<name>')
def show(name):
    if name is None:
        abort(404)
    url = photos.url(name)
    return render_template('show.html', url=url, name=name)


parser = reqparse.RequestParser()
parser.add_argument('name')
parser.add_argument('price')

db = SqliteDatabase('food.db')


class Dish(Model):
    id = PrimaryKeyField()
    name = CharField()
    price = DoubleField()

    class Meta:
        database = db  # This model uses the "food.db" database.


# Food
# shows a single food item and lets you delete a food item
class Food(Resource):
    def get(self, food_id):
        return model_to_dict(Dish.get(Dish.id == food_id))

    def delete(self, food_id):
        dish = Dish.get(Dish.id == food_id)
        return dish.delete_instance(), 204

    def put(self, food_id):
        args = parser.parse_args()
        dish = Dish.get(Dish.id == food_id)
        keys = args.keys()
        for key in keys:
            if args[key] != None:
                dish.__dict__['__data__'][key] = args[key]
        return dish.save(), 201


# FoodList
# shows a list of all foods, and lets you POST to add new foods
class FoodList(Resource):
    def get(self):
        foods = Dish.select().dicts()
        fs = []
        for row in foods:
            fs.append(row)
        return fs

    def post(self):
        args = parser.parse_args()
        dish = Dish()
        keys = args.keys()
        if 'name' in keys:
            dish.name = args['name']
        if 'price' in keys:
            dish.price = args['price']
        return dish.save(), 201


##
## Actually setup the Api resource routing here
##
api.add_resource(FoodList, '/foods')
api.add_resource(Food, '/foods/<food_id>')


def initialize_db():
    db.connect()
    db.create_tables([Dish], safe=True)
    db.close()


initialize_db()

if __name__ == '__main__':
    app.run()
