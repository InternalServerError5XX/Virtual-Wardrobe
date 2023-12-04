from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_mail import Mail

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'ZAlupka'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SECURITY_PASSWORD_SALT'] = 'ZALUPA!2.0'
    app.config['MAIL_DEFAULT_SENDER'] = 'from@example.com'
    
    mail1 = Mail(app)

    db.init_app(app)

    from .views import views
    from .auth import auth
    from .wishlist import wish_views
    from .generate_outfit import generate_views
    from .outfits import outfits_views

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(wish_views, url_prefix='/wish_views/')
    app.register_blueprint(auth, url_prefix='/auth/')
    app.register_blueprint(generate_views, url_prefix='/generate/')
    app.register_blueprint(outfits_views, url_prefix='/outfits/')

    from .models import User
 
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.start'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

# def create_database(app):
#     if not path.exists('website/' + DB_NAME):
#         db.create_all(app=app)
#         print('Created Database!')
