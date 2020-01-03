from flask import Flask
from app.utils import en_synset_to_id
import os
import logging

print()

print("Loading the Romanian WordNet...")
from rowordnet import RoWordNet
rown = RoWordNet(os.path.join("rowordnet", "rowordnet.xml"), xml=True)
ro_synsets = {synset_id: rown.synset(synset_id) for synset_id in rown.synsets()}

print("Loading the English WordNet...")
from nltk.corpus import wordnet as enwn
import nltk
nltk.download('wordnet')
en_synsets = {en_synset_to_id(synset): synset for synset in enwn.all_synsets()}


app = Flask(__name__)

app.secret_key = b'_2#yBL"A4A8k\no]/'
logging.basicConfig(filename='info.log', level=logging.ERROR)

from app.services.login import login_manager

from app import routes