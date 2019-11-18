from app import app, rown, en_synsets
from flask import render_template, send_file
from app.services.synsets import get_leaf_synsets, remove_requested_synsets, add_synset_to_rowordnet, get_synset_relations, \
    save_synsets, save_lemmas, remove_lemmas_from_req_lemmas, lemmas_exists, get_synset_general_info, lemmas_invalid
from flask import request, redirect, url_for
from app.services.model import users, req_synsets, req_lemmas, Synset, Lemma
import flask
import flask_login
from app.services.acces_level import requires_access_level, access_levels
import os
from app.services.logging import log_message


@app.route('/leaf_synsets')
@flask_login.login_required
def leaf_synsets():
    leaf_synsets_id, leaf_definition, leaf_lemmas, \
    leaf_relations, leaf_relations_definition, leaf_relations_lemmas = get_leaf_synsets()

    leaf_synsets_id = remove_requested_synsets(leaf_synsets_id)

    return render_template("leaf_synsets.html",
                           leaf_synsets_id=leaf_synsets_id,
                           leaf_definition=leaf_definition,
                           leaf_lemmas=leaf_lemmas,
                           leaf_relations=leaf_relations,
                           leaf_relations_definition=leaf_relations_definition,
                           leaf_relations_lemmas=leaf_relations_lemmas
                           )


@app.route('/create_synset', methods=["GET", "POST"])
@flask_login.login_required
def create_synset():
    if request.method == "GET":
        synset_id = request.args.get('synset_id')
        stamp, en_definition, en_lemmas = get_synset_general_info(synset_id)

        log_message("Requested synset {}".format(synset_id))

        return render_template("create_synset.html",
                               synset_id=synset_id,
                               stamp=stamp,
                               en_definition=en_definition,
                               en_lemmas=en_lemmas
                               )
    if request.method == "POST":
        synset_id = request.form.get("synset_id")
        definition = request.form.get("definition")
        nonlexicalized = False if request.form.get("nonlexicalized") is None else True
        stamp = request.form.get("stamp")
        lemma_counter = int(request.form.get("lemma_counter"))

        lemma_exists, lemma_ext_name, lemma_ext_sense = lemmas_exists(request)
        lemma_invalid, lemma_inv_name, lemma_inv_sense = lemmas_invalid(request)
        # invalid form
        if lemma_exists or definition == "" or lemma_invalid or (lemma_counter == 0 and not nonlexicalized):
            stamp, en_definition, en_lemmas = get_synset_general_info(synset_id)

            error_message = ""

            if definition == "":
                error_message += "Synset must have a definition.\n"
            if lemma_exists:
                error_message += "Lemma '{}' with sense '{}' already exists in RoWordNet.\n".format(
                    lemma_ext_name, lemma_ext_sense)
            if lemma_invalid:
                error_message += "Lemma '{}' with sense '{}' has uncompleted fields.\n".format(
                    lemma_inv_name, lemma_inv_sense)
            if lemma_counter == 0 and not nonlexicalized:
                error_message += "A lexicalized synset must have at least one lemma.\n"

            lemma_counter = int(request.form.get("lemma_counter"))
            lemmas = []

            for lemma_id in range(lemma_counter):
                req_lemma = request.form.get("lemma_" + str(lemma_id) + "_name")
                req_sense = request.form.get("lemma_" + str(lemma_id) + "_sense")

                lemmas.append((req_lemma, req_sense))

            return render_template("create_synset.html",
                                   synset_id=synset_id,
                                   stamp=stamp,
                                   lemmas=lemmas,
                                   en_definition=en_definition,
                                   en_lemmas=en_lemmas,
                                   definition=definition,
                                   error=True,
                                   error_message=error_message
                                   )

        synset = Synset(id=synset_id, definition=definition, nonlexicalized=nonlexicalized, stamp=stamp)

        new_lemmas = []
        if not nonlexicalized:
            for lemma_id in range(lemma_counter):
                lemma_name = request.form.get("lemma_" + str(lemma_id) + "_name")
                lemma_sense = request.form.get("lemma_" + str(lemma_id) + "_sense")

                lemma = Lemma(name=lemma_name, sense=lemma_sense, synset_id=synset_id)

                new_lemmas.append(lemma)
                req_lemmas.append(lemma)

        req_synsets.append(synset)
        save_synsets()
        save_lemmas()

        # if it's an admin, save it directly
        user_id = flask_login.current_user.get_id()
        for user in users:
            if user.id == user_id:
                if user.role == access_levels["admin"]:
                    add_synset_to_rowordnet(synset_id)
                elif user.role == access_levels["user"]:
                    log_message("New synset added to the requested synsets")
                    log_message(synset)
                    log_message("Literals: {}".format([(lemma.name, lemma.sense) if lemma.synset_id == synset_id else "" for lemma in new_lemmas]))

                break

        return redirect(url_for('leaf_synsets'))


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    if request.method == 'POST':
        username = flask.request.form['username']
        password = flask.request.form['password']

        user = None

        for user_it in users:
            if user_it.username == username:
                user = user_it

        if user is None:
            return render_template("login.html", invalid_credentials=True)

        if user.verify_password(password):
            flask_login.login_user(user)

            user.is_authenticated = True

            log_message("Logged in.")

            return flask.redirect(flask.url_for('leaf_synsets'))
        else:
            return render_template("login.html", invalid_credentials=True)


@app.route("/logout")
@flask_login.login_required
def logout():
    user_id = flask_login.current_user.get_id()
    user = None

    for user_it in users:
        if user_it.id == user_id:
            user = user_it

    log_message("Logged out.")

    user.is_authenticated = False

    flask_login.logout_user()

    return redirect(flask.url_for('login'))


@app.route('/requested_synsets')
@flask_login.login_required
@requires_access_level(access_levels["moderator"])
def requested_synsets():
    return render_template("requested_synsets.html", requested_synsets=req_synsets,
                           requested_lemmas=req_lemmas)


@app.route('/requested_synsets/accept_synset')
@flask_login.login_required
@requires_access_level(access_levels["moderator"])
def aceept_requested_synset():
    synset_id = request.args.get('synset_id')

    add_synset_to_rowordnet(synset_id)

    log_message("Accept synset: {}".format(synset_id))

    return render_template("requested_synsets.html", requested_synsets=req_synsets,
                           requested_lemmas=req_lemmas)


@app.route('/requested_synsets/reject_synset')
@flask_login.login_required
@requires_access_level(access_levels["moderator"])
def reject_requested_synset():
    synset_id = request.args.get('synset_id')

    for req_synset in req_synsets:
        if req_synset.id == synset_id:
            req_synsets.remove(req_synset)
            log_message("Synset rejected: ")
            log_message(req_synset)
            break

    save_synsets()

    remove_lemmas_from_req_lemmas(synset_id)

    save_lemmas()

    return render_template("requested_synsets.html", requested_synsets=req_synsets,
                           requested_lemmas=req_lemmas)


@app.route('/requested_synsets/edit_synset', methods=["GET", "POST"])
@flask_login.login_required
@requires_access_level(access_levels["moderator"])
def edit_requested_synset():
    if request.method == "GET":
        synset_id = request.args.get("synset_id")

        for synset in req_synsets:
            if synset_id == synset.id:
                definition = synset.definition
                nonlexicalized = synset.nonlexicalized
                stamp = synset.stamp

        lemmas = []
        for lemma in req_lemmas:
            if lemma.synset_id == synset_id:
                lemmas.append((lemma.name, lemma.sense))

        en_definition = en_synsets[synset_id].definition()
        en_lemmas = [(lemma.name(), en_synsets[synset_id].name().split(".")[2]) for lemma in
                     en_synsets[synset_id].lemmas()]

        log_message("Edit synset: {} - {}. Lemmas: {}".format(synset_id, definition, lemmas))

        return render_template("edit_synset.html", synset_id=synset_id, definition=definition,
                               nonlexicalized=nonlexicalized, stamp=stamp, lemmas=lemmas, en_definition=en_definition,
                               en_lemmas=en_lemmas)
    if request.method == "POST":
        synset_id = request.form.get("synset_id")
        definition = request.form.get("definition")
        nonlexicalized = False if request.form.get("nonlexicalized") is None else True
        stamp = request.form.get("stamp")
        lemma_counter = request.form.get("lemma_counter")

        lemma_exists, lemma_ext_name, lemma_ext_sense = lemmas_exists(request)
        lemma_invalid, lemma_inv_name, lemma_inv_sense = lemmas_invalid(request)
        # form is not correct
        if lemma_exists or definition == "" or lemma_invalid or (lemma_counter == 0 and not nonlexicalized):
            stamp, en_definition, en_lemmas = get_synset_general_info(synset_id)

            error_message = ""

            if definition == "":
                error_message += "Synset must have a definition.\n"
            if lemma_exists:
                error_message += "Lemma '{}' with sense '{}' already exists in RoWordNet.\n".format(lemma_ext_name, lemma_ext_sense)
            if lemma_invalid:
                error_message += "Lemma '{}' with sense '{}' has uncompleted fields.\n".format(lemma_inv_name, lemma_inv_sense)
            if lemma_counter == 0 and not nonlexicalized:
                error_message += "A lexicalized synset must have at least one lemma.\n"

            lemma_counter = int(request.form.get("lemma_counter"))
            lemmas = []

            for lemma_id in range(lemma_counter):
                req_lemma = request.form.get("lemma_" + str(lemma_id) + "_name")
                req_sense = request.form.get("lemma_" + str(lemma_id) + "_sense")

                lemmas.append((req_lemma, req_sense))

            return render_template("edit_synset.html", synset_id=synset_id, definition=definition,
                                   nonlexicalized=nonlexicalized, stamp=stamp, lemmas=lemmas,
                                   en_definition=en_definition,
                                   en_lemmas=en_lemmas,
                                   error=True,
                                   error_message=error_message
                                   )

        for synset in req_synsets:
            if synset.id == synset_id:
                synset.definition = definition
                synset.nonlexicalized = nonlexicalized
                synset.stamp = stamp

        remove_lemmas_from_req_lemmas(synset_id)

        for i in range(int(lemma_counter)):
            name = request.form.get("lemma_{}_name".format(i))
            sense = request.form.get("lemma_{}_sense".format(i))
            lemma = Lemma(name=name, sense=sense, synset_id=synset_id)

            req_lemmas.append(lemma)

        add_synset_to_rowordnet(synset_id)

        return redirect(url_for('requested_synsets'))


@app.route('/download_rowordnet')
@flask_login.login_required
@requires_access_level(access_levels["moderator"])
def download_rowordnet():
    rown.save(os.path.join("rowordnet", "rowordnet.xml"), xml=True)

    rowordnet_path = os.path.join("..", "rowordnet", "rowordnet.xml")

    log_message("Download rowordnet")

    return send_file(rowordnet_path, as_attachment=True)



