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
                depends_on_deck (Boolean): if true, changes in the underlying deck will create changes in DataSource - otherwise it's the other way around.
                children (list of Deck): decks tied to DataSet
        """
        def __init__(self, data_source = None, depends_on_deck=False, reload_from_file=False):
                self.data_source = data_source
                self.data_table = {}
                self.depends_on_deck = depends_on_deck
                self.children = []
                
                if reload_from_file:
                        self.load_data_from_source()
                else:
                        self.update()
        
        def add_child(self, child):
                """Adds an object (with an update() method), usually a Deck, that depends on this DataStatus
                """
                self.children.append(child)
        
        def load_data_from_source(self):
                self.data_table = self.data_source.pull_data()
                for child in self.children:
                        child.update()
        
        def update(self):
                """Either update the data from the DataSource, or update the DataSource from the data based on the depends_on_deck member.
                """
                if self.depends_on_deck:
                        if len(self.children) > 0:
                                self.data_table = self.children[0].get_dict_from_cards()
                                self.data_source.push_data(self.data_table)
                elif self.data_source is not None:
                        self.load_data_from_source()
        
        def get_data_set(self):
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

class CardDisplayScheme:
        """CardDisplayScheme - 
                Used to render the underlying card for review.
                
                render_front, render_Back (lambda (X)): function which transforms each side of a card into a displayable object (e.g. a string, or an image).
        """
        def __init__(self, render_front="default", render_back="default"):
                self.render_front = render_front
                self.render_back = render_back
                
                if type(render_front) == str:
                        if render_front == "default":
                                self.render_front = lambda x: str(x)
                if type(render_back) == str:
                        if render_back == "default":
                                self.render_back = lambda x: str(x)
                

class Card:
        """Card -
                The basic unit of review. Contains exactly two fields: front and back.
        
                Types are left open on purpose, for flexible behavior.
                
                front_side, back_side: objects describing what to put on each side of the card
                review_statuses: pointers to CardReviewStatus for each review session. Auto-added on creation of a CardReviewStatus object
                
        """
        def __init__(self, front_side, back_side):
                self.front_side = front_side
                self.back_side = back_side
                self.review_statuses = []
        
        def flipped_card(self):
                return Card(self.back_side, self.front_side)

class StatusScheme:
        """Manages status changes. 
                
                Transform_status (lambda [current status, status change] -> [new status]): function that updates the status within a CardReviewStatus object.
                status_filter (lambda [Review] -> [boolean]): function that determines which objects to filter
        """
        def __init__(self, scheme_name="default", default_status=1, transform_status="default", status_filter="default"):
                self.scheme_name = scheme_name
                self.default_status = default_status
                self.transform_status = None
                self.status_filter = None
                
                if type(transform_status) == str:
                        if transform_status.lower() == "default":
                                self.transform_status = lambda status, change: status
                else:
                        self.transform_status = transform_status
                if type(status_filter) == str:
                        if status_filter.lower() == "default":
                                self.status_filter = lambda review: True
                else:
                        self.status_filter = status_filter

class CardReviewStatus:
        """CardReviewStatus -
                Trackes statuses of each card within each review process.
        """
        def __init__(self, card, review, status_scheme, status="default", status_datetime="now"):
                self.card = card
                self.review = review
                if (self not in self.review.review_statuses):
                        self.review.review_statuses.append(self)
                if (self not in self.card.review_statuses):
                        self.card.review_statuses.append(self)
                if type(status) == str:
                        if status=="default":
                                self.status = status_scheme.default_status
                else:
                        self.status = self.review.status_casting_function(status)
                self.status_scheme = status_scheme
                self.status_datetime = status_datetime
                if type(status_datetime) == str:
                        if status_datetime == "now":
                                self.status_datetime = datetime.datetime.now()
                        else:
                                raise Exception("{} isn't a valid status date".format(status_date))
        
        def update_status(self, status_update):
                """Updates the status according to a "status_update" value - usually a Boolean
                      representing whether the card has been reviewed correctly. Should be handled
                      by the review status.
                """
                self.status = self.status_scheme.transform_status(self.status, status_update)
                self.status_datetime = datetime.datetime.now()

class ReviewSession:
        """Allows the user to interact with the deck. Prototype object.
        """
        def __init__(self, review, review_statuses = "none", review_indices="whole_deck_random"):
                self.review = review
                self.deck = self.review.deck
                self.review_indices = review_indices
                self.current_index = 0
                self.review_statuses = review_statuses
                self.max_cards = self.review.max_cards_per_session
                
                self.is_active = True
                
                if type(review_statuses) == str:
                        if review_statuses == "none":
                                self.review_statuses = []
                                
                self.status_scheme = self.review.status_scheme
                if type(review_indices) == str:
                        if review_indices == "whole_deck_random":
                                self.review_indices = [i for i in range(0, self.deck.num_cards())]
                                random.shuffle(self.review_indices)
                        elif review_indices == "whole_deck":
                                self.review_indices = [i for i in range(0, self.deck.num_cards())]

        def deactivate(self):
                self.is_active = False
                                
        def get_review_status(self, card="current"):
                if type(card) == str:
                        if card == "current":
                                card = self.get_current_card()
                        else:
                                raise Exception("Invalid type")
                for review_status in self.review_statuses:
                        if review_status.card == card:
                                return review_status
                return None
        
        def get_current_card(self):
                return self.deck[self.review_indices[self.current_index]]
                                
        def review_next_card(self):
                """Move to the next card in the review, and return it.
                """
                if not self.is_active:
                        return -1
                self.current_index += 1
                if self.current_index >= self.max_cards:
                        return -1
                elif self.current_index >= len(self.review_indices):
                        return -1
                else:
                        self.deactivate()
                return self.get_current_card()
        
        def set_review_status(self, status):
                """Directly changes the status for the current card.
                """
                current_card = self.get_current_card()
                self.review_statuses = [status_obj for status_obj in self.review_statuses if status_obj.card != current_card]
                self.review_statuses.append(CardReviewStatus(current_card, self, self.status_scheme, status=status))
        
        def update_review_status_from_result(self, res, callback="none"):
                """Uses a special "res" value - usually a Boolean involving whether or not the answer is correct -
                     to update the status of a card. The given review scheme should handle the logic here.
                     
                     Callback - can call another function based on the result.
                """
                if type(callback) == str:
                	if callback == "none":
                		callback = (lambda x: x)
                		
                review_status = self.get_review_status(self.get_current_card())
                if review_status is None:
                        review_status = CardReviewStatus(self.get_current_card(), self.review, self.status_scheme, status="default")
                else:
                        review_status.update_status(res)
                callback(review_status)
                
        def check_answer(self, answer):
                return True

class SimpleReviewSession(ReviewSession):
        """SimpleReviewSession -
                Simple review, just gives front and back. No input.
        """
        def __init__(self, review, review_indices="whole_deck_random"):
                super().__init__(review, review_indices="whole_deck_random")

class MultipleChoiceReviewSession(ReviewSession):
        """MultipleChoiceReviewSession -
                Multiple choice review
        """
        def __init__(self, review,  num_options=4, review_statuses="none", review_indices="whole_deck_random"):
                assert(num_options > 1)
                
                super().__init__(review, review_statuses=review_statuses, review_indices=review_indices)
                self.current_answer = -1
                self.current_options = []
                self.num_options = num_options
                
                self.all_back_options = self.deck.get_all_rendered_values("back")
                if (num_options > len(self.all_back_options)):
                        num_options = len(self.all_back_options)
        
        def get_header(self):
                """Gets the front of the current card
                """
                return self.deck.render_front(card=self.get_current_card())
        
        def generate_options(self):
                """Generate all options for the current card to be reviewed
                """
                self.current_answer = self.deck.render_back(card=self.get_current_card())
                values = [self.current_answer]
                while len(values) < self.num_options:
                        drop_value = random.choice(self.all_back_options)
                        if drop_value not in values:
                                values.append(drop_value)
                random.shuffle(values)
                self.current_options = values
                return self.current_options
        
        def check_answer(self, answer, status_callback="none"):
                """Check if the selected option is correct. Note that this is based on rendered values.
                """
                self.current_answer = self.deck.render_back(card=self.get_current_card())
                res = (answer == self.current_answer)
                self.update_review_status_from_result(res, status_callback)
                return res

class InputReviewSession(ReviewSession):
        """InputReviewSession -
                Uses user input to validate 
        """
        def __init__(self, review, review_statuses="none", review_indices="whole_deck_random"):
                super().__init__(review, review_statuses=review_statuses, review_indices=review_indices)
        
        def normalize(self, in_str):
                """Normalization for proper input comparison.
                """
                return in_str.lower().replace(" ", "").replace(".", "").replace(",", "")
        
        def check_answer(self, answer, status_callback="none"):
                """Insures the normalized rendered value given matches the correct answer.
                """
                res = (self.normalize(answer) == self.normalize(self.deck.render_back(card=self.get_current_card())))
                self.update_review_status_from_result(res, status_callback)
                return res
        
        def get_correct_answer(self):
                return self.deck.render_back(card=self.get_current_card())

class Review:
        """Review -
                Handles a "review" of the deck. 
                
                For example, a user might decide to make a seperate multiple-choice review (for recognition) and input review (for recall)
                        - with seperate statuses for each card. In this case, two Review objects should be created.
                
                deck (Deck) - underlying deck to review
                status_type - type of status. Right now, the only valid options are "default" (basic review type with no active
                        participation on the part of the user), and "leitner" (reflecting the Leitner system of flashcard review)
                review_statuses (list of CardReviewStatuses) - saves the review statuses for each card IN REVIEW. If a card has not been
                        added to the review, no review_status should exist.
        """
        def __init__(self, deck, status_scheme, review_type, max_cards_per_session=20, review_statuses="none"):
                self.deck = deck
                self.current_index = -1
                self.review_type = review_type
                
                self.status_scheme = status_scheme
                self.status_type = status_scheme.scheme_name
                
                self.max_cards_per_session = max_cards_per_session
                
                self.review_statuses = review_statuses
                if type(review_statuses) == str:
                        if review_statuses == "none":
                                self.review_statuses = []
                
                # optional type enforcement for reviews.
                self.status_casting_function = (lambda x: x)
        
        def get_indices_by_status(self):
                # status_filter_fn: True if a status should be included
                status_filter_fn = self.status_scheme.status_filter
                relevant_statuses = [review_status for review_status in self.review_statuses if status_filter_fn(review_status)]
                return [self.deck.cards.index(relevant_status.card) for relevant_status in relevant_statuses]
        
        def get_review_card_indices(self):
                """returns indices of all cards that are actively being reviewed.
                """
                return [self.deck.cards.index(review_status.card) for review_status in self.review_statuses]
        
        def get_unreviewed_card_indices(self):
                """Returns indices of all cards that have not entered the review.
                """
                reviewed_indices = self.get_review_card_indices()
                return [i for i in range(0,self.deck.num_cards()) if i not in reviewed_indices]
        
        def get_n_new_unreviewed_card_indices(self, n):
                """Get a certain number of unreviewed cards. Please note that this happens in the order of the deck.
                """
                new_indices = self.get_unreviewed_card_indices()
                if n > len(new_indices):
                        return new_indices
                else:
                        return new_indices[:n]
                
        
        def start_new_review_session(self, num_options=4, review_indices="whole_deck_random"):
                """Returns a new ReviewSession object according to the review_type
                """
                if self.review_type == "simple":
                        return SimpleReviewSession(self, review_indices=review_indices)
                elif self.review_type == "multiple_choice":
                        return MultipleChoiceReviewSession(self, num_options, review_statuses=self.review_statuses, review_indices=review_indices)
                elif self.review_type == "input":
                        return InputReviewSession(self, review_statuses=self.review_statuses, review_indices=review_indices)
                else:
                        raise Exception("Review type {} not recognized".format(self.review_type))

class Deck:
        """Basic deck object deriving cards from a data set
        
                filter_fn (card->boolean): true if a card should be included.
        """
        def __init__(self, parent_data_set, front_side_field, back_side_field, card_display_scheme, static=False, reload_from_file=False, filter_fn="none"):
                self.parent_data_set = parent_data_set
                self.parent_data_set.add_child(self)
                self.front_side_field = front_side_field
                self.back_side_field = back_side_field
                self.card_display_scheme = card_display_scheme
                self.static = static
                self.filter_fn = filter_fn
                self.cards = []
                if type(filter_fn) == str:
                        self.filter_fn = (lambda x: True)
                
                if reload_from_file:
                        self.load_data_from_source()
                else:
                        self.refresh_data()
        
        def add_card(self, front_side, back_side):
                new_card = Card(front_side, back_side)
                if self.filter_fn(new_card):
                        self.cards.append(new_card)
                        if self.static:
                                self.refresh_data()
        
        def remove_card(self, card_to_remove):
                self.cards.remove(card_to_remove)
                if self.static:
                        self.refresh_data()
        
        def add_new_review(self, review):
                """Attaches a new review object to the deck. Should happen automatically on intialization of a Review() object.
                """
                self.reviews.append(review)
        
        def get_dict_from_cards(self):
                """Returns a dictionary describing each card. [Field]: [list of objects].
                """
                data_dict = { self.front_side_field: [], self.back_side_field: []}
                for card in self.cards:
                        data_dict[self.front_side_field].append(card.front_side)
                        data_dict[self.back_side_field].append(card.back_side)
                return data_dict
        
        def load_data_from_source(self):
                """Pull from the DataSet object. For refreshing data or initializaing independent decks.
                """
                # underlying data: [front side, back side, updated (y/n)]: key to updating data in each card
                underlying_data = [ [front,back,False] for front,back in zip(self.parent_data_set[self.front_side_field], self.parent_data_set[self.back_side_field]) ]
                
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
        
        def refresh_data(self):
                """Either update the data in each card, or update the parent data set.
                """
                if self.static:
                        if self.parent_data_set.depends_on_deck:
                                self.parent_data_set.update()
                else:
                        self.load_data_from_source()
        
        def render_front(self, index=-1, card="none"):
                """Uses the attached display scheme to generate the front of a given card.
                """
                if index != -1:
                        return self.card_display_scheme.render_front(self.cards[index].front_side)
                elif type(card) != str:
                        return self.card_display_scheme.render_front(card.front_side)
                else:
                        assert (False)
        
        def render_back(self, index=-1, card="none"):
                """Uses the attached display scheme to generate the back of a given card
                """
                if index != -1:
                        return self.card_display_scheme.render_back(self.cards[index].back_side)
                elif type(card) != str:
                        return self.card_display_scheme.render_back(card.back_side)
                else:
                        assert (False)
        
        def find_card_by_side(self, front_side, back_side):
                """Find the card object that matches the given front and back values.
                    Note that these are non-rendered values.
                """
                for card in self.cards:
                        if (card.front_side == front_side and card.back_side == back_side):
                                return card
                return None
        
        def get_all_rendered_values(self, side):
                """Returns a list of post-rendered values for each card (e.g. for creating a list of options).
                """
                all_rendered_values = []
                for card in self.cards:
                        rendered_value = ""
                        if side == "front":
                                rendered_value = self.card_display_scheme.render_front(card.front_side)
                        elif side == "back":
                                rendered_value = self.card_display_scheme.render_back(card.back_side)
                        else:
                                assert (False)
                        if rendered_value not in all_rendered_values:
                                all_rendered_values.append(rendered_value)
                return all_rendered_values
        
        def num_cards(self):
                return len(self.cards)
        
        def shuffle(self):
                random.shuffle(self.cards)
        
        def get_random_card(self):
                return random.choice(self.cards)
        
        def update(self):
                """Update upon a material change. At the moment this only changes the data of the cards.
                """
                if not static:
                        self.refresh_data()
        
        def __getitem__(self, key):
                return self.cards[key]
        
        def name(self):
                return "{} ({}/{})".format(self.parent_data_set.name(), self.front_side_field, self.back_side_field)
