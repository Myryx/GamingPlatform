SUITS = {'club', 'spade', 'heart', 'diamond'}
SUITS_VALUES = {'club': u'\U00002663', 'spade': u'\U00002660', 'heart': u'\U00002665', 'diamond': u'\U00002666', }
RANKS = ('A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K')
VALUES = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10}


class Card:
    def __init__(self, suit, rank):
        if (suit in SUITS) and (rank in RANKS):
            self.suit = suit
            self.rank = rank
        else:
            self.suit = None
            self.rank = None
            print("Invalid card: ", suit, rank)

    def __str__(self):  # print card representation
        return self.suit + self.rank

    def get_suit(self):
        return self.suit

    def get_rank(self):
        return self.rank

    @staticmethod
    def make_card(card):  # this is the method that generates text representation of the card
        return card.get_rank() + SUITS_VALUES[card.get_suit()]

