# -*- coding: utf-8 -*-
"""Google Cloud Messaging service

Documentation is available on the Android Developer website:

https://developer.android.com/google/gcm/index.html
"""

from functools import partial

import requests

from .utils import chunk, json_dumps
from .exceptions import GCMError, GCMAuthError


__all__ = (
    'send',
    'send_bulk',
)


class Request(object):
    """Wrapper around requests session bound to GCM config."""
    def __init__(self, config):
        self.api_key = config.get('GCM_API_KEY')
        self.url = config.get('GCM_URL')

        self.session = requests.Session()
        self.session.auth = ('key', self.api_key)
        self.session.headers.update({
            'Content-Type': 'application/json',
        })

    def __call__(self, data, **options):
        return self.session.post(self.url, data, **options)


def create_payload(registration_ids,
                   data,
                   collapse_key=None,
                   delay_while_idle=None,
                   time_to_live=None):
    """Return notification payload in JSON format."""
    if not isinstance(registration_ids, (list, tuple)):
        registration_ids = [registration_ids]

    payload = {'registration_ids': registration_ids}

    if not isinstance(data, dict):
        data = {'message': data}

    if data is not None:
        payload['data'] = data

    if collapse_key is not None:
        payload['collapse_key'] = collapse_key

    if delay_while_idle is not None:
        payload['delay_while_idle'] = delay_while_idle

    if time_to_live is not None:
        payload['time_to_live'] = time_to_live

    return json_dumps(payload)


    """Sends a GCM notification to a single token."""
def send(registration_id, data, config, request=None, **options):
    if not config['GCM_API_KEY']:
        raise GCMAuthError('Missing GCM API key. Cannot send notifications.')

    if request is None:
        request = Request(config)

    payload = create_payload(registration_id, data, **options)
    response = request(payload)
    results = response.json()

    if 'failure' in results and results.get('failure'):
        raise GCMError(results)

    return results


    """Sends a GCM notification to one or more tokens."""
def send_bulk(registration_ids, data, config, request=None, **options):
    if request is None:
        request = Request(config)

    max_recipients = config.get('GCM_MAX_RECIPIENTS')

    results = []
    for _registration_ids in chunk(registration_ids, max_recipients):
        results.append(send(_registration_ids,
                            data,
                            config,
                            request=request,
                            **options))

    return results
