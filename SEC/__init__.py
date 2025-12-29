from flask import Flask, request, Blueprint
import os

def create_app(config_file="config.py"):
    app = Flask(__name__)
    app.config.from_pyfile(config_file)
    return app