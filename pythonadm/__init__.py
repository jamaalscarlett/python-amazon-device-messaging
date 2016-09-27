import datetime
import hashlib
import json
import requests

from base64 import standard_b64encode

AMAZON_TOKEN_URL = 'https://api.amazon.com/auth/O2/token'
AMAZON_REGISTRATION_URL = 'https://api.amazon.com/messaging/registrations/'
X_AMAZON_ACCEPT_TYPE = 'com.amazon.device.messaging.ADMSendResult@1.0'
X_AMAZON_TYPE_VERSION = 'com.amazon.device.messaging.ADMMessage@1.0'


def calculate_md5_checksum(data):
    utf8_data = {}
    utf8_keys = []

    keys = data.keys()
    utf8_keys = [key.encode('utf-8') for key in keys]

    for index, key in enumerate(keys):
        utf8_data[utf8_keys[index]] = data[key].encode('utf-8')

    utf8_keys.sort()
    utf8_string = ""

    for key in utf8_keys:
        utf8_string = utf8_string + key + ':' + utf8_data[key]
        if key != utf8_keys[-1]:
            utf8_string = utf8_string + ','
    md5_checksum = standard_b64encode(hashlib.md5(utf8_string).digest())
    return md5_checksum


def process_result(registration_id, result_data):
    processed_result = {'registration_id': registration_id}
    if 'reason' in result_data:
        processed_result['error'] = result_data.get('reason')
    elif registration_id != result_data.get('registrationID'):
        canonical_id = result_data.get('registrationID')
        processed_result['canonical_id'] = canonical_id
    return processed_result


class ConfigurationError(Exception):
    pass


class AmazonDeviceMessaging:
    def __init__(self, client_secret=None, client_id=None,
                 registration_url=AMAZON_REGISTRATION_URL,
                 token_url=AMAZON_TOKEN_URL):
        if not client_secret or not client_id:
            raise ConfigurationError
        self.client_secret = client_secret
        self.client_id = client_id
        self.registration_url = registration_url
        self.token_url = token_url
        self.retry_after = None

    def request_token(self):
        try:
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = {'grant_type': 'client_credentials',
                    'scope': 'messaging:push',
                    'client_secret': self.client_secret,
                    'client_id': self.client_id
                    }
            result = requests.post(self.token_url, headers=headers, data=data)
            token_data = result.json()
            return token_data
        except Exception:
            return None

    def send_message(self, registration_id, token_data, message=None,
                     consolidation_key=None, expires_after=None, data={},
                     send_md5=False):
        if self.retry_after:
            if self.retry_after > datetime.datetime.now():
                return {'registration_id': registration_id,
                        'error': 'Messages can not be sent until %s' % str(self.retry_after)}
            else:
                self.retry_after = None
        url = '%s%s/messages' % (self.registration_url, registration_id)
        headers = {'Content-Type': 'application/json',
                   'Accept': 'application/json',
                   'x-amzn-type-version': X_AMAZON_TYPE_VERSION,
                   'x-amzn-accept-type': X_AMAZON_ACCEPT_TYPE,
                   'Authorization': "Bearer " + token_data.get('access_token',
                                                               None)}
        if message:
            data['message'] = message

        payload = {'data': data}
        if consolidation_key:
            payload['consolidation_key'] = consolidation_key
        if expires_after:
            payload['expiresAfter'] = expires_after
        if send_md5:
            payload['md5'] = calculate_md5_checksum(data)

        result = requests.post(url, headers=headers, data=json.dumps(payload))
        status_code = result.status_code
        try:
            retry = int(datetime.datetime.now().strftime('%s')) + int(result.headers.get('Retry-After'))
            self.retry_after = datetime.datetime.fromtimestamp(retry)
        except ValueError:
            retry = datetime.datetime.strptime(result.headers.get('Retry-After'), '%a, %d %b %Y %H:%M:%S %Z')
            self.retry_after = retry
        except TypeError:
            pass
        processed_result = {'registration_id': registration_id}
        if status_code == 403:
            processed_result['error'] = 'HTTP request forbidden'
        elif status_code == 408:
            processed_result['error'] = 'HTTP request timeout'
        else:
            result_data = result.json()
            if 'reason' in result_data:
                processed_result['error'] = result_data.get('reason')
            elif registration_id != result_data.get('registrationID'):
                canonical_id = result_data.get('registrationID')
                processed_result['canonical_id'] = canonical_id
        return processed_result
