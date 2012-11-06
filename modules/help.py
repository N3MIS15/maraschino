from flask import render_template
from maraschino import app
from maraschino.noneditable import *
from maraschino.tools import requires_auth


@app.route('/xhr/help/')
@app.route('/xhr/help/<page>/')
@requires_auth
def xhr_help(page='intro'):
    return render_template('/help/help-'+page+'.html')
