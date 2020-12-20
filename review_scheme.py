import csv
import random
import json
import os
import datetime
import re

import data
import deck

class LeitnerReviewScheme(deck.ReviewScheme):
	def __init__(self, days_per_status=1, new_cards_per_session=5, max_status=5):
		super().__init__(-1)
		self.days_per_status       = days_per_status
		self.new_cards_per_session = new_cards_per_session
		self.max_status            = max_status
		
	def card_filter(self, card):
		status_dt = card.status_dt
		status    = card.status
		update_dt = status_dt + datetime.timedelta(days=(status*self.days_per_status))
		return (update_dt <= datetime.datetime.now()) and (status != -1)
	
	def get_cards_to_review(self, deck):
		out_cards = []
		new_cards = 0
		for card in deck.cards:
			if (card.status == -1) and (new_cards < self.new_cards_per_session):
				out_cards.append(card)
				new_cards += 1
			elif self.card_filter(card):
				out_cards.append(card)
		return out_cards
	
	def status_update(self, success, card):
		if card.status in [-1, 0]:
			card.status = 1 if success else 0
			return
		return card.status + (1 if success else -1)


class StreakReviewScheme(deck.ReviewScheme):
	def __init__(self, days_per_status=1, new_cards_per_session=5, max_status=5):
		super().__init__(-1)
		self.days_per_status       = days_per_status
		self.new_cards_per_session = new_cards_per_session
		self.max_status            = max_status
		
	def card_filter(self, card):
		status_dt = card.status_dt
		status    = card.status
		update_dt = status_dt + datetime.timedelta(days=(status*self.days_per_status))
		return (update_dt <= datetime.datetime.now()) and (status != -1)
	
	def get_cards_to_review(self, deck):
		out_cards = []
		new_cards = 0
		for card in deck.cards:
			if (card.status == -1) and (new_cards < self.new_cards_per_session):
				out_cards.append(card)
				new_cards += 1
			elif self.card_filter(card):
				out_cards.append(card)
		return out_cards
	
	def status_update(self, success, card):
		return (card.status + 1 if success else 0)
