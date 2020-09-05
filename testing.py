# testing script for carta

import carta
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
        
    

class TestCardDisplayScheme(unittest.TestCase):
    # a card display scheme object should be able to:
    #     - by default, return a string variation of an object
    def test_default(self):
        default_cds = carta.CardDisplayScheme()
        self.assertTrue(default_cds.render_front(1) == "1")
        self.assertTrue(default_cds.render_back(1) == "1")
        self.assertTrue(default_cds.render_front("test") == "test")

class TestCard(unittest.TestCase):
    # a card should be able to:
    #     - flip itself dynamically
    def test_flip(self):
        self.def_card = carta.Card("front", "back")
        flip_card = self.def_card.flipped_card()
        self.assertTrue(self.def_card != flip_card)
        self.assertTrue(flip_card.front_side != self.def_card.front_side)
        self.assertTrue(flip_card.front_side == self.def_card.back_side)

class TestStatusScheme(unittest.TestCase):
    # a status scheme should be able to:
    #     - keep schemes constant if a transformation has not been given
    def test_default(self):
        def_ss = carta.StatusScheme()
        self.assertTrue(def_ss.transform_status(7, 1) == 7)

class TestCardReviewStatus(unittest.TestCase):
    # a card review status object should be able to:
    #     - update itself properly according to a status scheme
    #           - should follow the rules of the scheme
    #           - should update based on the current time
    pass

class TestReviewSession(unittest.TestCase):
    # a review session object should:
    #     - not fetch new cards upon deactivation
    #     - not fetch new cards when reaching the end of the deck
    #     - automatically update review statuses
    def grab_review(self):
        self.default_ds = carta_local.CsvDataSource("countries.csv")
        self.default_dset = carta.DataSet(self.default_ds)
        self.sample_deck = carta.Deck(self.default_dset, "Name", "Capital", carta.CardDisplayScheme())
        deck_length = self.sample_deck.num_cards()
        empty_ss = carta.StatusScheme()
        self.sample_review = carta.Review(self.sample_deck, empty_ss, "simple", max_cards_per_session=deck_length+10)
        self.sample_review_session = self.sample_review.start_new_review_session()
        
    def setUp(self):
        self.grab_review()
    
    def test_deactivation(self):
        self.grab_review()
        self.sample_review_session.deactivate()
        self.assertTrue(self.sample_review_session.review_next_card() == -1)

    def test_finish(self):
        self.grab_review()
        for i in range(0, self.sample_deck.num_cards()):
            self.sample_review_session.review_next_card()
        self.assertTrue(self.sample_review_session.review_next_card() == -1)

class TestSimpleReviewSession(unittest.TestCase):
    # a simple review session object should:
    #     - not update the review statuses whatsoever
    def test_simple_review(self):
        default_ds = carta_local.CsvDataSource("countries.csv")
        default_dset = carta.DataSet(default_ds)
        sample_deck = carta.Deck(default_dset, "Name", "Capital", carta.CardDisplayScheme())
        empty_ss = carta.StatusScheme()
        sample_review = carta.Review(sample_deck, empty_ss, "simple")
        sample_review_session = sample_review.start_new_review_session()
        while sample_review_session.review_next_card() != -1:
            prev_status = sample_review_session.get_review_status()
            sample_review_session.update_review_status_from_result("test")
            next_status = sample_review_session.get_review_status()
            self.assertTrue(prev_status == next_status)

class TestMultipleChoiceReviewSession(unittest.TestCase):
    # a multiple choice review session object should:
    #     - generate unique options for each review
    #           - these options should contain the correct answer
    #           - the number of options should be less than or equal to the proper amount
    #           - the number of options should only be less than the amount given if there aren't enough cards in the deck
    #           - no option is repeated
    #     - check the answer
    #     - properly update the review status of the reviewed card
    def test_multichoice_review(self):
        default_ds = carta_local.CsvDataSource("countries.csv")
        default_dset = carta.DataSet(default_ds)
        sample_deck = carta.Deck(default_dset, "Name", "Capital", carta.CardDisplayScheme())
        empty_ss = carta.StatusScheme()
        sample_review = carta.Review(sample_deck, empty_ss, "multiple_choice")
        sample_review_session = sample_review.start_new_review_session()
        try_correct = True
        
        while sample_review_session.review_next_card() != -1:
            options = sample_review_session.generate_options()
            correct_answer = sample_review_session.deck.render_back(card=sample_review_session.get_current_card())
            self.assertTrue(len(options) <= sample_review_session.num_options)
            self.assertTrue(correct_answer in options)

            # this will never occur. will need to add new data sets for testing.
            if sample_review_session.deck.num_cards() < sample_review_session.num_options:
                self.assertTrue(len(options) < sample_review_session.num_options)

            dup_options = []
            for option in options:
                self.assertTrue(option not in dup_options)
                dup_options.append(option)
                
            if try_correct:
                # try correct answer
                try_correct = False
                correct_idx = options.index(correct_answer)
                self.assertTrue(sample_review_session.check_answer(options[correct_idx]))
            else:
                # try false answer
                try_correct = True
                correct_idx = options.index(correct_answer)
                incorrect_idx = (correct_idx+1) % len(options)
                self.assertFalse(sample_review_session.check_answer(options[incorrect_idx]))

class TestInputReviewSession(unittest.TestCase):
    # a test input review session object should:
    #     - check the answer properly
    #            - ensure that whitespace and punctuation shouldn't make an impact
    def test_input_review(self):
        default_ds = carta_local.CsvDataSource("countries.csv")
        default_dset = carta.DataSet(default_ds)
        sample_deck = carta.Deck(default_dset, "Name", "Capital", carta.CardDisplayScheme())
        empty_ss = carta.StatusScheme()
        sample_review = carta.Review(sample_deck, empty_ss, "input")
        sample_review_session = sample_review.start_new_review_session()
        while sample_review_session.review_next_card() != -1:
            pass

class TestReview(unittest.TestCase):
    # a review object should:
    #     - return a new, properly figured review session object on command
    #     - select a proper amount of new cards to review
    def test_status_scheme(self):
        self.data_source = carta_local.CsvDataSource("countries.csv")
        self.data_set = carta.DataSet(data_source=self.data_source)
        self.capital_deck = carta.Deck(self.data_set, "Name", "Capital", carta.CardDisplayScheme())

        self.mock_status_scheme = carta.StatusScheme()
        
        self.capital_review = carta.Review(self.capital_deck, self.mock_status_scheme, "input")
    

class TestDeck(unittest.TestCase):
    # a deck object should:
    #     - be able to accept/reject cards based on filter criteria
    def test_filter(self):
        default_ds = carta_local.CsvDataSource("Testing/csv_test.csv")
        default_dset = carta.DataSet(default_ds)
        filter_fn = (lambda x: x.back_side[0] == "1")
        filtered_deck = carta.Deck(default_dset, "field_one", "field_two", carta.CardDisplayScheme(), filter_fn=filter_fn)
        self.assertTrue(filtered_deck.num_cards() == 1)
        
    #     - load from a data set object dynamically
    #      [not implemented]
    #     - push data to a data set object if specified
    #     - render cards based on an attached display scheme
    def test_rendering(self):
        default_ds = carta_local.CsvDataSource("countries.csv")
        default_dset = carta.DataSet(default_ds)
        sample_display_scheme = carta.CardDisplayScheme()
        sample_deck = carta.Deck(default_dset, "Name", "Capital", sample_display_scheme)
        for i, card in enumerate(sample_deck.cards):
            self.assertTrue(sample_deck.render_front(index=i) == sample_display_scheme.render_front(card.front_side))
            self.assertTrue(sample_deck.render_back(index=i) == sample_display_scheme.render_back(card.back_side))

class TestDefaultStreakReview(unittest.TestCase):
    # a default streak review object should:
    # -
    pass

class TestDefaultLeitnerReview(unittest.TestCase):
    # a default leitner review object should:
    # -
    pass

if __name__ == "__main__":
    unittest.main()
