import csv
import random
import json
import os
import datetime
import re

class ReviewScheme:
	"""ReviewScheme -
		Scheme that determines which cards should be reviewed, and how.
		
		default_status - the initial status each card has upon creation.
		card_filter - function(card) for filtering which cards should be reviewed.
		card_update - function(success, card) for updating each card status.
	"""
	def __init__(self, default_status):
		self.default_status = default_status
	
	def card_filter(self, card):
		return True
	
	def status_update(self, card):
		return card.status

class Card:
        """Card -
                The basic unit of review. Contains exactly two fields: front and back.

                Types are left open on purpose, for flexible behavior. Cards are identified by
                	their front side.

                front_side, back_side: objects describing what to put on each side of the card
                status: the current status of the card.
                status_dt: datetime that the status was last updated.

        """
        def __init__(self, front_side, back_side, status, parent):
                self.front_side = front_side
                self.back_side  = back_side
                self.status     = status
                self.status_dt  = datetime.datetime.now()
                self.parent     = parent

        def flipped_card(self):
                return Card(self.back_side, self.front_side)
        
        def update_card(self, success):
        	self.status = self.parent.review_scheme.status_update(success, self)
        	self.status_dt = datetime.datetime.now()
        	
                
class Deck:
        """Basic deck object deriving cards from a data set
        """
        def __init__(self, parent, front_side, back_side, review_scheme_obj, filter_fn="none", initialize=True):
                self.parent = parent
                self.parent.add_child(self)
                self.review_scheme = review_scheme_obj
                self.front_side = front_side
                self.back_side  = back_side
                self.filter_fn = filter_fn
                self.cards = []
                if type(filter_fn) == str:
                        self.filter_fn = (lambda x: True)

		if initialize:
	                self.refresh_data()

        def load_data_from_source(self):
                """Pull from the DataSet object. For refreshing data or initializaing independent decks.
                """
                underlying_data = []
                for front, back in zip(self.parent[self.front_side], self.parent[self.back_side]):
                	underlying_data.append([front,back,False])

                new_cards = []

                # update and delete any cards
                for card in self.cards:
                        for subarray in underlying_data:
                                if subarray[0] == card.front:
                                        card.back = subarray[1]
                                        if self.filter_fn(card):
                                                new_cards.append(card)
                                        subarray[2] = True

                self.cards = new_cards

                # add new cards
                for subarray in underlying_data:
                        if not subarray[2]:
                                self.add_card(subarray[0], subarray[1])
                                
        def add_card(self, front_side, back_side):
        	self.cards.append(Card(front_side, back_side, self.review_scheme.default_status, self))

        def refresh_data(self):
                """Either update the data in each card, or update the parent data set.
                """
                self.load_data_from_source()

        def find_card_by_side(self, front_side, back_side):
                """Find the card object that matches the given front and back values.
                    Note that these are non-rendered values.
                """
                for card in self.cards:
                        if (card.front_side == front_side and card.back_side == back_side):
                                return card
                return None

        def num_cards(self):
                return len(self.cards)

        def shuffle(self):
                random.shuffle(self.cards)

        def get_random_card(self):
                return random.choice(self.cards)

        def update(self):
                """Update upon a material change. At the moment this only changes the data of the cards.
                """
                self.refresh_data()

        def __getitem__(self, key):
                return self.cards[key]

        def name(self):
                return "{} ({}/{})".format(self.parent.name(), self.front_side, self.back_side)
