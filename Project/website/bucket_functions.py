import os

import boto3
from flask import Flask
from werkzeug.utils import secure_filename
from .key_config import *
from PIL import Image, ImageOps


app = Flask(__name__)
# s3 configuration
UPLOAD_FOLDER = 'website/temp_files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
BUCKET_NAME = 'secular-bucket'
s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_ACCESS, region_name='eu-central-1')


def resize(filename):
    image = Image.open(UPLOAD_FOLDER + '/' + filename)
    image = ImageOps.exif_transpose(image)
    new_image = image.resize((700, 700))
    new_image.save(UPLOAD_FOLDER + '/' + filename)


def save_file(file):
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


def rename_file(old_filename, new_filename):
    os.rename(UPLOAD_FOLDER + '/' + old_filename, UPLOAD_FOLDER + '/' + new_filename)


def upload_to_bucket(filename):
    path = UPLOAD_FOLDER + '/' + filename
    s3.upload_file(Bucket=BUCKET_NAME, Filename=path, Key=filename)


def delete_from_bucket(filename):
    s3.delete_object(Bucket=BUCKET_NAME, Key=filename)


def remove_file(filename):
    os.remove(UPLOAD_FOLDER + '/' + filename)


def get_extension(filename):
    extension = filename.split('.', 1)
    if len(extension) > 0:
        filename = extension[1]
    return extension[1]


def get_img_s3_url(filename):
    return s3.generate_presigned_url('get_object', Params={'Bucket': BUCKET_NAME, 'Key': filename})
