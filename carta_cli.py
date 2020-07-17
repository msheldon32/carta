import carta
import os
import math
import carta_local
import carta_review_schemes

def clear_screen():
	if os.name == "nt":
		os.system('cls')
	else:
		os.system('clear')

def display_card_side(card, deck, side, status=None):
	def display_with_padding(text,padding=50):
		remaining_padding = (padding-2-len(text))
		print("|{}{}{}|".format(" "*math.ceil(remaining_padding/2),text," "*math.floor(remaining_padding/2)))
	clear_screen()
	card_text = ""
	if side == "front":
		card_text = str(deck.render_front(card=card))
	elif side == "back":
		card_text = str(deck.render_back(card=card))
	print("-"*50)
	display_with_padding(side.upper())
	print("|{}|".format(" "*48))
	display_with_padding(card_text)
	print("|{}|".format(" "*48))
	print("|{}{}|".format("" if status is None else status, " "*(48-len(str(status)))))
	print("-"*50)

def display_multiple_choices(choices, num_options=4):
	for i, choice in enumerate(choices):
		print("{}: {}".format(i, choice))

def edit_data_set_menu(data_set):
	pass

def edit_deck_menu(deck, data_sets):
	mutable_deck = deck.static and deck.parent_data_set.depends_on_deck
	if (mutable_deck):
		print("1 - Add a new card")
		print("2 - Delete a card")
	print("0 - Return to Previous Menu")
	command = int(input("What would you like to do? "))
	if command == 0:
		return
	elif command == 1:
		front_side = input("Enter the front side ({}): ".format(deck.front_side_field))
		back_side = input("Enter the back side ({}): ".format(deck.back_side_field))
		deck.add_card(front_side,back_side)
	elif command == 2:
		print("Command not implemented")
		

def data_set_menu(data_sets):
	print("1 - view all data sets")
	print("2 - add a new data set")
	print("3 - edit an existing data set")
	print("4 - delete a data set (along with it's child decks")
	print("0 - return to previous menu")
	command = int(input("What would you like to do? "))
	if command == 0:
		return
	elif command == 1:
		if len(data_sets) == 0:
			print("No data sets found")
		for i, set in enumerate(data_sets):
			print("{}: {}".format(i, set.name()))
	elif command == 2:
		file_name = input("Please enter the file name: ")
		file_ext = file_name.split(".")[-1]
		if file_ext not in ["csv"]:
			print("File extention not supported")
		read_only = input ("Read only (Y/N)? ").lower() == "y"
		if file_ext == "csv":
			data_sets.append(carta.DataSet(carta_local.CsvDataSource(file_name, read_only)))
	elif command == 3:
		if len(data_sets) == 0:
			print("No data sets found.")
		else:
			for i, set in enumerate(data_sets):
				print("{}: {}".format(i, set.name()))
			set_to_edit = int(input("Which data set would you like to edit: "))
			edit_data_set_menu(set_to_edit)
	elif command == 4:
		if len(data_sets) == 0:
			print("No data sets found.")
		else:
			for i, set in enumerate(data_sets):
				print("{}: {}".format(i, set.name()))
			set_to_delete = int(input("Which data set would you like to delete: "))
			delete_or_not = input("delete {} (Y/N)? ".format(data_sets[set_to_delete].name())).lower()
			if delete_or_not == "y":
				data_sets.remove(data_sets[set_to_delete])
		
def deck_menu(decks, data_sets):
	print("1 - view all decks")
	print("2 - add a new deck")
	print("3 - edit an existing deck")
	print("4 - delete a deck")
	print("0 - return to previous menu")
	command = int(input("What would you like to do? "))
	if command == 0:
		return
	elif command == 1:
		if len(decks) == 0:
			print("No decks found")
		for i, deck in enumerate(decks):
			print("{}: {}".format(i, deck.name()))
	elif command == 2:
		print("Please select the data set to pull from:")
		print("0: No external data set (create cards only)")
		for i, set in enumerate(data_sets):
			print("{}: {}".format(i+1, set.name()))
		set_to_use = int(input("Which data set would you like to use: "))
		deck_is_first = False
		if set_to_use == 0:
			deck_is_first = True
			file_name = input("Please enter the deck name: ") + ".csv"
			data_source = carta_local.CsvDataSource(file_name, read_only=False)
			set_to_use = carta.DataSet(data_source=data_source, depends_on_deck=True)
			data_sets.append(set_to_use)
		else:
			set_to_use = data_sets[set_to_use-1]
		print("\From these fields...")
		for i, field in enumerate(set_to_use.header()):
			print("{}: {}".format(i, field))
		front_field = input("Which field should be used on the front of the card? ")
		back_field = input("Which field should be used on the back of the card? ")
		if not deck_is_first:
			front_field = set_to_use.header()[int(front_field)]
			back_field = set_to_use.header()[int(back_field)]
		static = True
		if not deck_is_first:
			static = input("Should this deck be static (if not, it will change along with the data set) (Y/N)? ").lower() == "y"
		
		decks.append(carta.Deck(set_to_use,front_field,back_field,carta.CardDisplayScheme(),static=static))
	elif command == 3:
		for i, deck in enumerate(decks):
			print("{}: {}".format(i, deck.name()))
		deck_to_edit = int(input("Which deck would you like to edit: "))
		deck_to_edit = decks[deck_to_edit]
		edit_deck_menu(deck_to_edit, data_sets)
	elif command == 4:
		for i, deck in enumerate(decks):
			print("{}: {}".format(i, deck.name()))
		deck_to_delete = int(input("Which deck would you like to delete: "))
		deck_to_delete = decks[deck_to_delete]
		delete_or_not = input("Would you like to delete ({}) (Y/N)? ".format(deck_to_delete.name())).lower()
		if delete_or_not == "y":
			decks.remove(deck_to_delete)
			if deck_to_delete.static and deck_to_delete.parent_data_set.depends_on_deck:
				data_sets.remove(deck_to_delete.parent_data_set)

def get_review_by_type(reviews, deck_to_review, review_type):
	for review in reviews:
		if (review.review_type == review_type) and (review.deck == deck_to_review):
			return review
	return None

def start_review_session(decks, reviews):
	for i, deck in enumerate(decks):
		print("{}: {}".format(i, deck.name()))
	deck_to_review = int(input("Which deck would you like to review: "))
	deck_to_review = decks[deck_to_review]
	
	print("Please select the review type: ")
	print("0: Simple Review")
	print("1: Multiple Choice")
	print("2: Input Review")
	review_type = int(input("Please input your selection: "))
	
	if review_type == 0:
		review = get_review_by_type(reviews, deck_to_review, "simple")
		if review is None:
			review = carta.Review(deck_to_review, carta.StatusScheme(), "simple")
			reviews.append(review)
		review_session = review.start_new_review_session()
		while review_session.review_next_card() != -1:
			display_card_side(review_session.get_current_card(),deck_to_review, "front")
			input()
			display_card_side(review_session.get_current_card(),deck_to_review, "back")
			input()
		clear_screen()
	elif review_type == 1:
		review = get_review_by_type(reviews, deck_to_review, "multiple_choice")
		if review is None:
			review = carta_review_schemes.DefaultLeitnerReview(deck_to_review, "multiple_choice")
			reviews.append(review)
		review_session = review.start_new_review_session()
		while review_session.review_next_card() != -1:
			starting_status = review_session.get_review_status()
			if starting_status is None:
				starting_status = ""
			else:
				starting_status = str(starting_status.status)
			display_card_side(review_session.get_current_card(),deck_to_review, "front", status=starting_status)
			input()
			options = review_session.generate_options()
			display_multiple_choices(options)
			chosen_option = int(input("Please input the correct option: "))
			chosen_option = options[chosen_option]
			if review_session.check_option(chosen_option):
				input("You were correct!")
			else:
				correct_value = review_session.current_answer
				input("Incorrect! Answer {} ({}) is correct".format(options.index(correct_value), correct_value))
		clear_screen()
	elif review_type == 2:
		review = get_review_by_type(reviews, deck_to_review, "input")
		if review is None:
			review = carta_review_schemes.DefaultLeitnerReview(deck_to_review, "input")
			reviews.append(review)
		review_session = review.start_new_review_session()
		while review_session.review_next_card() != -1:
			starting_status = review_session.get_review_status()
			if starting_status is None:
				starting_status = ""
			else:
				starting_status = str(starting_status.status)
			display_card_side(review_session.get_current_card(),deck_to_review, "front", status=starting_status)
			input()
			choice = input("Please input the correct {}: ".format(deck_to_review.back_side_field))
			if review_session.check_answer(choice):
				input("You were correct!")
			else:
				correct_value = review_session.get_correct_answer()
				input("Incorrect! {} is correct".format(correct_value))
		

def command_loop():
	carta_data = carta_local.load_from_file("carta_data.json")
	data_sets = carta_data["data_sets"]
	decks = carta_data["decks"]
	reviews = carta_data["reviews"]
	while True:
		command = int(input("What would you like to do? "))
		
		if command == 1:
			start_review_session(decks,reviews)
		elif command == 2:
			data_set_menu(data_sets)
		elif command == 3:
			deck_menu(decks, data_sets)
		elif command == 9:
			display_options()
		elif command == 0:
			break
	if input("Save data (Y/N)? ").lower() == "y":
		carta_local.save_data(data_sets, decks, reviews, "carta_data.json")

def display_options():
	print("1 - start a new review session")
	print("2 - view/add/remove data sets")
	print("3 - view/add/remove decks")
	print("9 - display this message again")
	print("0 - exit")

if __name__=="__main__":
	print("Welcome to Carta")
	display_options()
	command_loop()
