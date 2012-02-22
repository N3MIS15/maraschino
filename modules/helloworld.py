from flask import Flask, jsonify, render_template

from Maraschino import app
from settings import *
from maraschino.tools import *

@app.route('/xhr/helloworld')
@requires_auth
def xhr_helloworld():

    yes = get_setting_value('helloworld_bool') == '1'
    string = get_setting_value('helloworld_string')

    return render_template('helloworld.html',
        yes = yes,
        string = string,
    )
