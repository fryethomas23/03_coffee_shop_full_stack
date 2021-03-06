import os, sys, traceback, logging
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''

#db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = [drink.short() for drink in Drink.query.all()]

    return jsonify({
        "success": True,
        "drinks": drinks
    }), 200

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_details(token):
    if type(token) == AuthError:
        print(token)
        abort(token.status_code)

    drinks = [drink.long() for drink in Drink.query.all()]

    return jsonify({
        "success": True,
        "drinks": drinks
    }), 200

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(token):
    if type(token) == AuthError:
        print(token)
        abort(token.status_code)

    body = request.get_json()
    id = body.get('id', None)
    title = body.get('title', None)
    recipe = str(body.get('recipe', None)).replace("\'","\"")
    
    try:
        new_drink = Drink(title=title, recipe=str(recipe))
        new_drink.insert()
    except Exception as e:
        print(e)
        abort(422)
    
    return jsonify({
        "success": True,
        "drinks": new_drink.long()
    }), 200

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(token, id):
    if type(token) == AuthError:
        print(token)
        abort(token.status_code)

    selected_drink = Drink.query.filter_by(id=id).one_or_none()
    if selected_drink == None:
        abort(404)

    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None) 

    try:
        if title:
            selected_drink.title = title
        if recipe:
            selected_drink.recipe = str(recipe).replace("\'","\"")
        selected_drink.update()
    except Exception as e:
        print(e)
        abort(422)

    return jsonify({
        "success": True,
        "drinks": [selected_drink.long()]
    }), 200

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(token, id):
    if type(token) == AuthError:
        abort(token.status_code)

    selected_drink = Drink.query.filter_by(id=id).one_or_none()
    if selected_drink == None:
        abort(404)

    selected_drink.delete()

    return jsonify({
        "success": True,
        "delete": id
    }), 200

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "unprocessable"
        }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False, 
        "error": 405,
        "message": "Method Not Allowed"
        }), 405

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "Not Found"
        }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False, 
        "error": 401,
        "message": "Unauthorized"
        }), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False, 
        "error": 403,
        "message": "Forbidden"
        }), 403

@app.errorhandler(400)
def forbidden(error):
    return jsonify({
        "success": False, 
        "error": 400,
        "message": "Bad Request"
        }), 400

@app.errorhandler(AuthError)
def Authentication_error(error):
    """
    Authentication error handler 
    """
    return jsonify({
        "success": False, 
        "error": error.error['code'],
        "message": error.error['description']
        }), error.status_code