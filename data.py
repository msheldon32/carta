import csv
import random
import json
import os
import datetime
import re

class DataSource:
        """DataSource -
                Generic prototype for a data source. Allows for pushing and pulling data.
        """
        def __init__(self, read_only=True):
                self.read_only = read_only

        def pull_data(self):
                pass

        def push_data(self):
                pass

        def name(self):
                pass

        def get_source_str(self):
                pass

class DataSet:
        """DataSet -
                Manages a data set, including pulling/pushing from a DataSource object.

                Seperate on purpose from DataSource to ensure abstraction from the actual data structure.

                data_source (DataSource): DataSource object to communicate with the actual storage of the data
                data_table (dictionary): dictionary for caching the underlying data. [FIELD NAME]: [list of values]
                children (list): decks tied to DataSet
        """
        def __init__(self, data_source = None):
                self.data_source = data_source
                self.data_table = {}
                self.children = []
                
                self.update()

        def add_child(self, child):
                """Adds an object (with an update() method), usually a Deck, 
                		that depends on this object
                """
                self.children.append(child)

        def load_data_from_source(self):
                self.data_table = self.data_source.pull_data()
                for child in self.children:
                        child.update()

        def update(self):
                """Either update the data from the DataSource, or update the DataSource from the data based on the depends_on_deck member.
                """
                self.load_data_from_source()

        def get_data(self):
                return self.data_table

        def project(self, fields):
                """Returns a new DataSet with a subset of fields.
                """
                new_data_set = DataSet()
                new_data_table = {}
                for field in fields:
                        new_data_table[field] = self.data_table[field]
                new_data_set.data_table = new_data_table
                return new_data_set

        def  __getitem__(self, key):
                if type(key) == str:
                        return self.data_table[key]
                else:
                        return [ self.data_table[field_name][key] for field_name in self.data_table ]

        def header(self):
                return [key for key in self.data_table.keys()]

        def name(self):
                return self.data_source.name()
