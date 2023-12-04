from datetime import datetime
from flask import Blueprint, render_template, redirect, request, url_for, flash, session
from flask_login import login_required, current_user
from sqlalchemy import func
from werkzeug.utils import secure_filename
from .models import *
from . import db
from .bucket_functions import save_file, remove_file, rename_file, upload_to_bucket, get_extension, get_img_s3_url, resize, delete_from_bucket
from .validation import is_valid_filename

outfits_views = Blueprint('outfits_views', __name__)


@outfits_views.route('/', methods=['GET', 'POST'])
@login_required
def outfits():
    if request.method == 'GET':
        args = request.args
        favourites_only = False
        message = 'No outfits yet...'
        if args.get('favourite') == 'True':
            user_outfits = db.session.query(Outfit).filter(Outfit.user_id == current_user.id, Outfit.favourite == True)
            favourites_only = True
            message = 'No favourite outfits yet...'
        elif args.get('search'):
            user_outfits = db.session.query(Outfit).filter(Outfit.user_id == current_user.id, Outfit.label.contains(args.get('search')))
            message = f'No outfits {args.get("search")} found'
        else:
            user_outfits = db.session.query(Outfit).filter(Outfit.user_id == current_user.id)

        # deletes all outfits with completed=False from db
        completed_false_outfits = Outfit.query.filter_by(completed=False).all()

        for outfit in completed_false_outfits:
            db.session.delete(outfit)
        db.session.commit()

        items_urls = []
        for outfit in user_outfits:
            for wear in outfit.items:
                items_urls.append(get_img_s3_url(wear.url))
        return render_template('outfits.html', favourites_only=favourites_only, outfits=user_outfits, wear_urls=items_urls, message=message, s3_func=get_img_s3_url)
    else:
        outfit_id = request.form['outfit_id']
        specific_item = db.session.query(Outfit).filter(Outfit.id == outfit_id).first()
        specific_item.favourite = not specific_item.favourite
        db.session.commit()
        return redirect(url_for('outfits_views.outfits'))


@outfits_views.route('/outfit_add/', methods=['GET', 'POST'])
@login_required
def add_outfit():
    if request.method == 'POST':
        args = request.args
        hat = args.get('Hat')
        body = args.get('Body')
        legs = args.get('Legs')
        feet = args.get('Feet')
        outfit_label = request.form['outfit_label']

        new_outfit = Outfit(label=outfit_label, user_id=current_user.id)

        hat = Wear.query.filter_by(id=int(hat)).first()
        body = Wear.query.filter_by(id=int(body)).first()
        legs = Wear.query.filter_by(id=int(legs)).first()
        feet = Wear.query.filter_by(id=int(feet)).first()

        new_outfit.items.append(hat)
        new_outfit.items.append(body)
        new_outfit.items.append(legs)
        new_outfit.items.append(feet)

        db.session.add(new_outfit)
        db.session.commit()
        return redirect(url_for('outfits_views.outfits'))
    else:

        args = request.args
        hat = args.get('Hat')
        body = args.get('Body')
        legs = args.get('Legs')
        feet = args.get('Feet')
        current_wears = [hat, body, legs, feet]

        img_urls = [None, None, None, None]
        if hat != '0':
            img_urls[0] = db.session.query(Wear).filter(Wear.user_id == current_user.id, Wear.id == int(hat)).first().url
        if body != '0':
            img_urls[1] = db.session.query(Wear).filter(Wear.user_id == current_user.id, Wear.id == int(body)).first().url
        if legs != '0':
            img_urls[2] = db.session.query(Wear).filter(Wear.user_id == current_user.id, Wear.id == int(legs)).first().url
        if feet != '0':
            img_urls[3] = db.session.query(Wear).filter(Wear.user_id == current_user.id, Wear.id == int(feet)).first().url
        return render_template('create_outfit.html', current_wears=current_wears, img_urls=img_urls, s3_func=get_img_s3_url)


@outfits_views.route('/outfit/add_wear/', methods=['GET', 'POST'])
@login_required
def add_wear_to_outfit():
    if request.method == 'POST':
        args = request.args
        id = args.get('id')
        hat = id if 'Hat' == args.get('type') else args.get('Hat')
        body = id if 'Body' == args.get('type') else args.get('Body')
        legs = id if 'Legs' == args.get('type') else args.get('Legs')
        feet = id if 'Feet' == args.get('type') else args.get('Feet')
        current_wears = [hat, body, legs, feet]
        return redirect(url_for("outfits_views.add_outfit", Hat=hat, Body=body, Legs=legs, Feet=feet))

    else:
        valid_types = ["Hat", "Body", "Legs", "Feet"]
        args = request.args
        hat = args.get('Hat')
        body = args.get('Body')
        legs = args.get('Legs')
        feet = args.get('Feet')

        current_wears = [hat, body, legs, feet]
        if args.get('type') in valid_types:
            wear_type = db.session.query(Wear).filter(Wear.user_id == current_user.id, Wear.type_ == args.get('type'))
        else:
            error_code = 'type'
            description = 'Current wear is not in allowed types (p.s. don\'t change url parameters)'
            return render_template("error.html", error_code=error_code, description=description)

        items_urls = []
        for wear in wear_type:
            items_urls.append(get_img_s3_url(wear.url))
        return render_template("choose_wears.html", user_wears=wear_type, wear_urls=items_urls,  s3_func=get_img_s3_url, current_wears=current_wears)


@outfits_views.route('/<int:id>', methods=['GET','POST'])
@login_required
def current_outfit(id):
    if request.method == 'POST':
        # Get the outfits to delete
        outfits_to_delete = Outfit.query.join(association_table).filter(association_table.c.wear_id == id, Outfit.id == id).all()

        # Delete the outfits and their entries in the association table
        for outfit in outfits_to_delete:
            db.session.delete(outfit)
            db.session.query(association_table).filter_by(outfit_id=outfit.id).delete()

        outfit = db.session.query(Outfit).filter(Outfit.id == id).first()

        db.session.delete(outfit)
        db.session.commit()

        return redirect(url_for('outfits_views.outfits'))
    else:
        current_outfit = db.session.query(Outfit).filter(Outfit.user_id == current_user.id, Outfit.id == id).first()
        return render_template('specific_outfit.html', outfit=current_outfit, s3_func=get_img_s3_url)

