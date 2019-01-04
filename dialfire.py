#!/usr/bin/env python
# encoding: utf-8
#
# Dialfire API
# http://apidoc.dialfire.com/#!/
#
# Dialfire Support
# https://www.dialfire.com/support/en/faq/14000114396#14000046720
#


import os
from json import dumps
import requests


class Dialfire():

    URL = "https://api.dialfire.com/api/{}"

    def __init__(self, campaign_id=None, campaign_token=None, tenant_id=None, tenant_token=None, task_name=None):
        self.tenant_id = tenant_id
        self.tenant_token = tenant_token
        self.campaign_id = campaign_id
        self.campaign_token = campaign_token
        self.task_name = task_name

    def __post_request(self, parts, data):
        headers = {
            'Authorization': 'Bearer {}'.format(self.campaign_token)
        }
        url = self.URL.format('/'.join(parts))
        req = requests.post(url, data=data, headers=headers)
        return req.json()

    def get_contacts_index(self):
        '''
        POST /api/campaigns/{campaign_id}/contacts/filter 
        search for contacts inside a campaign
        '''
        url_parts = ['campaigns', self.campaign_id, 'contacts', 'filter']
        return self.__post_request(url_parts, data=dumps({})).get('hits')

    def get_contacts_flat(self, ids=None):
        '''
        POST /api/campaigns/{campaign_id}/contacts/flat_view 
        get the flat view for a whole batch of contact records
        '''
        url_parts = ['campaigns', self.campaign_id, 'contacts', 'flat_view']
        return self.__post_request(url_parts, data=dumps(list(ids)))

    def create_contact(self, data):
        url_parts = ['campaigns', self.campaign_id,
                     'tasks', self.task_name, 'contacts', 'create']
        return self.__post_request(url_parts, data=dumps(data)).get('data', {}).get('$id')


def connect():
    session = None
    try:
        task_name = os.environ.get('DIALFIRE_TASK_NAME')
        tenant_id = os.environ.get('DIALFIRE_TENANT_ID')
        tenant_token = os.environ.get('DIALFIRE_TENANT_TOKEN')
        campaign_id = os.environ.get('DIALFIRE_CAMPAIGN_ID')
        campaign_token = os.environ.get('DIALFIRE_CAMPAIGN_TOKEN')

        if task_name and ((tenant_id and tenant_token)
                          or (campaign_id and campaign_token)):
            return Dialfire(tenant_id=tenant_id,
                            tenant_token=tenant_token,
                            campaign_id=campaign_id,
                            campaign_token=campaign_token,
                            task_name=task_name)
        else:
            raise UserWarning(
                'Environ must have Dialfire TENANT or CAMPAIGN credentials')

    except UserWarning as exception:
        pass
    return session
