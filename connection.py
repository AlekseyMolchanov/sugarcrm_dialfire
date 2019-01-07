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
        
        auth=Session.local_auth

        if os.environ.get('CIRCLECI'):
            auth=Session.remote_auth

        session = Session(url, username, password,
                          proxies=proxies,
                          auth=auth)
        

    except KeyError as exception:
        logger.error(exception)
    except Exception as exception:
        logger.critical(exception)
    return session
