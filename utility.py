import hashlib
import os
import random
import string
import time

from functools import wraps


def rand_number_n_digits(num_digits: int):
    return random.randrange(10**(num_digits - 1), (10**num_digits) - 1)


def get_random_string(min_length: int = 5, max_length: int = 10):
    length = random.randrange(min_length, max_length)
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def get_random_string_alphanum(min_length: int=8, max_length: int=10):
    length = random.randrange(min_length, max_length)
    character_set = string.ascii_letters + string.digits
    return ''.join(random.choice(character_set) for i in range(length))


def timeit(my_func):
    @wraps(my_func)
    def timed(*args, **kwargs):
        start = time.time()
        output = my_func(*args, **kwargs)
        end = time.time()
        diff = round(end - start, 8)
        print(f'{my_func.__name__} took {diff}s')

        return output
    return timed


def generate_random_password_set():
    pwd = get_random_string_alphanum()
    salt = generate_salt()
    pwd_hash = generate_password_hash(pwd, salt)

    return pwd, salt, pwd_hash


def generate_salt():
    return os.urandom(32)


# https://nitratine.net/blog/post/how-to-hash-passwords-in-python/
def generate_password_hash(password: str, salt):
    return hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100_000,
        dklen=128
    )