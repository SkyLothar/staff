from flask_wechat import WechatCipher
from flask_wechat.qyh import QYHMixin

from ..ext import db, cache
from ..mixin import BasicMixin
from ..utils import get_uid

from . import config


class WechatApp(BasicMixin, QYHMixin, db.Model):
    __tablename__ = "wechat_app"

    name = db.Column(db.Unicode(255), unique=True, nullable=False)
    with_contact_privilege = db.Column(db.Boolean, default=False)

    uid = db.Column(
        db.Unicode(32),
        default=get_uid, nullable=False, index=True
    )
    agentid = db.Column(db.Integer, nullable=False)

    secret = db.Column(db.Unicode(128), nullable=False)
    token = db.Column(db.Unicode(128), nullable=False)
    aeskey = db.Column(db.Unicode(128), nullable=False)

    def __str__(self):
        return str(self.name)

    @property
    def cipher(self):
        if not hasattr(self, "_cipher"):
            self._cipher = WechatCipher(config.corpid, self.token, self.aeskey)
        return self._cipher

    @property
    def cache_key(self):
        return "wa-at-{0}".format(self.secret)

    @property
    def auth_params(self):
        return dict(corpid=config.corpid, corpsecret=self.secret)

    def get_access_token(self):
        return cache.get(self.cache_key)

    def set_access_token(self, access_token, expires_in):
        cache.set(self.cache_key, access_token, timeout=expires_in)

    def sync_user(self, user):
        if not self.with_contact_privilege:
            raise ValueError("i can't do that... dude")

        info = self.find_user(user.wx_user_id)
        user.name = info["name"]
        user.avatar = info["avatar"]
        user.email = info["email"]
        user.active = info["status"] == 1

    def send_news(self, to_user, *articles):
        if len(articles) == 0:
            raise ValueError("give me somthing to send")
        return super(WechatApp, self).send_news(
            self.agentid,
            to_user,
            *articles
        )
