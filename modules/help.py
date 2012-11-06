from flask import render_template
from maraschino import app
from maraschino.noneditable import *
from maraschino.tools import requires_auth


@app.route('/xhr/help')
@requires_auth
def xhr_help():
    return render_template('/help/help-intro.html')

@app.route('/xhr/help/intro')
@requires_auth
def xhr_help_intro():
    return render_template('/help/help-intro.html')

@app.route('/xhr/help/modules')
@requires_auth
def xhr_help_modules():
    return render_template('/help/help-modules.html')