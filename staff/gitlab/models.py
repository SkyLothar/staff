import requests

from flask import abort

from ..account.models import User
from ..ext import cache, db
from ..mixin import BasicMixin
from ..utils import get_uid
from . import config


class GitlabAccount(db.Model, BasicMixin):
    __tablename__ = "gitlab_account"
    session = requests.Session()

    username = db.Column(db.Unicode(255), index=True, nullable=False)
    email = db.Column(db.Unicode(255), index=True, nullable=False)
    refresh_token = db.Column(db.Unicode(255), nullable=False)

    @classmethod
    def get_authorize_url(cls, user):
        uid = get_uid()
        cache.set(uid, user.id, 60)
        url = cls.expand_url("oauth", "authorize")
        query = requests.compat.urlencode(dict(
            client_id=config.appid,
            response_type="code",
            redirect_uri=config.callback,
            state=uid
        ))
        return url + "?" + query

    @classmethod
    def authorize(cls, state, code):
        user_id = cache.get(state)
        if user_id is None:
            abort(404)
        user = User.query.get_or_404(user_id)
        url = cls.expand_url("oauth", "token")
        resp = cls.session.post(url, data=dict(
            client_id=config.appid, client_secret=config.secret,
            code=code, grant_type="authorization_code",
            redirect_uri=config.callback
        ))
        if user.gitlab_account is not None:
            db.session.delete(user.gitlab_account)

        respjson = resp.json()
        user.gitlab_account = cls(refresh_token=respjson["refresh_token"])
        user.gitlab_account.set_token(respjson)
        user.gitlab_account.sync()

        cache.delete(state)
        return user

    @classmethod
    def expand_url(cls, prefix, uri):
        return "/".join([
            config.base_url.rstrip("/"),
            prefix.strip("/"), uri.lstrip("/")
        ])

    def call(self, method, uri, **kwargs):
        url = self.expand_url("api/v3", uri)
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = "Bearer {0}".format(self.access_token)
        caller = getattr(self.session, method)
        resp = caller(url, headers=headers, **kwargs)
        return resp.json()

    @property
    def token_cache_key(self):
        return "oauth-gitlab-{0}".format(self.id)

    @property
    def access_token(self):
        return cache.get(self.token_cache_key) or self.get_token()

    def get_token(self):
        info = self.call("get", "oauth/token")
        return self.set_token(info)

    def set_token(self, info):
        token = info["access_token"]
        cache.set(self.token_cache_key, token, timeout=info.get("expires_in"))
        return token

    def sync(self):
        info = self.call("get", "user")
        self.username = info["username"]
        self.email = info["email"]
