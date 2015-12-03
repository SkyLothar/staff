from flask import Blueprint, current_app, jsonify, redirect, request, url_for
from flask.ext.security import login_user, logout_user
from flask_wechat import WechatMessage

from ..account.models import User
from ..gitlab.models import GitlabAccount
from ..ext import db
from .models import WechatApp

api = Blueprint("wechat-api", __name__)


@api.route("/wechat/<uid>/callback", methods=["GET", "POST"])
def wechat_callback(uid):
    wa = WechatApp.query.filter_by(uid=uid).first_or_404()
    message = WechatMessage(wa.cipher, request)

    if not message.verified:
        current_app.logger.info("Bad Request")
        return ""
    if request.method == "GET":
        return message.data

    user = User.create(message.from_user_name)
    db.session.commit()

    if user.gitlab_account is not None:
        return message.make_text_response("hmm..")

    if message.msg_type == "BINDING":
        authorize_url = GitlabAccount.get_authorize_url(user)
        return message.make_news_response(dict(
            title="Let's Binding",
            description="",
            picurl="",
            url=authorize_url
        ))
    return message.make_text_response("you havn't bind your account yet")


@api.route("/wechat/<uid>/push", methods=["POST"])
def wechat_push(uid):
    wa = WechatApp.query.filter_by(uid=uid).first_or_404()
    req = request.get_json()
    wa.send_news(req.get("to_user"), *req["articles"])
    return jsonify(status="success")


@api.route("/bind")
def wechat_bind():
    user = GitlabAccount.authorize(
        request.values["state"],
        request.values["code"]
    )

    logout_user()
    login_user(user)
    db.session.commit()

    return redirect(url_for("index"))
