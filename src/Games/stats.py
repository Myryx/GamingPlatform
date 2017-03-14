# -*- coding: utf-8 -*-
# import botlab
# import config

# bot = botlab.BotLab(config.SETTINGS)


class Stats:  # class to keep all the info about the user
    def __init__(self, wins=0, draws=0, loss=0, loyalty=50, win_chance=47):
        self.wins = wins
        self.draws = draws
        self.loss = loss
        self.loyalty = loyalty  # user starts with average (up to 100)

        self.win_chance = win_chance  # that's the value that manipulates the probability

    @staticmethod
    def recreate_stats(dict):
        return Stats(dict['wins'], dict['draws'], dict['loss'], dict['loyalty'])

    def add_win(self):
        self.wins += 1


    def add_draw(self):
        self.draws += 1

    def add_loss(self):
        self.loss += 1

    def change_loyalty(self, bet):
        self.loyalty += bet / 50