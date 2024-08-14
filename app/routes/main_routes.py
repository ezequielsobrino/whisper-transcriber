from flask import Blueprint, render_template

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/v2/')
def index_v2():
    return render_template('transcriptions_v2.html')
