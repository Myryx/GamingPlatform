from .card import VALUES
from .card import Card

class Hand:
    def __init__(self):
        self.cards = []

    def __str__(self):
        result = ""
        for card in self.cards:
            result += " " + card.__str__()

        return "Hand contains" + result

    @staticmethod
    def create_hand(dict):
        hand = Hand()
        for i in range(len(dict['cards'])):
            hand.cards.append(Card(dict['cards'][i]['suit'], dict['cards'][i]['rank']))
        return hand

    def dict_representation(self):
        for i in range(len(self.cards)):
            self.cards[i] = self.cards[i].__dict__
        return self.__dict__

    def add_card(self, card):
        self.cards.append(card)

    def get_value(self, is_dealer_turn=True, is_dealer_hand=False, show_all=False):  # count how much player or dealer has right now
                                             # boolean is for not counting dealer card
        # count aces as 1, if the hand has an ace, then add 10 to hand value if it doesn't bust

        if is_dealer_hand and not is_dealer_turn:
            if VALUES[self.cards[1].get_rank()] == 1:   #HERE'S INDEX OUT OF RANGE!!!!!!!!!
                return 11  # it's an ace
            return VALUES[self.cards[1].get_rank()]  #everything but ace

        value = 0
        contains_ace = False
        for card in self.cards:
            rank = card.get_rank()  # rank of current card
            value += VALUES[rank]  # it corresponding value as integer

            if rank == 'A':
                if is_dealer_hand and show_all:
                    contains_ace = True  # ace detected, so we should consider bust case
                else:
                    contains_ace = True  # ace detected, so we should consider bust case

        if not is_dealer_turn:
            value -= VALUES[self.cards[0].get_rank()]

        if value < 12 and contains_ace :  # if we ace doesn't lead to bust
            value += 10



        return value

    def evaluate_until(self, until):  # count how much player or dealer has right now
        # boolean is for not counting dealer card  # count aces as 1, if the hand has an ace, then add 10 to hand value if it doesn't bust

        value = 0
        contains_ace = False
        for i, card in enumerate(self.cards):
            if i < until:
                rank = card.get_rank()  # rank of current card
                value += VALUES[rank]  # it corresponding value as integer

                if rank == 'A':
                    contains_ace = True  # ace detected, so we should consider busted case

        if value < 12 and contains_ace:  # if we don't have an ace
            value += 10

        return value