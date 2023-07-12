import os
from application.config import LocalDevelopmentConfig
from flask_security import Security,SQLAlchemySessionUserDatastore
from application.models import Role,User
from application.database import db
from flask import Flask
from flask_login import LoginManager
from application.models import User, Role
from application.models import ExtendedLoginForm,ExtendedRegisterForm,ExtendedForgotPasswordForm,ExtendedResetPasswordForm
from flask_mail import Mail
from flask_restful import Api

api=None

def create_app():
    app = Flask(__name__, template_folder="templates")
    if os.getenv('ENV', "development") == "production":
      raise Exception("Currently no production config is setup.")
    else:
      print("Starting Local Development")
      app.config.from_object(LocalDevelopmentConfig)
    
    db.init_app(app)
    api=Api(app)
    mail=Mail(app)
    
    app.app_context().push()
    user_datastore=SQLAlchemySessionUserDatastore(db.session, User, Role)
    security = Security(app, user_datastore,
       login_form=ExtendedLoginForm,register_form=ExtendedRegisterForm,forgot_password_form=ExtendedForgotPasswordForm,reset_password_form=ExtendedResetPasswordForm)
    
    
    return app,api

app, api = create_app()



# Import all the controllers so they are loaded
from application.controllers import *

from application.api import ProductAPI,CategoryAPI
api.add_resource(ProductAPI, "/api/product","/api/product/<string:prod_name>")
api.add_resource(CategoryAPI, "/api/category","/api/category/<string:cat_name>")

if __name__ == '__main__':
  # Run the Flask app
  app.run(host='0.0.0.0',port=5000)
