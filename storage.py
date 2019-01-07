#!/usr/bin/env python
# encoding: utf-8

import os
import csv
from datetime import datetime


class Stor(object):

    FOLDER = 'db'
    DT_FORMAT = "%Y-%m-%dT%H:%M:%S.%f.csv"
    CSV_FORMAT = dict(
        delimiter=',',
        quotechar='\'',
        lineterminator='\n',
        quoting=csv.QUOTE_NONNUMERIC,
    )
    CSV_FIELDNAMES = ['id', 'ref']

    def __init__(self, init_data):
        self.__data = {}
        self.init_data = init_data

        if not os.path.isdir(self.FOLDER):
            self.init_run()
        self.fill()

    def __generate_name(self):
        return datetime.now().strftime(self.DT_FORMAT)

    def __store(self, data):
        filepath = os.path.join(self.FOLDER, self.__generate_name())
        with open(filepath, 'w') as csvfile:
            csv_writer = csv.writer(csvfile, **self.CSV_FORMAT)
            for row in data:
                csv_writer.writerow(row)

    def init_run(self):
        '''
        create storage folder and save 
        iterable function init_data result 
        into csv
        '''
        os.makedirs(self.FOLDER)
        data = self.init_data()
        self.__store(data)

    def __walk(self):
        for path, _, files in os.walk(self.FOLDER):
            for each in files:
                filepath = os.path.join(path, each)
                yield filepath

    def fill(self):
        '''
        read stored data from 
        storage folder into index
        '''
        for filepath in self.__walk():
            with open(filepath, 'r') as csvfile:
                dialect = csv.Sniffer().sniff(csvfile.read(1024))
                csvfile.seek(0)
                reader = csv.DictReader(
                    csvfile, dialect=dialect, fieldnames=self.CSV_FIELDNAMES)
                for row in reader:
                    call_id, task_id = row['id'], row['ref']
                    self.__data[task_id] = call_id

    def append(self, call_id, task_id):
        self.__store([
            [call_id, task_id]
        ])

    def has(self, task_id):
        return self.__data.get(task_id)
