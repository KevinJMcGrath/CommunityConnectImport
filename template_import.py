import csv

from models.user import ImportedUser

def import_user_data(file_path: str):
    user_dict = {}

    with open(file_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            user = ImportedUser(row)

            if user.company in user_dict:
                user_dict[user.company].append(user)
            else:
                user_dict[user.company] = [user]

    return user_dict