import csv
import random
import json
import os
import datetime
import re
import xlrd
import carta
import carta_review_schemes

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
	data_source_info = []
	data_sources = []
	data_set_info = []
	deck_info = []
	review_info = []
	for i, data_set in enumerate(data_sets):
		if data_set.data_source not in data_sources:
			data_sources.append(data_set.data_source)
	for i, data_source in enumerate(data_sources):
		data_source_info.append({
			"num": i,
			"data_source_str": data_source.get_source_str(),
			"read_only": data_source.read_only
		})
	for i, data_set in enumerate(data_sets):
		data_set_info.append({
			"num": i,
			"data_source_num": data_sources.index(data_set.data_source),
			"depends_on_deck": data_set.depends_on_deck
		})
	for i, deck in enumerate(deck_list):
		deck_info.append({
			"num": i,
			"data_set_num": data_sets.index(deck.parent_data_set),
			"front_field": deck.front_side_field,
			"back_field": deck.back_side_field,
			"static": deck.static
		})
	review_status_info = []
	for i, review in enumerate(review_list):
		deck_num = deck_list.index(review.deck)
		review_info.append({
			"num": i,
			"deck_num": deck_num,
			"status_type": review.status_type,
			"review_type": review.review_type
		})
		child_review_status = review.review_statuses
		for j, review_status in enumerate(child_review_status):
			review_status_info.append({
				"num": j,
				"review_num": i,
				"deck_num": deck_num,
				"front_side": review_status.card.front_side,
				"back_side": review_status.card.back_side,
				"status": review_status.status,
				"status_datetime": review_status.status_datetime.strftime(DEFAULT_DATETIME_REP)
			})
	json_output = {
		"data_sources": data_source_info,
		"data_sets": data_set_info,
		"decks": deck_info,
		"reviews": review_info,
		"review_statuses": review_status_info
	}
	with open(output_file_location, "w") as json_out_file:
		json.dump(json_output, json_out_file)

def create_data_source(data_source_str, read_only):
	"""Reads in a new file and creates a DataSource object based off of the extention
	"""
	if os.path.splitext(data_source_str)[1] == ".csv":
		return CsvDataSource(data_source_str, read_only=read_only)
	elif os.path.splitext(data_source_str)[1] == ".xlsx":
		return ExcelDataSource(data_source_str)
	else:
		raise Exception("ERROR: data source type not recognized.")

def create_review_from_dict(deck_dict, review_dict):
	if review_dict["status_type"] == "leitner":
		return carta_review_schemes.DefaultLeitnerReview(deck_dict[review_dict["deck_num"]], review_dict["review_type"])
	elif review_dict["status_type"] == "streak":
		return carta_review_schemes.DefaultStreakReview(deck_dict[review_dict["deck_num"]], review_dict["review_type"])
	else:
		return carta.Review(deck_dict[review_dict["deck_num"]], carta.StatusScheme.DefaultScheme(), review_dict["review_type"])

def load_from_file(input_file_location):
	"""Recalls the JSON file from save_data() and creates objects from the existing data.
	"""
	data_dict = {}
	with open(input_file_location) as json_in_file:
		data_dict = json.load(json_in_file)
	data_dict["data_sources"] = {
		data_source["num"]: create_data_source(data_source["data_source_str"], data_source["read_only"])
			for data_source in data_dict["data_sources"]
	}
	data_dict["data_sets"] = {
		data_set["num"]: carta.DataSet(data_dict["data_sources"][data_set["data_source_num"]], data_set["depends_on_deck"], reload_from_file=True)
			for data_set in data_dict["data_sets"]
	}
	data_dict["decks"] = {
		deck["num"]: carta.Deck(data_dict["data_sets"][deck["data_set_num"]],
				   deck["front_field"], deck["back_field"],
				   carta.CardDisplayScheme(), deck["static"], reload_from_file=True)
			for deck in data_dict["decks"]
	}
	data_dict["reviews"] = {
		review["num"]: create_review_from_dict(data_dict["decks"], review)
			for review in data_dict["reviews"]
	}
	data_dict["review_statuses"] = {
		review_status["num"]: carta.CardReviewStatus(data_dict["decks"][review_status["deck_num"]].find_card_by_side(review_status["front_side"], review_status["back_side"]),
						 data_dict["reviews"][review_status["review_num"]], data_dict["reviews"][review_status["review_num"]].status_scheme,
						 status=review_status["status"], status_datetime=datetime.datetime.strptime(review_status["status_datetime"], DEFAULT_DATETIME_REP))
						 
			for review_status in data_dict["review_statuses"]
		
	}
	data_dict = {
		cat: [val for val in data_dict[cat].values()] for cat in data_dict.keys()
	}
	return data_dict
