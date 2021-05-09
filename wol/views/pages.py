from flask import Blueprint, render_template

from ..logic.crud import get_all_targets

pages = Blueprint('web', __name__, template_folder='../templates')


@pages.route('/targets/', methods=['GET'])
def get_web_targets():
    targets = get_all_targets()
    return render_template('targets.html', targets=targets)
