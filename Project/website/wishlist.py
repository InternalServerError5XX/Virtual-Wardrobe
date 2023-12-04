from datetime import datetime
from flask import Blueprint, render_template, redirect, request, url_for, flash, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .models import *
from . import db
from .bucket_functions import save_file, remove_file, rename_file, upload_to_bucket, get_extension, get_img_s3_url, resize, delete_from_bucket
from .validation import is_valid_filename

wish_views = Blueprint('wish_views', __name__)


@wish_views.route('/', methods=['GET', 'POST'])
@login_required
def wish_list():
    if request.method == 'GET':
        args = request.args
        favourites_only = False
        message = 'No wish items yet...'
        if args.get('favourite') == 'True':
            user_wish_wears = db.session.query(WishWear).filter(WishWear.user_id == current_user.id, WishWear.favourite == True)
            favourites_only = True
            message = 'No favourite wish items yet...'
        elif args.get('search'):
            user_wish_wears = db.session.query(WishWear).filter(WishWear.user_id == current_user.id, WishWear.label.contains(args.get('search')))
            message = f'No items {args.get("search")} found'
        else:
            user_wish_wears = db.session.query(WishWear).filter(WishWear.user_id == current_user.id)

        wears_url_list = []
        for wish_wear in user_wish_wears:
            wears_url_list.append(get_img_s3_url(wish_wear.url))
        return render_template('wishlist.html', user_wears=user_wish_wears, wears_url_list=wears_url_list, favourites_only=favourites_only, message=message)
    else:
        item_id = request.form['item_id']
        specific_item = db.session.query(WishWear).filter(WishWear.id == item_id).first()
        specific_item.favourite = not specific_item.favourite
        db.session.commit()
        return redirect(url_for('wish_views.wish_list'))


@wish_views.route('/add-wish', methods=['GET', 'POST'])
@login_required
def add_wish():
    error_msg = []
    if request.method == 'GET':
        return render_template('add_wish.html')
    else:
        file = request.files['file']

        # check if the file has valid name and extension
        if not is_valid_filename(file.filename):
            error_msg.append('File is not selected.')
            return render_template('add_wish.html', msg=error_msg)

        try:
            float(request.form['price'])
        except:
            error_msg.append('Price must be a number.')
            return render_template('add_wish.html', msg=error_msg)

        # if all is ok save data to db and upload file to s3 bucket
        else:
            if len(request.form['label']) > 18:
                error_msg.append('Label must be less than 18 characters.')
                return render_template('add_wish.html', msg=error_msg)

            label = request.form['label']
            color = request.form['color']
            price = request.form['price']
            location = request.form['location']
            type_ = request.form['type']
            file = request.files['file']

            dt = datetime.now()
            new_filename = str(datetime.timestamp(dt)).replace('.', '') + '.' + get_extension(secure_filename(file.filename))

            save_file(file)
            rename_file(secure_filename(file.filename), new_filename)
            resize(new_filename)
            upload_to_bucket(new_filename)
            remove_file(new_filename)

            new_wish_wear = WishWear(label=label, color=color, price=price, location=location, type_=type_, url=new_filename, user=current_user)

            db.session.add(new_wish_wear)
            db.session.commit()

            return redirect(url_for('wish_views.wish_list'))


@wish_views.route('/<int:id>', methods=['GET','POST'])
@login_required
def wish_wear(id):
    if request.method == 'POST':
        # deletes a wear img from s3
        wear_to_delete = db.session.query(WishWear).filter(WishWear.id == id).first()
        delete_from_bucket(wear_to_delete.url)
        # deletes a wear from db
        db.session.query(WishWear).filter(WishWear.id == id).delete()
        db.session.commit()
        return redirect(url_for('wish_views.wish_list'))
    else:
        specific_item = db.session.query(WishWear).filter(WishWear.id == id).first()
        wear_url = get_img_s3_url(specific_item.url)
        return render_template('current_wish.html', wear_img=wear_url, wear=specific_item)


@wish_views.route('/wishlist_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def wish_edit(id):
    specific_item = db.session.query(WishWear).filter(WishWear.id == id).first()
    error_msg = []
    if request.method == 'POST':
        file = request.files['file']

        # check if the file has valid name and extension
        if not is_valid_filename(file.filename):
            error_msg.append('File is not selected.')
            return render_template('edit_wish.html', msg=error_msg, wear=specific_item)
        try:
            float(request.form['price'])
        except:
            error_msg.append('Price must be a number.')
            return render_template('add_wish.html', msg=error_msg)

        # if all is ok save data to db and upload file to s3 bucket
        else:
            if len(request.form['label']) > 18:
                error_msg.append('Label must be less than 18 characters.')
                return render_template('edit_wish.html', msg=error_msg, wear=specific_item)

            new_label = request.form['label']
            new_color = request.form['color']
            new_price = request.form['price']
            new_location = request.form['location']
            new_type_ = request.form['type']
            new_file = request.files['file']

            dt = datetime.now()
            new_filename = str(datetime.timestamp(dt)).replace('.', '') + '.' + get_extension(
                secure_filename(new_file.filename))

            save_file(new_file)
            rename_file(secure_filename(new_file.filename), new_filename)
            resize(new_filename)
            upload_to_bucket(new_filename)
            remove_file(new_filename)

            delete_from_bucket(specific_item.url)

            db.session.query(WishWear).filter(WishWear.id == id).update({'label': new_label, 'color': new_color, 'price':new_price, 'location': new_location, 'type_': new_type_, 'url': new_filename})
            db.session.commit()
        return redirect(url_for('wish_views.wish_list'))
    else:
        return render_template('edit_wish.html', wear=specific_item)


@wish_views.route('/wishlist_move_to_wardrobe/<int:id>', methods=['POST'])
@login_required
def wish_move(id):
    if request.method == 'POST':
        specific_item = db.session.query(WishWear).filter(WishWear.id == id).first()
        new_wear = Wear(favourite=specific_item.favourite, label=specific_item.label, color=specific_item.color, type_=specific_item.type_, url=specific_item.url, user=current_user)
        db.session.add(new_wear)
        db.session.query(WishWear).filter(WishWear.id == id).delete()
        db.session.commit()
        return redirect(url_for('views.wardrobe'))
