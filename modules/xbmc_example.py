from flask import Flask, render_template
from Maraschino import app
from maraschino.noneditable import *
import maraschino.logger as logger
import jsonrpclib

@app.route('/xhr/xbmc_example') # The route Maraschino uses to run the function (Maraschino load '/xhr/ModuleName' as the modules default location)
@requires_auth # Use Maraschino's basic Authentication
def xhr_xbmc_example():
    return render_template('xbmc_example.html') # Render the template for our module

@app.route('/xhr/xbmc_example/ping') # The route we will use to ping the server
@requires_auth
def xhr_xbmc_ping():
    xbmc = jsonrpclib.Server(server_api_address()) # Use XBMC server defined in server settings
    
    try:
        logger.log('XBMC_EXAMPLE :: Pinging XBMC', 'INFO') # Log what we are doing
        ping = xbmc.JSONRPC.Ping() # The actual ping request
    except:
        logger.log('XBMC_EXAMPLE :: Ping Failed', 'ERROR')
        ping = 'Ping Failed'

    return render_template('xbmc_example.html', result = ping) # Render the result of ping to our template



