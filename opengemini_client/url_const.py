"""
define url const class
"""


class UrlConst:
    """
    url const class
    """
    PING = '/ping'
    QUERY = '/query'
    STATUS = '/status'
    WRITE = '/write'

    no_auth_required = {
        '/ping': {
            'GET',
            'HEAD'
        },
        '/query': {
            'OPTIONS'
        },
        '/status': {
            'GET',
            'HEAD'
        }
    }
