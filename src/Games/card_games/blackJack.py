import botlab
import config
import telebot
import time
import jsonpickle as json
from Games import game
from .card import Card
from .deck import Deck
from .hand import Hand
from user import User
from System import System


bot = botlab.BotLab(config.SETTINGS)


class BlackJack(game.Game):
    def __init__(self, user, bet):
        super().__init__()
        self.user = user
        # initialize dealer and player
        self.player_hand = Hand()
        self.dealer_hand = Hand()

        self.deck = Deck()  # fresh shuffled deck
        self.bet_value = bet  # default bet value
        self.is_dealer_turn = False
        self.can_continue = True

    def dict_representation(self):
        self.user = self.user.dict_representation()
        self.player_hand = self.player_hand.dict_representation()
        self.dealer_hand = self.dealer_hand.dict_representation()
        self.deck = self.deck.dict_representation()
        return self.__dict__

    @staticmethod
    def recreate_blackjack(dictionary):

        b = BlackJack(None, dictionary['bet_value'])
        b.user = User.recreate_user(dictionary['user'])
        b.player_hand = Hand.create_hand(dictionary['player_hand'])
        b.dealer_hand = Hand.create_hand(dictionary['dealer_hand'])
        b.deck = Deck.create_deck(dictionary['deck'])  # fresh shuffled deck
        b.can_continue = dictionary['can_continue']
        b.is_dealer_turn = dictionary['is_dealer_turn']
        return b

    def deal(self):
        self.can_continue = False
        # give them start cards
        self.dealer_hand.add_card(self.deck.pull_top_card())
        self.dealer_hand.add_card(self.deck.pull_top_card())

        self.player_hand.add_card(self.deck.pull_top_card())
        self.player_hand.add_card(self.deck.pull_top_card())

        # self.player_hand.add_card(self.deck.pull_ten())
        # self.player_hand.add_card(self.deck.pull_ace())

        if self.dealer_hand.get_value() == 21:  # OK, dealer has a blackjack

            if self.player_hand.get_value() == 21:  # if player has a blackjack too
                return 0  # it's a tie, push bets to their owners
            else:
                return -1  # dealer has instant 21, player doesn't, dealer wins

        elif self.player_hand.get_value() == 21:  # dealer doesn't have a blackjack and player does
            return 1  # player wins

        else:
            self.can_continue = True
            return 2  # everything is OK, continue game

    def hit(self, session=None):
        self.can_continue = False
        self.player_hand.add_card(self.deck.pull_top_card(self.player_hand.get_value(),
                                                          System.get_instance(session).win_chance,
                                                          User.get_user_by_id(session.chat_id, session).stats.loyalty))
        if self.player_hand.get_value() > 21:

            return -1  # player busted

        elif self.player_hand.get_value() < 21:
            self.can_continue = True
            return 0  # player not busted

        else:
            return 1  # player did a blackjack!

    def stand(self):

        self.can_continue = False
        self.is_dealer_turn = True

        while self.dealer_hand.get_value() < 17:  # dealer pulls cards until reaches 17 - soft 17 rule

            self.dealer_hand.add_card(self.deck.pull_top_card())  #

        if self.dealer_hand.get_value() > 21:

            return 1  # dealer busted

        elif self.dealer_hand.get_value() > self.player_hand.get_value():

            return -1  # dealer wins

        elif self.dealer_hand.get_value() == self.player_hand.get_value():

            return 0  # it's a tie, push bets to their owners

        elif self.dealer_hand.get_value() < self.player_hand.get_value():

            return 2  # player has a bigger value

    @staticmethod
    def send_deal(session, cbq):
        k = telebot.types.InlineKeyboardMarkup(row_width=5)
        k.add(telebot.types.InlineKeyboardButton(text=session._('Stand'), callback_data='stand'),
              telebot.types.InlineKeyboardButton(text=session._('Hit'), callback_data='hit'))

        bj = BlackJack.recreate_blackjack(session.get_field('game')[0])
        deal_result = bj.deal()

        if deal_result == 2 and User.is_in_game(session.chat_id, session):
            bot.edit_message_text(text=bj.display_current_game(session), chat_id=session.chat_id,
                                  message_id=cbq.message.message_id, reply_markup=k, parse_mode='markdown')  # continue

        elif deal_result == -1:
            User.set_is_in_game_by_id(False, session.chat_id, session)
            time.sleep(0.5)
            if User.is_in_game(session.chat_id, session):  # if didn't end the session
                bot.edit_message_text(text=bj.reveal_hidden_dealer_card(session), chat_id=session.chat_id,
                                      message_id=cbq.message.message_id, reply_markup=k,
                                      parse_mode='markdown')  # dealer's bj
            time.sleep(2)

            user = User.get_user_by_id(session.chat_id, session)
            user.loss(int(bj.bet_value))
            User.record_user(user, session)

            if User.is_in_game(session.chat_id, session):  # if didn't end the session
                bj.bets_changed_menu(session, cbq, session.get_field('bet')[0],
                                     bj.reveal_hidden_dealer_card(session) + '\n\n' + session._('DealerBJ'))

        elif deal_result == 1:  # Player has a blackjack

            time.sleep(0.5)
            bot.edit_message_text(text=bj.reveal_hidden_dealer_card(session), chat_id=session.chat_id,
                                  message_id=cbq.message.message_id, reply_markup=k,
                                  parse_mode='markdown')  # player's bj
            time.sleep(2)

            user = User.get_user_by_id(session.chat_id, session)
            user.win(int(bj.bet_value))
            User.record_user(user, session)
            if User.is_in_game(session.chat_id, session):  # if didn't end the session
                bj.bets_changed_menu(session, cbq, session.get_field('bet')[0],
                                     bj.reveal_hidden_dealer_card(session) + '\n\n' + session._('PlayerBJ'))
            User.set_is_in_game_by_id(False, session.chat_id, session)

        elif deal_result == 0 and User.is_in_game(session.chat_id, session):
            time.sleep(0.5)
            bot.edit_message_text(text=bj.reveal_hidden_dealer_card(session), chat_id=session.chat_id,
                                  message_id=cbq.message.message_id, reply_markup=k, parse_mode='markdown')  # tie
            time.sleep(1)

            user = User.get_user_by_id(session.chat_id, session)
            user.tie(0)
            User.record_user(user, session)
            if User.is_in_game(session.chat_id, session):  # if didn't end the session
                bj.bets_changed_menu(session, cbq, session.get_field('bet')[0],
                                     bj.reveal_hidden_dealer_card(session) + '\n\n' + session._('Tie'))
            User.set_is_in_game_by_id(False, session.chat_id, session)

        session.set_field('game', bj.dict_representation())

    @staticmethod
    def send_hit(session, cbq):
        k = telebot.types.InlineKeyboardMarkup(row_width=5)
        k.add(telebot.types.InlineKeyboardButton(text=session._('Stand'), callback_data='stand'),
              telebot.types.InlineKeyboardButton(text=session._('Hit'), callback_data='hit'))

        bj = BlackJack.recreate_blackjack(session.get_field('game')[0])

        hit_result = bj.hit(session)
        session.set_field('game', bj.dict_representation())  # we need a dump because we
        bj = BlackJack.recreate_blackjack(session.get_field('game')[0])
        if hit_result == 0 and User.is_in_game(session.chat_id, session):
            bot.edit_message_text(text=bj.display_current_game(session), chat_id=session.chat_id,
                                  message_id=cbq.message.message_id, reply_markup=k, parse_mode='markdown')  # continue

        elif hit_result == 1 and User.is_in_game(session.chat_id, session):
            bot.edit_message_text(text=bj.display_current_game(session), chat_id=session.chat_id,
                                  message_id=cbq.message.message_id, reply_markup=k, parse_mode='markdown')
            bj.send_stand(session, cbq)

        elif hit_result == -1:
            bot.edit_message_text(text=bj.display_current_game(session), chat_id=session.chat_id,
                                  message_id=cbq.message.message_id, reply_markup=k, parse_mode='markdown')
            time.sleep(0.5)

            user = User.get_user_by_id(session.chat_id, session)
            user.loss(int(bj.bet_value))
            User.record_user(user, session)
            if User.is_in_game(session.chat_id, session):
                session.set_field('bet', bj.bets_changed_menu(session, cbq, session.get_field('bet')[0],
                                     bj.display_current_game(session, True) + '\n\n' + session._('PlayerBusted')))
            User.set_is_in_game_by_id(False, session.chat_id, session)

        session.set_field('game', bj.dict_representation())

    @staticmethod
    def send_stand(session, cbq):
        k = telebot.types.InlineKeyboardMarkup(row_width=5)
        k.add(telebot.types.InlineKeyboardButton(text=session._('Stand'), callback_data='stand'),
              telebot.types.InlineKeyboardButton(text=session._('Hit'), callback_data='hit'))

        bj = BlackJack.recreate_blackjack(session.get_field('game')[0])
        dealer_result = bj.stand()

        time.sleep(1)
        if User.is_in_game(session.chat_id, session):
            bot.edit_message_text(text=bj.reveal_hidden_dealer_card(session), chat_id=session.chat_id,
                              message_id=cbq.message.message_id, reply_markup=k, parse_mode='markdown')  # continue

        time.sleep(1)
        i = 2
        while i < len(bj.dealer_hand.cards) and User.is_in_game(session.chat_id, session):
            bot.edit_message_text(text=bj.add_dealer_card_to_view(i, session), chat_id=session.chat_id,
                                  message_id=cbq.message.message_id, reply_markup=k, parse_mode='markdown')  # continue
            i += 1
            time.sleep(1.5)

        if dealer_result == 2:
            user = User.get_user_by_id(session.chat_id, session)
            user.win(int(bj.bet_value))

            User.record_user(user, session)
            if User.is_in_game(session.chat_id, session):
                bj.bets_changed_menu(session, cbq, session.get_field('bet')[0],
                                     bj.display_current_game(session, True) + '\n\n' + session._('PlayerWins'))
                User.set_is_in_game_by_id(False, session.chat_id, session)

        elif dealer_result == -1:
            user = User.get_user_by_id(session.chat_id, session)
            user.loss(int(bj.bet_value))
            User.record_user(user, session)
            if User.is_in_game(session.chat_id, session):
                bj.bets_changed_menu(session, cbq, session.get_field('bet')[0],
                                     bj.display_current_game(session, True) + '\n\n' + session._('DealerWins'))
                User.set_is_in_game_by_id(False, session.chat_id, session)

        elif dealer_result == 1 and User.is_in_game(session.chat_id, session):
            user = User.get_user_by_id(session.chat_id, session)
            user.win(int(bj.bet_value))
            User.record_user(user, session)
            if User.is_in_game(session.chat_id, session):
                bj.bets_changed_menu(session, cbq, session.get_field('bet')[0],
                                     bj.display_current_game(session, True) + '\n\n' + session._('DealerBusted'))
                User.set_is_in_game_by_id(False, session.chat_id, session)

        elif dealer_result == 0 and User.is_in_game(session.chat_id, session):
            user = User.get_user_by_id(session.chat_id, session)
            user.tie(0)
            User.record_user(user, session)
            if User.is_in_game(session.chat_id, session):
                bj.bets_changed_menu(session, cbq, session.get_field('bet')[0],
                                     bj.display_current_game(session, True) + '\n\n' + session._('Tie'))
                User.set_is_in_game_by_id(False, session.chat_id, session)

        session.set_field('game', bj.dict_representation())

    def display_current_game(self, session, show_all=False):
        answer = ''
        for idx, card in enumerate(self.dealer_hand.cards):
            if idx == 0 and not self.is_dealer_turn:  # first card in dealer hand
                answer += '?'  # we shouldn't reveal value of the first card
            else:
                answer += Card.make_card(card)
            answer += ' '
        answer += session._('DealerHas') + '*' + str(
            self.dealer_hand.get_value(self.is_dealer_turn, True, show_all)) + '*'
        answer += '\n\n'
        for card in self.player_hand.cards:
            answer += Card.make_card(card)
            answer += ' '
        answer += session._('YouHave') + '*' + str(self.player_hand.get_value()) + '*'
        return answer

    def add_dealer_card_to_view(self, idx,
                                session):  # this f. is for smooth step-by-step dealer drawing cards, idx is current limit
        answer = ''
        for i in range(0, idx + 1):
            answer += Card.make_card(self.dealer_hand.cards[i])
            answer += ' '
        answer += session._('DealerHas') + '*' + str(self.dealer_hand.evaluate_until(idx + 1)) + '*'
        answer += '\n\n'
        for card in self.player_hand.cards:
            answer += Card.make_card(card)
            answer += ' '
        answer += session._('YouHave') + '*' + str(self.player_hand.get_value()) + '*'
        return answer

    def reveal_hidden_dealer_card(self, session):
        answer = ''
        for idx, card in enumerate(self.dealer_hand.cards):
            if idx == 2: break
            answer += Card.make_card(card)
            answer += ' '
        answer += session._('DealerHas') + '*' + str(self.dealer_hand.evaluate_until(2)) + '*'
        answer += '\n\n'
        for card in self.player_hand.cards:
            answer += Card.make_card(card)
            answer += ' '
        answer += session._('YouHave') + '*' + str(self.player_hand.get_value()) + '*'
        return answer

    @staticmethod
    def bets_changed_menu(session, cbq, already_selected, final_text=''):
        final_text += '\n' + session._('YourBalance') + str(
            User.get_money(session.chat_id, session)) + '\n' + session._('YourBet')
        if User.get_money(session.chat_id, session) > 0:
            k = telebot.types.InlineKeyboardMarkup(row_width=5)
            bet_array = ['10', '20', '50', '100', '500']  # it's our bets
            if already_selected is not None:
                bet_array.remove(
                    already_selected)  # if we already have a bet, it won't be displayed in order to not being tapped
            button_array = []
            for i in reversed(bet_array):  # now remove all bets that are bigger than what user can afford
                if int(i) > User.get_money(session.chat_id, session):
                    bet_array.remove(i)
            for i in bet_array:
                button_array.append(telebot.types.InlineKeyboardButton(text=i, callback_data=i))  # finally add proper buttons

            if int(already_selected) > User.get_money(session.chat_id, session):
                already_selected = bet_array[len(bet_array) - 1]
                session.set_field('game', BlackJack(User.get_user_by_id(session.chat_id, session), already_selected).dict_representation())  # default bet

            k.add(*button_array)
            k.add(telebot.types.InlineKeyboardButton(text=already_selected + ' ' + session._('CoinsDeal'), callback_data='deal'))
            k.add(telebot.types.InlineKeyboardButton(text='Back', callback_data='back'))
            bot.edit_message_text(text=final_text, chat_id=session.chat_id, message_id=cbq.message.message_id,
                                  reply_markup=k, parse_mode='markdown')  # update bet

            return already_selected
        else:
            # PLEASE REPLACE THIS LATER ON FUNCTION FROM TEST. Couldn't make it because of fucking python import rules
            k = telebot.types.InlineKeyboardMarkup()
            k.add(telebot.types.InlineKeyboardButton(text=session._('FillWallet'), callback_data='fill'))
            k.add(telebot.types.InlineKeyboardButton(text=session._('ShareWithFriend'), callback_data='share'))
            k.add(telebot.types.InlineKeyboardButton(text=session._('BackToMain'), callback_data='back'))
            bot.edit_message_text(text=final_text, chat_id=session.chat_id, message_id=cbq.message.message_id,
                                  reply_markup=k, parse_mode='markdown')  # update bet
            return 0

