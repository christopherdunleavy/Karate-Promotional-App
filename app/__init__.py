from flask import Flask
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_login import LoginManager
from database_setup import Base, User
from flask_bcrypt import Bcrypt


bcrypt = Bcrypt()
login_manager = LoginManager()
engine = create_engine(os.environ['DATABASE_URL'])
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

def createApp():
    app = Flask(__name__)
    app.secret_key = 'super_secret_key'
    login_manager.init_app(app)
    bcrypt.init_app(app)
    registerBlueprints(app)
    return app

def registerBlueprints(app):
    from app.application_blueprint import application_blueprint

    app.register_blueprint(application_blueprint)
