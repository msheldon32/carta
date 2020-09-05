import csv
import random
import json
import os
import datetime
import re
import xlrd
import carta
import carta_review_schemes
import dill

DEFAULT_DATETIME_REP = "%m/%d/%Y, %H:%M:%S"

class CsvDataSource(carta.DataSource):
        """Pulls/pushes data from a csv file. Uses header and standard delimitation settings. 
        """
        def __init__(self, file_name, read_only=True):
                super().__init__(read_only)
                self.file_name = file_name
        
        def pull_data(self):
                data_matrix = []
                data_dict   = {}
                with open(self.file_name) as csvfile:
                        csv_reader = csv.reader(csvfile)
                        data_matrix = [row for row in csv_reader]
                header = data_matrix[0]
                data_matrix = data_matrix[1:]

                num_fields = len(header)

                for row in data_matrix:
                        if len(row) != num_fields:
                                raise Exception("Invalid csv file.")
                
                for i, field_name in enumerate(header):
                        data_dict[field_name] = [row[i] for row in data_matrix]
                return data_dict
        
        def push_data(self, data_dict):
                assert (not self.read_only)
                header = []
                data_matrix = []
                for i, field_name in enumerate(data_dict.keys()):
                        header.append(field_name)
                        for j, val in enumerate(data_dict[field_name]):
                                if i == 0:
                                        data_matrix.append([val])
                                else:
                                        data_matrix[j].append(val)
                data_matrix = [header] + data_matrix
                with open(self.file_name, "w") as csvfile:
                        csvwriter = csv.writer(csvfile)
                        for row in data_matrix:
                                csvwriter.writerow(row)
        
        def name(self):
                return self.file_name.split("/")[-1]
        
        def get_source_str(self):
                return self.file_name

class ExcelDataSource(carta.DataSource):
        """Read-only data source for Excel files.
        """
        def __init__(self, file_name):
                super().__init__(True)
                self.file_name = file_name
        
        def pull_data(self):
                data_matrix = []
                data_dict   = {}
                excel_source = xlrd.open_workbook(self.file_name)
                excel_sheet = excel_source.sheet_by_index(0)
                
                for i in range(0, excel_sheet.nrows):
                        row = []
                        for j in range(0, excel_sheet.ncols):
                                row.append(excel_sheet.cell(i,j).value)
                        data_matrix.append(row)
                header = data_matrix[0]
                data_matrix = data_matrix[1:]
                for i, field_name in enumerate(header):
                        data_dict[field_name] = [row[i] for row in data_matrix]
                return data_dict
        
        def push_data(self, data_dict):
                raise Exception("Pushing data not supported with excel.")
        
        def name(self):
                return self.file_name.split("/")[-1]
        
        def get_source_str(self):
                return self.file_name
        
def save_data(data_sets, deck_list, review_list, output_file_location):
        """Creates a JSON file describing all relevant objects.
        """
        data_sources = [data_set.data_source for data_set in data_sets]
        
        full_dict = {
                "data_sources": data_sources,
                "data_set": data_sets,
                "decks": deck_list,
                "reviews": review_list
        }

        dill.dump(full_dict, open(output_file_location, "wb"))

def load_from_file(input_file_location):
        """RECALLS the JSON file from save_data() and creates objects from the existing data.
        """

        return dill.load(open(input_file_location, "rb"))
