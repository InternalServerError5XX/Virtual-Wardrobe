from datetime import datetime
from flask import Blueprint, render_template, redirect, request, url_for, flash, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .models import *
from . import db
from .bucket_functions import save_file, remove_file, rename_file, upload_to_bucket, get_extension, get_img_s3_url, resize, delete_from_bucket
from .validation import is_valid_filename


views = Blueprint('views', __name__)


@views.route('/home/', methods=['GET', 'POST'])
@login_required
def home():
    return render_template('home.html', user = current_user)


@views.route('/', methods=['GET'])
def starrt():
     return redirect(url_for('auth.start'))


@views.route('/wardrobe/', methods=['GET','POST'])
@login_required
def wardrobe():
    if request.method == 'GET':
        args = request.args
        favourites_only = False
        message = 'No items yet...'
        if args.get('favourite') == 'True':
            user_wears = db.session.query(Wear).filter(Wear.user_id == current_user.id, Wear.favourite == True)
            favourites_only = True
            message = 'No favourite items yet...'
        elif args.get('search'):
            user_wears = db.session.query(Wear).filter(Wear.user_id == current_user.id, Wear.label.contains(args.get('search')))
            message = f'No items {args.get("search")} found'
        else:
            user_wears = db.session.query(Wear).filter(Wear.user_id == current_user.id)

        wears_url_list = []
        for wear in user_wears:
            wears_url_list.append(get_img_s3_url(wear.url))
        return render_template('wardrobe.html', user_wears=user_wears, wears_url_list=wears_url_list, favourites_only=favourites_only, message=message)
    else:
        item_id = request.form['item_id']
        specific_item = db.session.query(Wear).filter(Wear.id == item_id).first()
        specific_item.favourite = not specific_item.favourite
        db.session.commit()
        return redirect(url_for('views.wardrobe'))


@views.route('/wardrobe/<int:id>', methods=['GET','POST'])
@login_required
def wardrobe_wear(id):
    if request.method == 'POST':
        # deletes a wear img from s3
        wear_to_delete = db.session.query(Wear).filter(Wear.id == id).first()
        delete_from_bucket(wear_to_delete.url)

        # deletes a wear from db
        db.session.query(Wear).filter(Wear.id == id).delete()

        # Get the outfits to delete
        outfits_to_delete = Outfit.query.join(association_table).filter(association_table.c.wear_id == id).all()

        # Delete the outfits and their entries in the association table
        for outfit in outfits_to_delete:
            db.session.delete(outfit)
            db.session.query(association_table).filter_by(outfit_id=outfit.id).delete()

        db.session.commit()

        return redirect(url_for('views.wardrobe'))
    else:
        outfits = []
        outfits_to_delete = Outfit.query.filter(Outfit.items.any(id=id)).all()
        for outfit in outfits_to_delete:
            outfits.append(outfit.label)

        specific_item = db.session.query(Wear).filter(Wear.id == id).first()
        wear_url = get_img_s3_url(specific_item.url)
        return render_template('current_wear.html', wear_img=wear_url, wear=specific_item, outfits=outfits)


@views.route('/add-wear', methods=['GET', 'POST'])
@login_required
def add_wear():
    error_msg = []
    if request.method == 'GET':
        return render_template('add_wear.html')
    else:
        file = request.files['file']

        # check if the file has valid name and extension
        if not is_valid_filename(file.filename):
            error_msg.append('File is not selected.')
            return render_template('add_wear.html', msg=error_msg)

        # if all is ok save data to db and upload file to s3 bucket
        else:
            if len(request.form['label']) > 18:
                error_msg.append('Label must be less than 18 characters.')
                return render_template('add_wear.html', msg=error_msg)

            label = request.form['label']
            color = request.form['color']
            type_ = request.form['type']
            file = request.files['file']

            dt = datetime.now()
            new_filename = str(datetime.timestamp(dt)).replace('.', '') + '.' + get_extension(secure_filename(file.filename))

            save_file(file)
            rename_file(secure_filename(file.filename), new_filename)
            resize(new_filename)
            upload_to_bucket(new_filename)
            remove_file(new_filename)

            new_wear = Wear(label=label, color=color, type_=type_, url=new_filename, user=current_user)

            db.session.add(new_wear)
            db.session.commit()

            return redirect(url_for('views.wardrobe'))


@views.route('/wardrobe-edit/<int:id>', methods=['GET','POST'])
@login_required
def wardrobe_edit(id):
    specific_item = db.session.query(Wear).filter(Wear.id == id).first()
    error_msg = []
    if request.method == 'POST':
        file = request.files['file']

        # check if the file has valid name and extension
        if not is_valid_filename(file.filename):
            error_msg.append('File is not selected.')
            return render_template('edit_item.html', msg=error_msg, wear=specific_item)

        # if all is ok save data to db and upload file to s3 bucket
        else:
            if len(request.form['label']) > 18:
                error_msg.append('Label must be less than 18 characters.')
                return render_template('edit_item.html', msg=error_msg, wear=specific_item)

            new_label = request.form['label']
            new_color = request.form['color']
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

            db.session.query(Wear).filter(Wear.id == id).update({'label': new_label, 'color': new_color, 'type_': new_type_, 'url': new_filename})
            db.session.commit()
        return redirect(url_for('views.wardrobe'))
    else:
        return render_template('edit_item.html', wear=specific_item)


@views.route('/settings/', methods=['GET'])
@login_required
def settings():
    return render_template('settings.html', user = current_user)


