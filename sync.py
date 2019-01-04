#!/usr/bin/env python
# encoding: utf-8

from sugarcrm import Task
from connection import connect as sugar_connect
from dialfire import connect as dial_connect
from storage import Stor
from pprint import pprint
from functools import partial

import logging
logging.basicConfig(level=logging.DEBUG)


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
                              'email1'
                              ]}
        tasks = self.sugar_session.get_entry_list(query, links=links)
        for task in tasks:
            if hasattr(task, 'contacts'):
                __tasks_with_contact.append(task)
        return __tasks_with_contact


    def already_exported(self, task):
        return self.stor.has(task.id)

    def prepare_export_data(self, task):
        contact = task.contacts[0]
        export_data = {
            'NameFirst': task.name,
            '$phone': (contact.phone_work or contact.phone_other or ""),
            'first_name': contact.first_name,
            'last_name': contact.last_name,
            'Gender': contact.salutation,
            'POSITION': contact.title,
            'street': contact.primary_address_street,
            'city': contact.primary_address_city,
            'postcode': contact.primary_address_postalcode,
            'Mail': contact.email1,
            '$ref': task.id
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

    sugar_session = sugar_connect()
    diall_session = dial_connect()

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

    sync = SyncCallTaskApi(diall_session, sugar_session)
    for task in sync.get_tasks():
        if not sync.already_exported(task):
            data = sync.prepare_export_data(task)
            contact_id = sync.diall_session.create_contact(data)
            sync.stor.append(contact_id, task.id)

    return 0

if __name__ == "__main__":
    exit(main())
