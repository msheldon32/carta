# testing script for carta

import unittest
import carta_local

class TestCsvDataSource(unittest.TestCase):
    def setUp(self):
        self.standard_csv = carta_local.CsvDataSource("Testing/csv_test.csv", read_only=False)
        
    # a csv data source object should be able to:
    #     - pull data successfully from a standard csv file
    def test_standard_csv(self):
        data_dict_test = self.standard_csv.pull_data()
        self.assertTrue("field_one" in data_dict_test.keys())
        self.assertTrue("field_two" in data_dict_test.keys())
        self.assertTrue("11" in data_dict_test["field_one"])
        self.assertTrue("22" in data_dict_test["field_two"])
        
    #     - fail upon pulling data from a nonstandard csv file
    def test_nonstandard_csv(self):
        nonstandard_csv = carta_local.CsvDataSource("Testing/nonstdcsv_test.csv")
        with self.assertRaises(Exception):
            nonstandard_csv.pull_data()
    
    #     - push data to said csv file successfully
    def test_push_data(self):
        self.standard_csv.push_data({"field_three": ["13", "23"], "field_four": ["14", "24"]})
        duplicate_csv_obj = carta_local.CsvDataSource("Testing/csv_test.csv")
        duplicate_dict_test = duplicate_csv_obj.pull_data()
        self.assertTrue("field_three" in duplicate_dict_test.keys())
        self.assertTrue("24" in duplicate_dict_test["field_four"])
        self.standard_csv.push_data({"field_one": ["11", "21"], "field_two": ["12", "22"]})
    
    #     - return a name properly
    def test_data_source_name(self):
        self.assertTrue(self.standard_csv.name() == "csv_test.csv")
        
class TestDataSet(unittest.TestCase):
    def setUp(self):
        test_data_source = carta_local.CsvDataSource("Testing/csv_test.csv")
        self.primary_data_set = carta.DataSet(data_source=test_data_source)
        
    # a data set object should be able to:
    #     - pull data from any kind of data source
    def test_pull_data(self):
        self.assertTrue("field_one" in self.primary_data_set.data_table.keys())
        self.assertTrue("22" in self.primary_data_set.data_table["field_two"])
        
    #     - update dynamically from a deck (if selected)
    #     - update children dynamically
    #           - [not implemented yet]
    #     - project properly
    def test_projection(self):
        proj = self.primary_data_set.project(["field_one"])
        self.assertTrue("field_one" in proj.data_table.keys())
        self.assertTrue("field_two" not in proj.data_table.keys())
    
    #     - override [] with integers
    #     - override [] with strings
    def test_override(self):
        field_one = self.primary_data_set["field_one"]
        self.assertTrue("11" in field_one)
        self.assertTrue("21" in field_one)
        self.assertTrue(len(field_one) == 2)
        first_row = self.primary_data_set[0]
        self.assertTrue("11" in first_row)
        self.assertTrue("12" in first_row)
        self.assertTrue(len(first_row) == 2)
