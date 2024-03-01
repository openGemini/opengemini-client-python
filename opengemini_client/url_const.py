"""
define url const class
"""


class UrlConst:
    """
    url const class
    """
    URL_PING = '/ping'
    URL_QUERY = '/query'
    URL_STATUS = '/status'
    URL_WRITE = '/write'

    no_auth_required = {
        URL_PING: {
            'GET': {},
            'HEAD': {}
        },
        URL_QUERY: {
            'OPTIONS': {}
        },
        URL_STATUS: {
            'GET': {},
            'HEAD': {}
        }
    }
