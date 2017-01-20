from .card import SUITS
from .card import RANKS
from .card import VALUES
from .card import Card
import random


class Deck:
    def __init__(self, deck_amount=5):
        self.cards = []
        for i in range(deck_amount):
            for suit in SUITS:
                for rank in RANKS:
                    self.cards.append(Card(suit, rank))
        self.shuffle()

    def dict_representation(self):
        for i in range(len(self.cards)):
            self.cards[i] = self.cards[i].__dict__
        return self.__dict__

    @staticmethod
    def create_deck(dict):
        deck = Deck()
        for i in range(len(dict['cards'])):
            deck.cards.append(Card(dict['cards'][i]['suit'], dict['cards'][i]['rank']))
        return deck

    def shuffle(self):
        random.shuffle(self.cards)

    def pull_top_card(self, player_current_value=None, loyalty=None, win_chance=None):  # gives the top card from the deck
        if player_current_value is None and win_chance is None and loyalty is None:
            return self.cards.pop(0)
        else:
            max_possible = 21 - player_current_value
            drawn_card = self.cards.pop(0)
            if loyalty < 50 and VALUES[drawn_card.rank] > max_possible and random.randint(0, 99) < (loyalty + win_chance) / 2 - 50:
                return self.cards.pop(0)  # let's try again
            elif loyalty > 50 and VALUES[drawn_card.rank] <= max_possible and random.randint(0, 99) < 50 - (loyalty + win_chance) / 2:
                return self.cards.pop(0)  # sorry, this card isn't for you even if you weren't overdrawn
            else:
                return drawn_card

    def pull_ace(self):
        return Card('club', 'A')

    def pull_king(self):
        return Card('club', 'K')

    def pull_nine(self):
        return Card('club', '9')

    def pull_ten(self):
        return Card('club', '10')

    def __str__(self):
        result = ""
        for card in self.cards:
            result += " " + card.__str__()

        return "Deck contains" + result
