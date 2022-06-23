#!/usr/bin/env python3
"""
export HTTP_AUTH_USERNAME='<USERNAME>'
export HTTP_AUTH_PASSWORD='<PASSWORD>'
"""
import os
import json
from base64 import b64encode


if __name__ == '__main__':
    username = os.environ['HTTP_AUTH_USERNAME']
    password = os.environ['HTTP_AUTH_PASSWORD']

    creds = f'{username}:{password}'
    creds = creds.encode('ascii')
    creds = b64encode(creds)
    creds = creds.decode('ascii')

    basic_auth = {
        'Authorization': f'Basic {creds}'
    }

    print(json.dumps(basic_auth, indent=4, default=str))




