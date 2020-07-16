import carta
import datetime

default_leitner_settings = {
	"DAYS_PER_STATUS": 1,
	"NEW_CARDS_PER_SESSION": 5
}

default_streak_settings = {
	"DAYS_PER_STATUS": 1,
	"NEW_CARDS_PER_SESSION": 5
}

def default_leitner_update(days_per_status):
	# returns a function which filters all "due" cards, where cards are reviewed with a period of (status*days_per_status)
	return (lambda review: review.status_datetime + datetime.timedelta(days=(days_per_status * review.status)) <= datetime.datetime.now())

def default_streak_update(days_per_status):
	# returns a function which filters all "due" cards, where cards are reviewed with a period of (status*days_per_status)
	return (lambda review: review.status_datetime + datetime.timedelta(days=(days_per_status * review.status)) <= datetime.datetime.now())
		
class DefaultLeitnerReview(carta.Review):
	"""DefaultLeitnerReview -
		Creates new leitner review 
	"""
	def __init__(self, deck, review_type, review_statuses="none", days_per_status=default_leitner_settings["DAYS_PER_STATUS"], 
			new_cards_per_session=default_leitner_settings["NEW_CARDS_PER_SESSION"]):
		self.days_per_status = days_per_status
		self.new_cards_per_session = new_cards_per_session
		super().__init__(deck, carta.StatusScheme.LeitnerScheme(), review_type, review_statuses)
	
	def start_new_review_session(self, num_options=4):
		review_indices = self.get_indices_by_status(default_leitner_update(self.days_per_status))
		review_indices += self.get_n_new_unreviewed_card_indices(self.new_cards_per_session)
		return super().start_new_review_session(num_options, review_indices, num_options=num_options)

class DefaultStreakReview(carta.Review):
	"""DefaultStreakReview -
		Creates a "streak" review - the status is the number of correct answers to the review. Card status resets to one on failure.
	"""
	def __init__(self, deck, review_type, review_statuses="none", days_per_status=default_streak_settings["DAYS_PER_STATUS"], 
			new_cards_per_session=default_streak_settings["NEW_CARDS_PER_SESSION"]):
		self.days_per_status = days_per_status
		self.new_cards_per_session = new_cards_per_session
		super().__init__(deck, carta.StatusScheme.StreakScheme(), review_type, review_statuses)
		
	def start_new_review_session(self, num_options=4):
		review_indices = self.get_indices_by_status(default_streak_update(self.days_per_status))
		review_indices += self.get_n_new_unreviewed_card_indices(self.new_cards_per_session)
		return super().start_new_review_session(num_options, review_indices, num_options=num_options)
