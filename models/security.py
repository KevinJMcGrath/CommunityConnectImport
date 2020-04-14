import logging

import utility

class Passwords:
    def __init__(self):
        self.user_password = ''
        self.user_password_salt = ''
        self.user_password_hash = ''
        self.km_password = ''
        self.km_password_salt = ''
        self.km_password_hash = ''

    def generate_random_passwords(self):
        self.user_password, self.user_password_salt, self.user_password_hash = utility.generate_random_password_set()
        self.km_password, self.km_password_salt, self.km_password_hash = utility.generate_random_password_set()


def get_fresh_password_set():
    logging.debug('Generating fresh password set.')
    pwd = Passwords()
    pwd.generate_random_passwords()

    return pwd