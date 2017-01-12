import sys
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource, fields, marshal_with

import button as b

DBPATH = "p.db"

app = Flask(__name__)
api = Api(app)

button_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'clicks': fields.Integer,
    'resets': fields.Integer,
    'criationTimestamp': fields.String(attribute='creationTime'),
    'lastResetTimestamp': fields.String(attribute='lastReset')
}

clickParser = reqparse.RequestParser()
clickParser.add_argument('delta', type=int)

resetParser = reqparse.RequestParser()
resetParser.add_argument('reset')

newButtonParser = reqparse.RequestParser()
newButtonParser.add_argument('name', required=True)


class Button(Resource):

    @marshal_with(button_fields, envelope='button')
    def get(self, button_id):
        db = b.load_db(DBPATH)
        try:
            button = b.Button(db, button_id)
            button.get()
        except KeyError:
            abort(404, message=
                  "Button {} doesn't exist".format(button_id))

        return button
              

    @marshal_with(button_fields, envelope='button')
    def put(self, button_id):
        args = clickParser.parse_args()

        db = b.load_db(DBPATH)
        try:

            button = b.Button(db, button_id)
            if args['delta']:
                button.click(args['delta'])
            else:
                button.click()

        except KeyError:
            abort(404, message=
                  "Button {} doesn't exist".format(button_id))

        return button

    @marshal_with(button_fields, envelope='button')
    def post(self, button_id):
        args = resetParser.parse_args()

        db = b.load_db(DBPATH)
        try:
            if args['reset'] == 'yes':
                button = b.Button(db, button_id)
                button.reset()

                return button
            else:
                abort(404, message=
                      "Reset must be confirmed with reset field set to yes".format(button_id))


        except KeyError:
            abort(404, message=
                  "Button {} doesn't exist".format(button_id))


#     def delete(self, button_id):
#         abort_if_todo_doesnt_exist(button_id)
#         del TODOS[button_id]
#         return '', 204


class ButtonList(Resource):

    def get(self):
        db = b.load_db(DBPATH)
        return b.Button.list(db)

    @marshal_with(button_fields, envelope='button')
    def post(self):
        db = b.load_db(DBPATH)
        args = newButtonParser.parse_args()
        button = b.Button.new(db, args['name'])

        return button, 201

api.add_resource(ButtonList, '/buttons')
api.add_resource(Button, '/buttons/<button_id>')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
