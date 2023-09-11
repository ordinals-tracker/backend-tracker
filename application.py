from flask_cors import CORS
import time
import utils
from flask import Flask, request, jsonify

application = Flask(__name__)

cors = CORS(application)
cors = CORS(application, resources={r"/*": {"origins": "*"}})

@application.route('/')
def healthcheck():
    return {"healthcheck": "ok"}

@application.route('/track/<wallets>', methods=['GET'])
def get_all_data(wallets):

    return jsonify({
        "ordinals-track": utils.get_me_activity(wallets.split(","))
    })

@application.route('/holdings/<wallets>', methods=['GET'])
def get_all_holdings(wallets):

    holdings,total_balance,usd_total_balance = utils.get_holdings(wallets.split(","))
    return jsonify({
        "holdings": holdings,
        "total_balance": total_balance,
        "usd_total_balance": usd_total_balance
    })

if __name__ == '__main__':
    application.run()
