"""interaction.py -
    Linkage script for user interaction.

    Inputs:
        - Start new session
        - Submit answer
        - Get next card
    Output:
        - Current cards in review
        - Unreviewed cards
"""

import carta
import carta_local
import os.path

class ReviewMenu:
    def __init__(self, data_state):
        self.data_state = data_state

class DataSourceMenu:
    def __init__(self, data_state):
        self.data_state = data_state

class DeckMenu:
    def __init__(self, data_state):
        self.data_state = data_state

class MainMenu:
    def __init__(self, data_state):
        self.data_state = data_state

    def get_data_source_menu(self):
        return DataSourceMenu(self.data_state)

    def get_deck_menu(self):
        return DeckMenu(self.data_state)

class DataState:
    def __init__(self, save_file):
        self.save_file = save_file
        self.state_data = []
        if (os.path.isfile(self.save_file)):
            self.state_data = load_from_file(save_file)
    
    def save_data(self):
        carta_local.save_data(self.state_data["data_set"],
                  self.state_data["decks"],
                  self.state_data["reviews"], self.save_file)

    def get_data_sets(self):
        return self.state_data["data_set"]

    def get_decks(self):
        return self.state_data["decks"]

    def get_reviews(self):
        return self.state_data["reviews"]

class User:
    def __init__(self, data_state):
        self.data_state = data_state
        self.data_sets = []
        self.decks = []
        self.reviews = []

class UserReviewInterface:
    """UserReviewInterface -
            Class that allows the user to interact with ReviewSession objects in a more
                controlled manner.
    """
    def __init__(self, user, review):
        self.user = user
        self.review = review
        self.review_session = None
        assert(review in user.reviews)

    def start_review_session(self, num_options=4, new_cards=True):
        self.review_session = self.review.start_new_review_session(num_options=num_options, new_cards=new_Cards)
        return self.review_session

    def submit_answer(self, answer):
        return self.review_session.check_answer(answer)

    def get_next_card(self):
        self.review_session.review_next_card()

    def get_current_card(self):
        return self.review_session.get_current_card()

    def current_card_front(self):
        return self.review_session.deck.render_front(card=self.get_current_card())

    def current_card_back(self):
        return self.review_session.deck.render_back(card=self.get_current_card())
