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
def default_leitner_update(current_status, status_update, max_status="none"):
	"""Updates according to the Leitner system.
		- each card has an integer status
		- lowest statuses are reviewed more often
		- status increments by one on correct identification
		- status decrements by one on incorrect identification
		- status cannot be lower than 1
	"""
	assert (type(current_status) == int)
	assert (type(status_update) == bool)
	has_max = True
	if type(max_status) == str:
		if max_status == "none":
			has_max = False
	if (current_status == 1 and not status_update):
		return current_status
	elif has_max:
		if current_status >= max_status:
			return max_status
	return current_status + (1 if status_update else -1)	

def generate_leitner_status_scheme(max_status="none"):
		"""Implements the Leitner method. 
		"""
		return carta.StatusScheme(scheme_name="leitner", transform_status=(lambda cs, su: default_leitner_update(cs, su, max_status)))
			
def default_streak_update(current_status, status_update, max_status="none"):
	"""Updates according to the card's streak.
		- each card has an integer status
		- lowest statuses are reviewed more often
		- status increments by one on correct identification
		- status resets to 1 on failure
		- status cannot be lower than 1
	"""
	assert (type(current_status) == int)
	assert (type(status_update) == bool)
	has_max = True
	if type(max_status) == str:
		if max_status == "none":
			has_max = False
	if (current_status == 1 and not status_update):
		return current_status
	elif has_max:
		if current_status >= max_status:
			return max_status
	return (current_status + 1) if status_update else 1

def generate_streak_status_scheme(max_status="none"):
	return carta.StatusScheme(scheme_name="streak", transform_status=(lambda cs, su: default_streak_update(cs, su, max_status)))
		
def default_leitner_status_filter(days_per_status):
	# returns a function which filters all "due" cards, where cards are reviewed with a period of (status*days_per_status)
	return (lambda review: review.status_datetime + datetime.timedelta(days=(days_per_status * review.status)) <= datetime.datetime.now())

def default_streak_status_filter(days_per_status):
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
		super().__init__(deck, generate_leitner_status_scheme(), review_type, review_statuses)
	
	def start_new_review_session(self, num_options=4):
		review_indices = self.get_indices_by_status(default_leitner_status_filter(self.days_per_status))
		review_indices += self.get_n_new_unreviewed_card_indices(self.new_cards_per_session)
		return super().start_new_review_session(num_options=num_options, review_indices=review_indices)

class DefaultStreakReview(carta.Review):
	"""DefaultStreakReview -
		Creates a "streak" review - the status is the number of correct answers to the review. Card status resets to one on failure.
	"""
	def __init__(self, deck, review_type, review_statuses="none", days_per_status=default_streak_settings["DAYS_PER_STATUS"], 
			new_cards_per_session=default_streak_settings["NEW_CARDS_PER_SESSION"]):
		self.days_per_status = days_per_status
		self.new_cards_per_session = new_cards_per_session
		super().__init__(deck, generate_streak_status_scheme(), review_type, review_statuses)
		
	def start_new_review_session(self, num_options=4):
		review_indices = self.get_indices_by_status(default_streak_status_filter(self.days_per_status))
		review_indices += self.get_n_new_unreviewed_card_indices(self.new_cards_per_session)
		return super().start_new_review_session(num_options=num_options, review_indices=review_indices)
