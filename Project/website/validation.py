# from auth import *


def rate_password(password):
    points = int(0)
    special_symbols = '$%&@<>!'
    if len(password) >= 8:  # перевірка довжини
        points += int(1)

    if password != password.lower():  # перевірка на принаймні одну букву у верхньому регістрі
        points += int(1)

    if password != password.upper():  # перевірка на принаймні одну букву у нижньому регістрі
        points += int(1)

    if sum(c.isdigit() for c in password) >= 2:  # перевірка на кількість цифр (принаймні 2)
        points += int(1)

    if any(c not in special_symbols for c in password):
        points += int(1)

    return points


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'jfif'}


def is_valid_filename(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

