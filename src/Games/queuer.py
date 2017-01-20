import botlab
import config
from Timer import ClockTimer
from user import User
from collections import deque
import random

room_size = 5
number_enough_toplay = 1

bot = botlab.BotLab(config.SETTINGS)


class queuer():
    def __init__(self):
        pass

    @staticmethod
    def queue_bot_for_game(bet, game_name, session):
        if len(session.collection(game_name).get_field(bet)) > 0:
            users = session.collection(game_name).get_field(bet)[0]
        else:
            return None
        users.append([-1, -1, '?'])
        session.collection(game_name).set_field(bet, users)  # put them back

    @staticmethod
    def queue_for_game(game_name, bet, last_msg_id, session):
        users = deque()
        if len(session.collection(game_name).get_field(bet)) > 0:
            users = session.collection(game_name).get_field(bet)[0]

        users.append([session.chat_id, last_msg_id, '?'])
        session.collection(game_name).set_field(bet, users)  # put them back
        user = User.get_user_by_id(session.chat_id, session)
        user.information.queue_time = 0
        User.record_user(user, session)

        if len(users) == number_enough_toplay:  # we've got 5 users queued for the game with this bet
            for i in range(room_size - number_enough_toplay):
                queuer.queue_bot_for_game(bet, game_name, session)
            random.shuffle(users)
            session.collection(game_name).set_field(bet, users)
            return True
        ClockTimer.start_queue_clock(1, session, last_msg_id, game_name)
        return False

    @staticmethod
    def get_first_n_players(game_name, bet, session, n):
        first_n_players = []
        all_players = session.collection(game_name).get_field(bet)[0]  # get all those users that are queued for the game with this bet

        for i in range(n):
            if all_players[0] is not None:
                first_n_players.append(all_players.popleft())
        return first_n_players

