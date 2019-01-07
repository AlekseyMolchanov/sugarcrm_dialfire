#!/usr/bin/env python
# encoding: utf-8


import os
from sugarcrm import Session
import logging

logger = logging.getLogger()

def connect(proxies=None):
    session = None
    try:
        url = os.environ['SUGAR_CRM_URL']
        username = os.environ['SUGAR_CRM_USERNAME']
        password = os.environ['SUGAR_CRM_PASSWORD']
        logger.debug('url:{} username:{} pass:{}'.format(url, username, password))
        
        session = Session(url, username, password,
                          proxies=proxies,
                          auth=Session.local_auth)
    except KeyError as exception:
        logger.error(exception)
    return session
