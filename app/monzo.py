
class UnsupportedWebhook(Exception):
    pass


SUPPORTED_WEBHOOKS = [
    'transaction.created',
]


def check_type(data):
    if data['type'] not in SUPPORTED_WEBHOOKS:
        raise UnsupportedWebhook


def get_payee_name(data):
    name_ = data['data']['merchant']['name']
    return name_


def get_emoji(data):
    # Try and get the emoji
    try:
        emoji = data['data']['merchant']['emoji']
    except KeyError:
        emoji = ''
    return emoji


def get_tags(data):
    # Try and get the suggested tags
    try:
        suggested_tags = data['data']['merchant']['metadata']['suggested_tags']
    except KeyError:
        suggested_tags = ''

    return suggested_tags


def get_create_date(data):
    return data['data']['created']


def get_amount(data):
    return data['data']['amount']


