# -*- coding: utf-8 -*-
from Games.wallet import Wallet
from Games.stats import Stats
from information import Information
from ReferralGenerator import ReferralGenerator
import jsonpickle as json

class User:
    def __init__(self, id):
        self.id = id
        self.wallet = Wallet()
        self.stats = Stats()
        self.information = Information()
        self.last_message = ''  # we need these because we want sometimes to add smth to existing text but without
        self.last_message_id = None
        self.last_markup = None  # knowing exactly what it is. So we will just take this and add what we want
        self.current_tab = 0  # game tab by default
        self.current_game = None
        self.referral_link = ReferralGenerator.generate_invite_link(id)
        self.referral_id = None

    @staticmethod
    def recreate_user(dictionary):
        user = User(dictionary['id'])
        user.wallet = Wallet.recreate_wallet(dictionary['wallet'])
        user.stats = Stats.recreate_stats(dictionary['stats'])
        user.information = Information.recreate(dictionary['information'])
        user.last_message = dictionary['last_message']
        user.last_message_id = dictionary['last_message_id']
        user.last_markup = dictionary['last_markup']
        user.current_tab = dictionary['current_tab']
        user.current_game = dictionary['current_game']
        user.referral_link = dictionary['referral_link']
        user.referral_id = dictionary['referral_id']
        return user

    @staticmethod
    def get_user_by_id(id, session):
        if session.collection('users').get_object({'id': id}) is not None:
            return User.recreate_user(session.collection('users').get_object({'id': id}))
        else:
            return None

    def dict_representation(self):
        self.wallet = self.wallet.__dict__
        self.stats = self.stats.__dict__
        self.information = self.information.__dict__
        return self.__dict__

    @staticmethod
    def get_money(id, session):
        return session.collection('users').get_object({'id': id})['wallet']['money']

    @staticmethod
    def get_current_game(id, session):
        return session.collection('users').get_object({'id': id})['current_game']

    @staticmethod
    def set_current_game(id, session, current_game):
        user = User.get_user_by_id(id, session)
        user.current_game = current_game
        User.record_user(user, session)

    @staticmethod
    def get_last_message(id, session):
        return User.get_user_by_id(id, session).last_message

    @staticmethod
    def get_last_markup(id, session):
        return User.get_user_by_id(id, session).last_markup

    @staticmethod
    def get_last_message_id(id, session):
        return User.get_user_by_id(id, session).last_message_id

    @staticmethod
    def is_in_game(id, session):
        return User.get_user_by_id(id, session).information.is_in_game

    @staticmethod
    def set_is_in_game_by_id(true_or_false, id, session):
        user = User.get_user_by_id(id, session)
        user.information.set_is_in_game(true_or_false)
        User.record_user(user, session)

    def set_is_in_game(self, true_or_false):
        self.information.set_is_in_game(true_or_false)

    @staticmethod
    def record_user(user, session):
        session.collection('users').set_object(user.dict_representation(), {'id': user.id})

    @staticmethod
    def get_all_users(session):
        return session.collection('users')

    @staticmethod
    def downgrade_to_affordable_bet(id, session):
        bet_array = ['10', '20', '50', '100', '500']  # it's our bets
        for i in reversed(bet_array):
            if int(i) > User.get_money(id, session):
                bet_array.remove(i)
        if len(bet_array) == 0:
            return False
        else:
            session.set_field('bet', bet_array[len(bet_array) - 1])
            return True

    @staticmethod
    def increase_user_start_bonus(id, session, percent_amount):
        user = User.get_user_by_id(id, session)
        user.wallet.increase_deposit_bonus(percent_amount)
        User.record_user(user, session)

    def increase_start_bonus(self, percent_amount):
        self.wallet.increase_deposit_bonus(percent_amount)

    @staticmethod
    def get_user_bonus(id, session):
        return User.get_user_by_id(id, session).wallet.deposit_bonus


    @staticmethod
    def encode_users(users):
        for i, user in enumerate(users):
            users[i] = json.encode(user.__dict__, unpicklable=False)
        return users

    def generate_referral_id(self, session):
        self.referral_id = ReferralGenerator.generate_referral_id(session)

    @staticmethod
    def generate_user_referral_id(id, session):
        user = User.get_user_by_id(id, session)
        user.referral_id = ReferralGenerator.generate_referral_id(session)
        User.record_user(user, session)

    @staticmethod
    def get_referral_id(id, session):
        return User.get_user_by_id(id, session).referral_id

    def win(self, bet):
        self.wallet.manage_money(bet)
        self.stats.add_win()
        self.stats.change_loyalty(bet)

    def tie(self, bet):
        self.wallet.manage_money(bet)
        self.stats.add_draw()
        self.stats.change_loyalty(bet)

    def loss(self, bet):
        self.wallet.manage_money(-bet)
        self.stats.add_loss()
        self.stats.change_loyalty(bet)

    def loss_with_bet_already_taken(self, bet):
        self.stats.add_loss()
        self.stats.change_loyalty(bet)


