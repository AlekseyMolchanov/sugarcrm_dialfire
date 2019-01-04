#!/usr/bin/env python
# encoding: utf-8


import os
from sugarcrm import Session


def connect():
    session = None
    try:
        url  = os.environ['SUGAR_CRM_URL']
        username = os.environ['SUGAR_CRM_USERNAME']
        password = os.environ['SUGAR_CRM_PASSWORD']
        session = Session(url, username, password)
    except KeyError as exception:
        pass
    return session
