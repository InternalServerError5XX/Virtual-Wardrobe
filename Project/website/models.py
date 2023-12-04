from . import db
from flask_login import UserMixin


association_table = db.Table(
    "outfit_wears",
    db.metadata,
    db.Column("outfit_id", db.ForeignKey("outfits.id")),
    db.Column("wear_id", db.ForeignKey("wears.id")),
)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(30))
    password = db.Column(db.String(50))
    confirmed = db.Column(db.Boolean, default=False)
    wears = db.relationship("Wear", backref="user")
    wish_wears = db.relationship("WishWear", backref="user")
    outfits = db.relationship('Outfit', backref='user')
    

class Wear(db.Model):
    __tablename__ = 'wears'
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(18))
    color = db.Column(db.String(7))
    type_ = db.Column(db.String(4))
    url = db.Column(db.String(1000))
    favourite = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Outfit(db.Model):
    __tablename__ = 'outfits'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    label = db.Column(db.String(20))
    items = db.relationship("Wear", secondary=association_table)
    favourite = db.Column(db.Boolean, default=False)
    completed = db.Column(db.Boolean, default=True)


class WishWear(db.Model):
    __tablename__ = 'wish_wears'
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(18))
    color = db.Column(db.String(7))
    type_ = db.Column(db.String(4))
    url = db.Column(db.String(1000))
    location = db.Column(db.String(1000))
    price = db.Column(db.Float)
    favourite = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))









