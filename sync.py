#!/usr/bin/env python
# encoding: utf-8
import os
import argparse
from sugarcrm import Task, Account
from connection import connect as sugar_connect
from dialfire import connect as dial_connect
from storage import Stor
from pprint import pprint
from functools import partial

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


class SyncCallTaskApi(object):
    def __init__(self, diall_session, sugar_session):
        self.diall_session = diall_session
        self.sugar_session = sugar_session
        self.stor = Stor(self.read_init_data)

    def get_tasks(self):
        __tasks_with_contact = []

        query = Task(name="%Call%")

        links = {'Contacts': ['id',
                              'title',
                              'salutation',
                              'first_name',
                              'last_name',
                              'phone_work',
                              'phone_other',
                              'primary_address_street',
                              'primary_address_city',
                              'primary_address_postalcode',
                              'email1',
                              'account_id',
                              'telefon_direkt_c',
                              'telefon_zentrale_firma_c'
                              ]}
        tasks = self.sugar_session.get_entry_list(query, links=links)
        
        logger.info('found {} tasks with "Call" in name'.format(len(tasks)))
        
        for task in tasks:
            if hasattr(task, 'contacts'):
                __tasks_with_contact.append(task)
            else:
                logger.warn('Found task without contacts "{}" [{}]'.format(task.name, task.id))

        return __tasks_with_contact

    def already_exported(self, _id):
        return self.stor.has(_id)

    def prepare_export_data(self, task):

        contact = task.contacts[0]

        account = self.sugar_session.get_entry(
            Account.module, contact.account_id)

        export_data = {
            'NameFirst': account.name if account else '',
            '$phone': (contact.phone_work or
                       contact.phone_other or
                       contact.telefon_direkt_c or
                       contact.telefon_zentrale_firma_c or
                       ""),
            'first_name': contact.first_name,
            'last_name': contact.last_name,
            'Gender': contact.salutation,
            'POSITION': contact.title,
            'street': contact.primary_address_street,
            'city': contact.primary_address_city,
            'postcode': contact.primary_address_postalcode,
            'Mail': contact.email1,
            '$ref': contact.id
        }
        return export_data

    def read_init_data(self):
        '''
        load from dialfire history and store in the file system
        '''
        index = self.diall_session.get_contacts_index()
        ids = map(lambda each: each.get('$id'), index)
        data = self.diall_session.get_contacts_flat(ids)
        return map(lambda each: [each['$id'], each['$ref']], data)


def main():

    parser = argparse.ArgumentParser(prog='sync.py')
    parser.add_argument(
        '--http-proxy', help='proxy HTTP example: http://10.10.1.10:3128', type=str)
    parser.add_argument(
        '--https-proxy', help='proxy HTTPs example: http://10.10.1.10:1080', type=str)
    parser.add_argument(
        '--no-proxy', help='disable proxy for host example: bestcrm.bechtle.intra', type=str)

    options = vars(parser.parse_args())

    proxies = {}
    if 'http_proxy' in options:
        proxies['http'] = options['http_proxy']

    if 'https_proxy' in options:
        proxies['https'] = options['https_proxy']

    if 'no_proxy' in options and options['no_proxy']:
        os.environ['NO_PROXY'] = options['no_proxy']

    sugar_session = sugar_connect()
    diall_session = dial_connect(proxies=(proxies or None))

    if not sugar_session:
        print ("\n######## Warning ########")
        print ("You must define Environment Variables:")
        print ("SUGAR_CRM_URL, SUGAR_CRM_USERNAME and SUGAR_CRM_PASSWORD")
        print ("###########################\n")
        exit(1)

    if not diall_session:
        print ("\n######## Warning ########")
        print ("You must define Environment Variables:")
        print ("DIALFIRE_CAMPAIGN_ID, DIALFIRE_CAMPAIGN_TOKEN and DIALFIRE_TASK_NAME")
        print ("###########################\n")
        exit(1)

    assigned_user_id = os.environ.get('SUGAR_CRM_ASSIGNED_USER_ID')

    sync = SyncCallTaskApi(diall_session, sugar_session)
    tasks = sync.get_tasks()

    if not tasks:
        logger.warning('No tasks with "call" in name')
    else:
        logger.info('found {} tasks'.format(len(tasks)))

    if not assigned_user_id:
        logger.warning('SUGAR_CRM_ASSIGNED_USER_ID is not set')
    else:
        logger.info('Used SUGAR_CRM_ASSIGNED_USER_ID: {}'.format(assigned_user_id))


    for task in tasks:
        if not assigned_user_id or assigned_user_id == task.assigned_user_id:

            data = sync.prepare_export_data(task)
            if not sync.already_exported(data['$ref']):
                contact_id = sync.diall_session.create_contact(data)
                sync.stor.append(contact_id, task.id)
                sync.stor.append(contact_id, data['$ref'])
                logger.info('sync {}'.format(data['$ref']))
            else:
                logger.info('already sync {}'.format(data['$ref']))

        elif assigned_user_id:
            logger.warn('Found task with deferent assigned_user_id "{}" [{}]'.format(task.name, task.id))

    return 0


if __name__ == "__main__":
    exit(main())
