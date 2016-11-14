from flask import Blueprint, jsonify

from .forms import CreateUserForm
from ..ldap import ldap


api = Blueprint("staff-api", __name__, template_folder=".")


@api.route("/staff/new", methods=["POST"])
def create_new_staff():
    form = CreateUserForm()
    if form.validate_on_submit():
        succeeded = ldap.create_user(
            form.username.data.strip(),
            form.given_name.data.strip(),
            form.surname.data.strip(),
            form.password.data.strip()
        )
        if succeeded:
            return jsonify(succeeded=True)
    return jsonify(form.errors)
