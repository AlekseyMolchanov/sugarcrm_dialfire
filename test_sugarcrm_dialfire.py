#!/usr/bin/env python
# encoding: utf-8

import os
import pytest

from sugarcrm import Task, Contact

from connection import connect as sugar_connect
from dialfire import connect as dial_connect
from sync import SyncCallTaskApi

import generate

@pytest.fixture(scope="module")
def state(request):
    __state = {'account': None}
    def resource_teardown():

        sugar_session = sugar_connect()

        current = sugar_session.get_entry(Task.module, __state.get('task_1').id)
        current.deleted = True
        current = sugar_session.set_entry(current)

        current = sugar_session.get_entry(Task.module, __state.get('task_2').id)
        current.deleted = True
        current = sugar_session.set_entry(current)

        current = sugar_session.get_entry(Task.module, __state.get('task_3').id)
        current.deleted = True
        current = sugar_session.set_entry(current)

        
    request.addfinalizer(resource_teardown)

    return __state


@pytest.fixture(scope="module")
def sessions(request):
    sugar_session = sugar_connect()
    assert sugar_session
    
    diall_session = dial_connect()
    assert diall_session

    return diall_session, sugar_session


def fake_contact_data():
        
    primary_address_city = next(generate.generate_City())
    primary_address_street = next(generate.generate_Street())

    phones = generate.generate_Phone()

    first_name, last_name, _, salutation = generate.generate_person()
    
    return dict(
        first_name=first_name,
        last_name=last_name,
        title=generate.generate_Position(),
        primary_address_street=primary_address_street,
        primary_address_city=primary_address_city,
        primary_address_postalcode=generate.generate_ZIP(),
        phone_home=next(phones),
        phone_mobile=next(phones),
        phone_other=next(phones),
        phone_work=next(phones),
        salutation=salutation,
        email1=generate.generate_Email(first_name, last_name)
    )


def fake_task_data(name, contact_id):

        date_start, date_end = generate.generate_dates_range()
        now = generate.generate_now()
    
        return dict(
            name="Task: {}".format(name),
            description="Some task description",
            date_start=date_start, 
            date_end=date_end,
            date_modified=now,
            priority='Medium',                      
            contact_id=contact_id,
        )

def test_call_in_task_name(sessions, state):

    diall_session, sugar_session = sessions

    obj = Contact(**fake_contact_data())
    contact = sugar_session.set_entry(obj)
    state['contact'] = contact
    
    obj = Task(**fake_task_data('Some task without keyword in name', contact.id))
    task = sugar_session.set_entry(obj)
    state['task_1'] = task

    obj = Task(**fake_task_data('Some task with Call keyword in name', contact.id))
    task = sugar_session.set_entry(obj)
    state['task_2'] = task

    obj = Task(**fake_task_data('Some task with CALL keyword in name', contact.id))
    task = sugar_session.set_entry(obj)
    state['task_3'] = task
    
    sync = SyncCallTaskApi(diall_session, sugar_session)
    tasks = sync.get_tasks()
    assert tasks
    for task in tasks:
        assert 'call' in task.name.lower()


def test_task_eq_data(sessions, state):
    diall_session, sugar_session = sessions
    sync = SyncCallTaskApi(diall_session, sugar_session)
    tasks = sync.get_tasks()
    assert tasks
    for task in tasks:
        
        data_to_export = sync.prepare_export_data(task)
        
        assert not sync.already_exported(data_to_export['$ref'])
        
        
        contact_id = sync.diall_session.create_contact(data_to_export)
        sync.stor.append(contact_id, task.id)

        found_diall_contact_data = diall_session.get_contacts_flat([contact_id])
        contact_data = found_diall_contact_data[0]
        esported_data = {
            'NameFirst': contact_data.get('NameFirst'),
            '$phone': contact_data.get('$phone'),
            'first_name': contact_data.get('first_name'),
            'last_name': contact_data.get('last_name'),
            'Gender': contact_data.get('Gender'),
            'POSITION': contact_data.get('POSITION'),
            'street': contact_data.get('street'),
            'city': contact_data.get('city'),
            'postcode': contact_data.get('postcode'),
            'Mail': contact_data.get('Mail'),
            '$ref': contact_data.get('$ref')
        }
        for k,v in data_to_export.items():
            assert esported_data.get(k) == v

