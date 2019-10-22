import sys
import os
print("Adding new user...")
sys.stdout = open(os.devnull, "w")

import pickle
from app.services.model import User
from werkzeug.security import generate_password_hash
import argparse
from app.services.acces_level import access_levels

sys.stdout = sys.__stdout__

parser = argparse.ArgumentParser()
parser.add_argument("--username")
parser.add_argument("--password")
parser.add_argument("--role")
parser.add_argument("--firstname", default="")
parser.add_argument("--lastname", default="")

args = parser.parse_args()

with open(os.path.join("app", "resources", "users.pickle"), "rb") as file:
    users = pickle.load(file)

for user in users:
    if user.username == args.username:
        raise ValueError("Username is not unique")

next_id = max([user.id for user in users]) + 1

new_user = User(next_id,
                args.username,
                generate_password_hash(args.password),
                False,
                access_levels[args.role],
                args.firstname, args.lastname)

users.append(new_user)

with open(os.path.join("app", "resources", "users.pickle"), "wb") as file:
    pickle.dump(users, file)

print("User '{}' successfully added".format(args.username))
