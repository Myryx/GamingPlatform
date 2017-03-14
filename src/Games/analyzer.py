# -*- coding: utf-8 -*-
start_money = 2000

# import Ma
class analyzer:
    def __init__(self):
        print()


    @staticmethod
    def calculate_estimated_happiness(user):
        all_games = user.stats.wins + user.stats.loss  # we don't calculate draws right now
        if all_games > 0:
            win_percentage = user.stats.wins / all_games
        else:
            return -1
        money_won = user.wallet.money - start_money
        user_happiness = win_percentage + money_won

        return user_happiness
