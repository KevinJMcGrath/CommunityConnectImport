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