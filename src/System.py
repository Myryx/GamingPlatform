# -*- coding: utf-8 -*-
class System:  # class to keep all the info about the user
    def __init__(self, win_chance):
        self.bots_amount = 0  # bots that are online and playing
        self.wins = [0, 0]  # [blackjack, dice]
        self.draws = [0, 0]  # [blackjack, dice]
        self.losses = [0, 0]  # [blackjack, dice]
        self.money_lost = [0, 0]  # [blackjack, dice]
        self.money_won = [0, 0]  # [blackjack, dice]
        self.win_chance = win_chance

    @staticmethod
    def recreate(dict):
        system = System(dict['win_chance'])
        system.bots_amount = dict['bots_amount']
        system.wins = dict['wins']
        system.draws = dict['draws']
        system.losses = dict['losses']
        system.money_lost = dict['money_lost']
        system.money_won = dict['money_won']
        return system

    def dict_representation(self):
        return self.__dict__

    @staticmethod
    def get_instance(session):
        return System.recreate(session.collection('system').get_field('system_instance')[0])

    @staticmethod
    def add_bot(session):
        system = System.recreate(session.collection('system').get_field('system_instance')[0])
        system.bots_amount += 1
        session.collection('system').set_field('system_instance', system.__dict__)

    @staticmethod
    def add_dice_loss(session, bet):
        system = System.recreate(session.collection('system').get_field('system_instance')[0])
        system.losses = [system.losses[0], system.losses[1] + 1]
        system.money_lost = [system.money_lost[0], system.money_lost[1] + int(bet)]
        session.collection('system').set_field('system_instance', system.__dict__)

    @staticmethod
    def add_dice_win(session, bet):
        system = System.recreate(session.collection('system').get_field('system_instance')[0])
        system.wins = [system.wins[0], system.wins[1] + 1]
        system.money_won = [system.money_won[0], system.money_won[1] + int(bet)]
        session.collection('system').set_field('system_instance', system.__dict__)

    @staticmethod
    def release_bots(session, amount):
        system = System.recreate(session.collection('system').get_field('system_instance')[0])
        system.bots_amount -= amount
        session.collection('system').set_field('system_instance', system.__dict__)
