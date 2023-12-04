from datetime import datetime
from flask import Blueprint, render_template, redirect, request, url_for, flash, session
from flask_login import login_required, current_user
from sqlalchemy import func
from werkzeug.utils import secure_filename
from .models import *
from . import db
from .bucket_functions import save_file, remove_file, rename_file, upload_to_bucket, get_extension, get_img_s3_url, resize, delete_from_bucket
from .validation import is_valid_filename

generate_views = Blueprint('generate_views', __name__)


@generate_views.route('/', methods=['GET'])
@login_required
def generate():
    return render_template('main_generate.html')


@generate_views.route('/outfit', methods=['GET', 'POST'])
@login_required
def generating():
    if request.method == 'POST':

        wear_ids = request.args.getlist('id')
        outfit_label = request.form['outfit_label']

        new_outfit = Outfit(label=outfit_label, user_id=current_user.id)

        hat = Wear.query.filter_by(id=wear_ids[0]).first()
        body = Wear.query.filter_by(id=wear_ids[1]).first()
        legs = Wear.query.filter_by(id=wear_ids[2]).first()
        feet = Wear.query.filter_by(id=wear_ids[3]).first()

        new_outfit.items.append(hat)
        new_outfit.items.append(body)
        new_outfit.items.append(legs)
        new_outfit.items.append(feet)

        db.session.add(new_outfit)
        db.session.commit()

        return redirect(url_for('outfits_views.outfits'))

    else:
        wear_types = ['Hat', 'Body', 'Legs', 'Feet']
        wears = []
        for wear_type in wear_types:
            wear = db.session.query(Wear).filter(Wear.user_id == current_user.id, Wear.type_ == wear_type).order_by(
                func.random()).first()
            wears.append(wear)

        # Add None for wear types that do not have a wear item
        # None is used as a string to handle with query params!
        for i in range(len(wear_types)):
            if wears[i] is None:
                wears[i] = 'None'
        wears_url_list = []
        for wear in wears:
            if wear == 'None':
                wears_url_list.append('None')
            else:
                wears_url_list.append(get_img_s3_url(wear.url))
        wear_ids = [wear.id for wear in wears if wear != 'None']
        return render_template('regenerate.html', outfit=wears, wears_url_list=wears_url_list, wear_ids=wear_ids)