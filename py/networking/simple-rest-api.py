#!/usr/bin/env python3
'''
Example REST API. Can be expanded to act as a server of some sort or whatever.
'''

import argparse

from flask import Flask, request
from flask_restful import Api, Resource


class ExampleResource(Resource):
    '''
    An example REST endpoint. Handles GET, POST, PUT, and DELETE
    '''

    def get(self):
        '''
        Handle the GET request here. Parameters in request.GET
        '''
        print("GET request: ", request)
        return {}

    def post(self):
        '''
        Handle the POST request here.
        '''
        print("POST request: ", request)

        # Example for handling POST with a file
        # f = request.files['some_key']
        # f.save('file/path')
        return {}

    def put(self):
        '''
        Handle PUT request here.
        '''
        print("PUT request: ", request)
        return {}

    def delete(self):
        '''
        Handle DELETE request here.
        '''
        print("DELETE request: ", request)
        return {}


def load_api(app):
    '''
    Example loading the resources so they're available.
    '''
    Api(app).add_resource(ExampleResource, "/url/to/resource")


def create_app(name=None):
    '''
    Creates the Flast application and sets stuff up.
    '''
    app = Flask(name or 'app')
    load_api(app)
    return app


def main():
    '''
    Entry point
    '''
    parser = argparse.ArgumentParser(description="Runs a simple REST server")
    parser.add_argument('-p', "--port", type=int)
    parser.add_argument('-i', "--host")
    args = parser.parse_args()

    host = args.host or "0.0.0.0"
    port = args.port or 8080

    app = create_app()
    app.run(host, port, True, use_reloader=True)


if __name__ == "__main__":
    main()
