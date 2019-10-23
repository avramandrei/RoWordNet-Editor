from flask import Flask
from app.utils import en_synset_to_id
import os

print()

print("Loading the Romanian WordNet...")
from rowordnet import RoWordNet
rown = RoWordNet(os.path.join("rowordnet", "rowordnet.pickle"))
ro_synsets = {synset_id: rown.synset(synset_id) for synset_id in rown.synsets()}

print("Loading the English WordNet...")
from nltk.corpus import wordnet as enwn
en_synsets = {en_synset_to_id(synset): synset for synset in enwn.all_synsets()}


app = Flask(__name__)

app.secret_key = b'_2#yBL"A4A8k\no]/'


from app.services.login import login_manager

from app import routes