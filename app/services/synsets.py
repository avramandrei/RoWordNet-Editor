from app import rown, enwn, ro_synsets, en_synsets
from app.utils import en_synset_relations
from app.services.model import req_synsets, req_lemmas
from rowordnet.synset import Synset as RoWNSynset
from app.utils import pos_dict
import os
import pickle
import flask_login
from app.services.model import users


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


def remove_lemmas_from_req_lemmas(synset_id):
    length = len(req_lemmas)
    i = 0

    while i < length:
        if req_lemmas[i].synset_id == synset_id:
            del req_lemmas[i]
            i -= 1
            length -= 1

        i += 1


def add_synset_to_rowordnet(synset_id):
    for req_synset in req_synsets:
        if req_synset.id == synset_id:
            synset = req_synset
            req_synsets.remove(req_synset)
            break

    save_synsets()

    rown_synset = RoWNSynset(id=synset.id, pos=pos_dict[synset.id[-1]], nonlexicalized=synset.nonlexicalized,
                             stamp=synset.stamp, definition=synset.definition)

    for req_lemma in req_lemmas:
        if req_lemma.synset_id == synset_id:
            rown_synset.add_literal(req_lemma.name, req_lemma.sense)

    remove_lemmas_from_req_lemmas(synset_id)

    save_lemmas()

    rown.add_synset(rown_synset)

    outbound_relations, inbound_relations = get_synset_relations(synset_id)

    print(outbound_relations)
    print(inbound_relations)

    for rel_synset_id, relation in outbound_relations:
        rown.add_relation(synset.id, rel_synset_id, relation)

    for rel_synset_id, relation in inbound_relations:
        rown.add_relation(rel_synset_id, synset.id, relation)

    print("New synset added to the WordNet: ")
    rown.print_synset(synset_id)

    rown.save(os.path.join("rowordnet", "rowordnet.pickle"))

    ro_synsets[synset_id] = rown_synset


def get_synset_relations(synset_id):
    synset = en_synsets[synset_id]

    all_relations = en_synset_relations(synset)

    outbound_relations = list()

    for synset, relation in all_relations.items():
        if synset in rown.synsets():
            outbound_relations.append((synset, relation))

    inbound_relations = list()

    # for out_synset_id, _ in outbound_relations:
    #     out_synset_relations = en_synset_relations(en_synsets[out_synset_id])
    #
    #     for (out_rel_synset_id, out_rel_synset_rel) in out_synset_relations.items():
    #         if out_rel_synset_id == synset_id:
    #             inbound_relations.append((out_synset_id, out_rel_synset_rel))

    for ro_synset_id in rown.synsets():
        if ro_synset_id.startswith("ENG"):
            out_synset_relations = en_synset_relations(en_synsets[ro_synset_id])

        for (out_rel_synset_id, out_rel_synset_rel) in out_synset_relations.items():
            if out_rel_synset_id == synset_id:
                inbound_relations.append((ro_synset_id, out_rel_synset_rel))

    return outbound_relations, inbound_relations


def save_synsets():
    with open(os.path.join("app", "resources", "synsets.pickle"), "wb") as file:
        pickle.dump(req_synsets, file)


def save_lemmas():
    with open(os.path.join("app", "resources", "lemmas.pickle"), "wb") as file:
        pickle.dump(req_lemmas, file)


def lemmas_exists(request):
    synsets_id = rown.synsets()

    for synset_id in synsets_id:
        synset = rown.synset(synset_id)

        for lemma, sense in zip(synset.literals, synset.literals_senses):
            lemma_counter = int(request.form.get("lemma_counter"))

            for lemma_id in range(lemma_counter):
                req_lemma = request.form.get("lemma_" + str(lemma_id) + "_name")
                req_sense = request.form.get("lemma_" + str(lemma_id) + "_sense")

                if req_lemma == lemma and req_sense == sense and ("x" in sense or "c" in sense):
                    return True, req_lemma, req_sense

    return False, None, None


def get_synset_general_info(synset_id):
    user_id = flask_login.current_user.get_id()

    for user in users:
        if user.id == user_id:
            firstname = user.firstname
            lastname = user.lastname

    en_definition = en_synsets[synset_id].definition()
    en_lemmas = [(lemma.name(), en_synsets[synset_id].name().split(".")[2]) for lemma in en_synsets[synset_id].lemmas()]

    return firstname + " " + lastname, en_definition, en_lemmas

