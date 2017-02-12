import json
import logging

from decimal import Decimal
from flask import Flask, request, jsonify
from dateutil.parser import parse
import settings
import monzo
from monzo import UnsupportedWebhook, get_payee_name, get_emoji, get_tags
from ynab import YNAB

app = Flask(__name__, template_folder='../html', static_folder='../static')
app.config['DEBUG'] = settings.flask_debug

log = logging.getLogger(__name__)

if settings.sentry_dsn:
    from raven.contrib.flask import Sentry
    sentry = Sentry(app)


@app.route('/')
def route_index():
    return 'hello world'


@app.route('/monzo_webhook', methods=['POST'])
def route_webhook():
    data = json.loads(request.data.decode('utf8'))
    try:
        monzo.check_type(data)
    except UnsupportedWebhook:
        log.warning('Unsupported webhook type: %s' % data['type'])
        return ""

    ynab = YNAB(settings.ynab_username, settings.ynab_password, settings.ynab_budget)

    entities_account_id = ynab.get_account(settings.ynab_account).id
    entities_payee_id = ynab.get_payee(monzo.get_payee_name(data)).id

    suggested_tags = get_tags(data)
    emoji = get_emoji(data)

    transactions = ynab.create_transaction(
        account_id=entities_account_id,
        payee_id=entities_payee_id,
        date=parse(monzo.get_create_date(data)),
        memo="%s %s" % (emoji, suggested_tags),
        imported_payee=monzo.get_payee_name(data),
        amount= Decimal(monzo.get_amount(data)) / 100,
    )

    ynab.add_transactions(transactions)
    return jsonify(data)


if __name__ == "__main__":
    app.run()
