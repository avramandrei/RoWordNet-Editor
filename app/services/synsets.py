from app import rown, enwn, ro_synsets, en_synsets
from app.utils import en_synset_relations
from app.services.model import req_synsets, req_lemmas
from rowordnet.synset import Synset as RoWNSynset
from app.utils import pos_dict
import os
import pickle


def get_leaf_synsets():
    ro_synsets_id = set(ro_synsets.keys())
    en_synsets_id = set(en_synsets.keys())

    diff_synsets_id = en_synsets_id - ro_synsets_id
    leaf_synsets_id = set()

    leaf_definition = {}
    leaf_lemmas = {}
    leaf_relations = {}
    leaf_relations_definition = {}
    leaf_relations_lemmas = {}

    # calculate the leaf synsets
    for diff_synset_id in diff_synsets_id:
        diff_synset = en_synsets[diff_synset_id]

        # get relations of the diff synset
        diff_rel_synsets = en_synset_relations(diff_synset)

        # extract relations
        rel_synset = set(diff_rel_synsets.keys())

        # calculate the intersection synsets between the diff synset and romanian synsets
        intersection = ro_synsets_id.intersection(rel_synset)

        # if any nodes have been found, add necessary fields
        if len(intersection) > 0:
            leaf_synsets_id.add(diff_synset_id)

            leaf_definition[diff_synset_id] = diff_synset.definition()

            sense = diff_synset.name().split(".")[2]
            leaf_lemmas[diff_synset_id] = [(lemma.name(), sense) for lemma in diff_synset.lemmas()]

            leaf_relations[diff_synset_id] = {inter_synset_id: diff_rel_synsets[inter_synset_id]
                                              for inter_synset_id in intersection}

            leaf_relations_definition[diff_synset_id] = {inter_synset_id: en_synsets[inter_synset_id].definition()
                                                         for inter_synset_id in intersection}

            for inter_synset_id in intersection:
                leaf_relations_lemmas[diff_synset_id] = {inter_synset_id: list()}

                for lemma in en_synsets[inter_synset_id].lemmas():
                    sense = en_synsets[inter_synset_id].name().split(".")[2]
                    leaf_relations_lemmas[diff_synset_id][inter_synset_id].append((lemma.name(), sense))

        if len(leaf_synsets_id) > 50:
            break

    return leaf_synsets_id, leaf_definition, leaf_lemmas,\
           leaf_relations, leaf_relations_definition, leaf_relations_lemmas


def remove_requested_synsets(leaf_synset_ids):
    req_synset_ids = set(synset.id for synset in req_synsets)

    leaf_synset_ids = leaf_synset_ids - leaf_synset_ids.intersection(req_synset_ids)

    return leaf_synset_ids


def add_synset_to_rowordnet(synset, lemmas, relations):
    rown_synset = RoWNSynset(id=synset.id, pos=pos_dict[synset.id[-1]], nonlexicalized=synset.nonlexicalized,
                             stamp=synset.stamp, definition=synset.definition)

    for lemma in lemmas:
        rown_synset.add_literal(lemma.name, lemma.sense)

    rown.add_synset(rown_synset)

    for rel_synset_id, relation in relations:
        rown.add_relation(synset.id, rel_synset_id, relation)

    rown.save(os.path.join("rowordnet", "rowordnet.pickle"))

def get_synset_relations(synset_id):
    synset = en_synsets[synset_id]

    all_relations = en_synset_relations(synset)

    relations = list()

    for synset, relation in all_relations.items():
        if synset in rown.synsets():
            relations.append((synset, relation))

    return relations


def save_synsets():
    with open(os.path.join("app", "resources", "synsets.pickle"), "wb") as file:
        pickle.dump(req_synsets, file)


def save_lemmas():
    with open(os.path.join("app", "resources", "lemmas.pickle"), "wb") as file:
        pickle.dump(req_lemmas, file)
