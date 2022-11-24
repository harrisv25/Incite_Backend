import models

from flask import Blueprint, request, jsonify

from playhouse.shortcuts import model_to_dict

from flask_login import current_user

import psycopg2

# create our blueprint
# first argument is the blueprint's name
# second argument is its import_name
# similar to create a router in express
tests = Blueprint('tests', 'tests')

def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database='incite_db',
        user='postgres',
        password='Phareo25!Vahj1234'
        )
    return conn

@tests.route('/', methods=['GET'])
def tests_index():
    result = models.Test.select()
    print('result of test select query')
    print(result)


@tests.route('/')
def tests_index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM tests;')
    test = cur.fetchall()
    cur.close()
    conn.close()
    # return render_template('index.html', books=books)
    return jsonify(
        data=test,
        message='Successfully created test!',
        status=201
    ), 201

    # this seem helpful
    # for dog in result:
    #     print(dog.__data__)

    # or we can do it manually
    # dog_dicts = []
    # for dog in result:
    #     dog_dict = model_to_dict(dog)
    #     dog_dicts.append(dog_dict)

    # or use a list comprehension

    # dog_dicts = [model_to_dict(dog) for dog in result]
    # using current_user to get these dogs is SO SO EASY
    # we can just say current_user.dogs instead of
    # old_dogs = models.Dogs.select().where(models.Dog.owner_id == current_user.id)
    # current_user_dog_dicts = [model_to_dict(dog) for dog in current_user.dogs] # *sparkle*

    # for dog_dict in current_user_dog_dicts:
    #     dog_dict['owner'].pop('password')


    # return jsonify({
    #     'data': current_user_dog_dicts,
    #     'message': f"Successfully found {len(current_user_dog_dicts)} dogs",
    #     'status': 200
    # }), 200

# dog create route
# POST /api/v1/dogs/
# #
# @dogs.route('/', methods=['POST'])
# def create_dogs():
#     payload = request.get_json() # this is like req.body in express
#     print(payload)
#     new_dog = models.Dog.create(name=payload['name'], owner=current_user.id, breed=payload['breed'])
#     print(new_dog) # just print the ID -- check sqlite3 to see the data
#                    # run sqlite3 dogs.sqlite and run SQL queries in the CLI

#     # print(new_dog.__dict__)
#     # this might be useful, sometimes it gives you better info
#     # dict is a class attribute automatically added to the python class

#     # print(dir(new_dog)) # look at all of the models' stuff and pretty methods!!

#     # you can't jsonify new_dog directly because it's not a dictionary or
#     # other jsonifiable things
#     # so when we get this error TypeError: Object of type Dog is not JSON serializable
#     # when we try to jsonify
#     # to convert the .... wait for it ... model to dict
#     dog_dict = model_to_dict(new_dog)

#     dog_dict['owner'].pop('password')

#     return jsonify(
#         data=dog_dict,
#         message='Successfully created dog!',
#         status=201
#     ), 201


# # SHOW ROUTE
# # GET api/v1/dogs/<dog_id>
# # in express it looked something like this
# # router.get('/:id')
# @dogs.route('/<id>', methods=['GET'])
# def get_one_dog(id):
#     dog = models.Dog.get_by_id(id)
#     print(dog)
#     return jsonify(
#         data = model_to_dict(dog),
#         message = 'Success!!! 🎉',
#         status = 200
#     ), 200


# # UPDATE ROUTE
# # PUT api/v1/dogs/<dog_id>
# @dogs.route('/<id>', methods=["PUT"])
# def update_dog(id):
#     payload = request.get_json()
#     query = models.Dog.update(**payload).where(models.Dog.id == id)
#     query.execute()
#     return jsonify(
#         data = model_to_dict(models.Dog.get_by_id(id)),
#         status=200,
#         message='resource updated successfully'
#     ), 200


# # DELETE ROUTE
# # DELETE api/v1/dogs/<dog_id>
# @dogs.route('/<id>', methods=['DELETE'])
# def delete_dog(id):
#     query = models.Dog.delete().where(models.Dog.id == id)
#     query.execute()
#     return jsonify(
#         data= model_to_dict(models.Dog.get_by_id(id)),
#         message='resource successfully deleted',
#         status=200
#     ), 200



# # COMBINED ROUTES
# # GET, PUT, DELETE api/v1/dogs/<dog_id>
# # @dogs.route('/<id>', methods=['GET', 'PUT', 'DELETE'])
# # def handle_one_dog(id):
# #     try:
# #         dog = models.Dog.select().where(models.Dog.id == id).get()
# #         if request.method == 'GET':
# #                 return jsonify(
# #                     data = model_to_dict(dog),
# #                     message = 'Success!!! 🎉',
# #                     status = 200
# #                 ), 200
# #         payload = request.method == 'PUT' and request.get_json()
# #         dog.update(**payload).execute() if payload else dog.delete_instance()
# #         data = model_to_dict(models.Dog.get_by_id(id)) if payload else [model_to_dict(dog) for dog in models.Dog.select()]
# #         return jsonify(
# #             data= data,
# #             message= f'Dog {"Updated" if payload else "Deleted"} Successfully',
# #             status=200
# #         ), 200
# #     except:
# #         return jsonify(
# #             message= f'{request.method} FAILED: The dog with the id of {id} does not exist',
# #             status = 404
# #         ), 404