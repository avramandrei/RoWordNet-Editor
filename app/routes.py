from app import app
from flask import render_template
from app.services.synsets import get_leaf_synsets, remove_requested_synsets, add_synset_to_rowordnet, get_synset_relations, save_synsets, save_lemmas
from flask import request, redirect, url_for
from app.services.models import users, req_synsets, req_lemmas, Synset, Lemma
import flask
import flask_login
from app.services.acces_level import requires_access_level, access_levels


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

        user_id = flask_login.current_user.get_id()

        for user in users:
            if user.id == user_id:
                firstname = user.firstname
                lastname = user.lastname

        return render_template("create_synset.html",
                               synset_id=synset_id,
                               stamp=lastname + " " + firstname
                               )
    if request.method == "POST":
        synset_id = request.form.get("synset_id")
        definition = request.form.get("definition")
        nonlexicalized = False if request.form.get("nonlexicalized") is None else True
        stamp = request.form.get("stamp")

        synset = Synset(id=synset_id, definition=definition, nonlexicalized=nonlexicalized, stamp=stamp)
        req_synsets.append(synset)
        save_synsets()

        if not nonlexicalized:
            lemma_counter = int(request.form.get("lemma_counter"))

            for lemma_id in range(lemma_counter):
                lemma_name = request.form.get("lemma_" + str(lemma_id) + "_name")
                lemma_sense = request.form.get("lemma_" + str(lemma_id) + "_sense")

                lemma = Lemma(id=req_lemmas[-1].id if len(req_lemmas) > 0 else 0,
                              name=lemma_name, sense=lemma_sense, synset_id=synset_id)
                req_lemmas.append(lemma)
                save_lemmas()

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

    for req_synset in req_synsets:
        if req_synset.id == synset_id:
            synset = req_synset
            req_synsets.remove(req_synset)
            break

    lemmas = []

    for req_lemma in req_lemmas:
        if req_lemma.synset_id == synset_id:
            lemmas.append(req_lemma)
            req_lemmas.remove(req_lemma)

    save_synsets()
    save_lemmas()

    relations = get_synset_relations(synset_id)

    add_synset_to_rowordnet(synset, lemmas, relations)

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
            break

    for req_lemma in req_lemmas:
        if req_lemma.synset_id == synset_id:
            req_lemmas.remove(req_lemma)

    save_synsets()
    save_lemmas()

    return render_template("requested_synsets.html", requested_synsets=req_synsets,
                           requested_lemmas=req_lemmas)

