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
        PING: {
            'GET': {},
            'HEAD': {}
        },
        QUERY: {
            'OPTIONS': {}
        },
        STATUS: {
            'GET': {},
            'HEAD': {}
        }
    }
