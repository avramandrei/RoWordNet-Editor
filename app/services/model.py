from werkzeug.security import check_password_hash
import os
import pickle


class Synset():
    def __init__(self, id, definition, stamp, nonlexicalized):
        self.id = id
        self.definition = definition
        self.stamp = stamp
        self.nonlexicalized = nonlexicalized

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'definition': self.definition,
            'stamp': self.stamp,
            'nonlexicalized': self.nonlexicalized,
        }


class Lemma:
    def __init__(self, id, name, sense, synset_id):
        self.id = id
        self.name = name
        self.sense = sense
        self.synset_id = synset_id

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'sense': self.sense,
            'synset_id': self.synset_id,
        }


class User:
    def __init__(self, id, username, password, is_authenticated, role, firstname, lastname, is_active=True, is_anonymous=True):
        self.id =id
        self.username = username
        self.password = password
        self.is_authenticated = is_authenticated
        self.role = role
        self.firstname = firstname
        self.lastname = lastname
        self.is_active = is_active
        self.is_anonymous = is_anonymous

    def get_id(self):
        return self.id

    def verify_password(self, password):
        return check_password_hash(self.password, password)


try:
    with open(os.path.join("app", "resources", "synsets.pickle"), "rb") as file:
        req_synsets = pickle.load(file)
except FileNotFoundError:
    req_synsets = []

try:
    with open(os.path.join("app", "resources", "lemmas.pickle"), "rb") as file:
        req_lemmas = pickle.load(file)
except FileNotFoundError:
    req_lemmas = []

try:
    with open(os.path.join("app", "resources", "users.pickle"), "rb") as file:
        users = pickle.load(file)
except FileNotFoundError:
    users = []


