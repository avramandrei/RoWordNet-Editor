import logging
import flask_login
from flask import request
from datetime import datetime as dt
from app.services.model import users


logger = logging.getLogger('werkzeug')


def log_message(message):
    user_id = flask_login.current_user.get_id()

    for user_it in users:
        if user_it.id == user_id:
            user = user_it

    logger.info("%s - - [%s] %s: %s",
                request.remote_addr,
                dt.utcnow().strftime("%d/%b/%Y:%H:%M:%S.%d")[:-3],
                user.username,
                message)