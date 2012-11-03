from flask import render_template
from maraschino import app
from maraschino.noneditable import *
from maraschino.tools import requires_auth


@app.route('/xhr/help')
@requires_auth
def xhr_help():
    return render_template('help_dialog.html')