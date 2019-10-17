pos_dict = {"n": "NOUN", "a": "ADJECTIVE", "v": "VERB", 'r': "ADVERB"}
pos_dict_inv = {"NOUN": "n", "ADJECTIVE": "a", "VERB": "v", "ADVERB": "r"}


def en_synset_to_id(synset):
    return "ENG30-{:08d}-{}".format(synset.offset(), synset.pos() if synset.pos() is not "s" else "a")


def en_synset_relations(synset):
    rel_synsets = {}

    # find hypernyms
    for hypernym in synset.hypernyms():
        rel_synsets[en_synset_to_id(hypernym)] = "hypernym"

    # find instance_hypernyms
    for instance_hypernym in synset.instance_hypernyms():
        rel_synsets[en_synset_to_id(instance_hypernym)] = "instance_hypernym"

    # find hyponyms
    for hyponym in synset.hyponyms():
        rel_synsets[en_synset_to_id(hyponym)] = "hyponym"

    # find instance_hyponyms
    for instance_hyponym in synset.instance_hyponyms():
        rel_synsets[en_synset_to_id(instance_hyponym)] = "instance_hyponym"

    # find member_holonym
    for member_holonym in synset.member_holonyms():
        rel_synsets[en_synset_to_id(member_holonym)] = "member_holonym"

    # find substance_holonyms
    for substance_holonym in synset.substance_holonyms():
        rel_synsets[en_synset_to_id(substance_holonym)] = "substance_holonym"

    # find substance_holonyms
    for part_holonym in synset.part_holonyms():
        rel_synsets[en_synset_to_id(part_holonym)] = "part_holonym"

    # find member_meronyms
    for member_meronym in synset.member_meronyms():
        rel_synsets[en_synset_to_id(member_meronym)] = "member_meronym"

    # find substance_meronyms
    for substance_meronym in synset.substance_meronyms():
        rel_synsets[en_synset_to_id(substance_meronym)] = "substance_meronym"

    # find part_meronyms
    for part_meronym in synset.part_meronyms():
        rel_synsets[en_synset_to_id(part_meronym)] = "part_meronym"

    # find attributes
    for attribute in synset.attributes():
        rel_synsets[en_synset_to_id(attribute)] = "attribute"

    # find causes
    for cause in synset.causes():
        rel_synsets[en_synset_to_id(cause)] = "cause"

    # find entailments
    for entailment in synset.entailments():
        rel_synsets[en_synset_to_id(entailment)] = "entailment"

    # find also_sees
    for also_see in synset.also_sees():
        rel_synsets[en_synset_to_id(also_see)] = "also_see"

    # find verb_groups
    for verb_group in synset.verb_groups():
        rel_synsets[en_synset_to_id(verb_group)] = "verb_group"

    # find similar_tos
    for similar_to in synset.similar_tos():
        rel_synsets[en_synset_to_id(similar_to)] = "similar_to"

    for lemma in synset.lemmas():
        ant_lemmas = lemma.antonyms()
        for ant_lemma in ant_lemmas:
            rel_synsets[en_synset_to_id(ant_lemma.synset())] = "near_antonym"

        pert_lemmas = lemma.pertainyms()
        for pert_lemma in pert_lemmas:
            rel_synsets[en_synset_to_id(pert_lemma.synset())] = "near_pertainym"

        deriv_lemmas = lemma.derivationally_related_forms()
        for deriv_lemma in deriv_lemmas:
            rel_synsets[en_synset_to_id(deriv_lemma.synset())] = "near_derived_from"

    return rel_synsets
