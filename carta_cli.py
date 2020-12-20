import csv
import random
import json
import os
import datetime
import re

import review_scheme
import data
import deck
import carta_local

data_sets = []
decks = []

def input_review(deck):
	cards = deck.review_scheme.get_cards_to_review(deck)
	for card in cards:
		print ("Front side: {}".format(card.front_side))
		answer = input("Enter the answer: ")
		if answer == card.back_side:
			print ("Correct!")
			card.update_card(True)
		else:
			print ("Incorrect!")
			card.update_card(False)

def multichoice_review(deck):
	cards = deck.review_scheme.get_cards_to_review(deck)
	for card in cards:
		print ("Front side: {}".format(card.front_side))
		options = [card]
		while (len(options) < 4) or (len(options) == len(deck.cards)):
			new_card = deck.get_random_card()
			if new_card in options:
				continue
			options.append(new_card)
		random.shuffle(options)
		for i, option in enumerate(options):
			print ("{}: {}".format(i, option.back_side))
		
		answer = int(input("Enter the answer: "))
		answer = options[answer].back_side
		if answer == card.back_side:
			print ("Correct!")
			card.update_card(True)
		else:
			print ("Incorrect - the correct answer is: {}".format(card.back_side))
			card.update_card(False)

def view_all_cards(deck):
	for card in deck.cards:
		print("Front side: {}".format(card.front_side))
		print("Back side: {}".format(card.back_side))
		input()

def review_menu(deck):
	next_steps = {
		1: multichoice_review,
		2: input_review,
		3: view_all_cards,
		0: exit
	}
	print("1: Multiple Choice Review")
	print("2: Input Review")
	print("3: View all cards")
	selection = int(input("Enter your selection: "))
	if selection == 0:
		return
	next_steps[selection](deck)

def add_new_deck(data_set = None):
	if data_set is None:
		if len(data_sets) == 0:
			print ("Looks like there's no existing data sets")
		print ("Select the parent data set: ")	
		for i, data_set in enumerate(data_sets):
			print ("{}: {}".format(i+1, data_set.name()))
		selection = int(input("Enter your selection: "))
		data_set = data_sets[selection-1]
		
	print ("Features: ")
	features = data_set.header()
	for i, feature in enumerate(features):
		print ("{}: {}".format(i+1, feature))
	front_side_i = int(input("Enter the front side field: "))
	front_side = features[front_side_i-1]
	back_side_i  = int(input("Enter the back side field: "))
	back_side = features[back_side_i-1]
	print ("1: Leitner")
	print ("2: Streak")
	review_scheme_no = int(input("Enter the review scheme: "))
	review_scheme_obj = None
	if review_scheme_no == 1:
		review_scheme_obj = review_scheme.LeitnerReviewScheme()
	elif review_scheme_no == 2:
		review_scheme_obj = review_scheme.StreakReviewScheme()
	decks.append(deck.Deck(data_set, front_side, back_side, review_scheme_obj))

def deck_detail(deck):
	print ("-"*30)
	print ("Data Set: {}".format(deck.parent.name()))
	print ("Front Field: {}".format(deck.front_side))
	print ("Back Field: {}".format(deck.back_side))
	
	print ("1: review")
	print ("2: delete deck")
	print ("0: return")
	selection = int(input("Enter your selection: "))
	
	if selection == 0:
		return
	elif selection == 1:
		review_menu(deck)
	elif selection == 2:
		global decks
		print ("Deleting..")
		decks = [d for d in decks if d != deck]
	else:
		print ("Invalid input..")
		deck_detail()
		return		

def view_decks():
	for i, deck in enumerate(decks):
		print ("{}: {}".format(i+1, deck.name()))
	
	print ("0: Return")
	selection = int(input("Enter your selection: "))
	if selection == 0:
		return
	elif (selection > len(decks)) or (selection < 0):
		print ("Invalid input..")
		view_decks()
		return
	deck_detail(decks[selection-1])
	
def data_set_detail(data_set):
	print ("-"*30)
	print ("Name: {}".format(data_set.name()))
	print ("Source: {}".format(data_set.data_source.name()))
	print ("Source Location: {}".format(data_set.data_source.get_source_str()))
	feature_string = ", ".join(data_set.header())
	print ("Features: {}".format(feature_string))
	
	print ("1: add new deck")
	print ("2: remove set")
	print ("0: return")
	selection = int(input("Enter your selection: "))
	
	if selection == 0:
		return
	elif selection == 1:
		add_new_deck(data_set)
	elif selection == 2:
		print ("Note: this will delete all child decks.")
		if input("Are you sure you want to continue (Y/N").lower() == "y":
			global data_sets
			global decks
			data_sets = [ds for ds in data_sets if ds != data_set]
			decks = [d for d in decks if d.parent != data_set]
		return
	else:
		print ("Invalid input..")
		data_set_detail()
		return

def view_data_sets():
	for i, data_set in enumerate(data_sets):
		print ("{}: {}".format(i+1, data_set.name()))
	
	print ("0: Return")
	selection = int(input("Enter your selection: "))
	if selection == 0:
		return
	elif (selection > len(data_sets)) or (selection < 0):
		print ("Invalid input..")
		view_data_sets()
		return
	data_set_detail(data_sets[selection-1])
	

def add_new_data_set():
	print ("1: New csv data set")
	print ("2: New excel data set")
	selection = int(input("Enter your selection: "))
	file_name = input("Enter the file location: ")
	data_source = None
	if selection == 1:
		data_source = carta_local.CsvDataSource(file_name)
	elif selection == 2:
		data_source = carta_local.ExcelDataSource(file_name)
	data_set = data.DataSet(data_source)
	data_sets.append(data_set)
	

def data_set_menu():
	next_steps = {
		1: view_data_sets,
		2: add_new_data_set
	}
	print ("1: View Data Sets")
	print ("2: Add a New Data Set")
	print ("0: Return")
	selection = int(input("Enter your selection: "))
	if selection == 0:
		return
	next_steps[selection]()

def deck_menu():
	next_steps = {
		1: view_decks,
		2: add_new_deck
	}
	print ("1: View Decks")
	print ("2: Add a New Deck")
	print ("0: Return")
	selection = int(input("Enter your selection: "))
	if selection == 0:
		return
	next_steps[selection]()

def save_data():
	carta_local.save_data(data_sets, decks, "carta_data.p")

def carta_menu():
	next_steps = {
		1: data_set_menu,
		2: deck_menu,
		3: save_data
	}
	print ("1: Data Sets")
	print ("2: Decks")
	print ("3: Save")
	print ("0: Exit")
	
	selection = int (input("Enter your selection: "))
	if selection == 0:
		if input("Save (Y/N): ").lower() == "y":
			save_data()
		return False
	next_steps[selection]()
	return True
	
def main_loop():
	while True:
		if not carta_menu():
			break

if __name__=="__main__":
	if (os.path.isfile('carta_data.p')):
		c_data = carta_local.load_from_file('carta_data.p')
		data_sets = c_data["data_set"]
		decks = c_data["decks"]
	
	
	main_loop()
