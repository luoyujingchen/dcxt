from flask import Flask
from flask_restful import abort, reqparse, Resource, Api
from flask_restful.representations import json
from peewee import *
from playhouse.shortcuts import model_to_dict

app = Flask(__name__)
api = Api(app)


@app.route('/')
def hello_world():
    return 'Hello World!'


FOODS = {
    'foodid1': {'name': 'food 1', 'price': 24},
    'foodid2': {'name': 'food 2', 'price': 25},
    'foodid3': {'name': 'food 3', 'price': 26},
}


def abort_if_food_doesnt_exist(food_id):
    if food_id not in FOODS:
        abort(404, message="food {} doesn't exist".format(food_id))


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
            if args[key]!= None:
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
