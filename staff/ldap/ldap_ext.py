from ldap3 import Server, Connection, utils, ALL, HASHED_SALTED_MD5


class LDAP(object):
    def __init__(self):
        self._server = None
        self._base_dn = None

    def init_app(self, app):
        self._server = Server(app.config["LDAP_SERVER"], get_info=ALL)
        self._base_dn = app.config["LDAP_BASE_DN"]
        self._admin_password = app.config["LDAP_ADMIN_PWD"]
        self._gid = app.config["LDAP_DEFUALT_GID"]
        self._home_template = app.config["LDAP_HOME_TEMPLATE"]
        self._mail_template = app.config["LDAP_MAIL_TEMPLATE"]

    def get_connection(self):
        dn = "cn=admin,{0}".format(self._base_dn)
        conn = Connection(self._server, user=dn, password=self._admin_password)
        conn.start_tls()
        binded = conn.bind()
        if binded:
            return conn
        return None

    def get_user_dn(self, username):
        dn = "cn={0},ou=users,{1}".format(username, self._base_dn)
        return dn

    def check_password(self, username, password, connection=None):
        connection = connection or self.get_connection()
        dn = self.get_user_dn(username)
        return connection.rebind(user=dn, password=password)

    def create_user(self, username, given_name, surname, password):
        if self.is_user_exists(username):
            return self.change_password(username, password)

        connection = connection = self.get_connection()
        dn = self.get_user_dn(username)
        salted_password = utils.hashed.hashed(HASHED_SALTED_MD5, password)
        uid = self.get_next_uid(connection)

        return connection.add(
            dn, ["inetOrgPerson", "posixAccount", "top"],
            {
                "cn": username,
                "gidNumber": self._gid,
                "homeDirectory": self._home_template.format(username=username),
                "sn": surname,
                "givenName": given_name,
                "uid": username,
                "uidNumber": uid,
                "l": "active",
                "loginShell": "/bin/bash",
                "mail": self._mail_template.format(username=username),
                "userPassword": salted_password
            }
        )

    def get_next_uid(self, connection):
        connection.search(
            "ou=users,{0}".format(self._base_dn),
            "(cn=*)",
            attributes="uidNumber"
        )
        max_uid = max([
            resp["attributes"]["uidNumber"]
            for resp in connection.response
        ])
        return max_uid + 1

    def is_user_exists(self, username, connection=None):
        dn = self.get_user_dn(username)
        connection = connection or self.get_connection()
        connection.search(dn, "(cn={0})".format(username))
        count = len(connection.response or [])
        return count > 0
