from werkzeug.security import generate_password_hash, check_password_hash
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

users = [
    User(1, "verginica.barbu",
         "pbkdf2:sha256:150000$XhoGbp8C$c13ca840c685b5971eded007c858180dc99d4b183a8464a756dc67ae08a8df67",
         False, 2, "Verginica", "Barbu"),

    User(2, "andrei.avram",
         "pbkdf2:sha256:150000$nDm04HBe$e499a69576ec5bd334e042a2d7488ada18234be06f15994bbb633c0298d15eef",
         False, 0, "Andrei", "Avram"),

    User(3, "admin.admin",
         "pbkdf2:sha256:150000$BOJy8Ew0$152d4e56163f20fc0e1170368312203841223852f4fe2ec07845058c451f910d",
         False, 2, "Admin", "Admin")
]
