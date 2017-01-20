import botlab
import config
import telebot
import time
import jsonpickle as json
from Games.queuer import queuer
bot = botlab.BotLab(config.SETTINGS)

class Room:
    def __init__(self, game_name, players_amount, session):
        self.bet = session.get_field('bet')[0]
        self.id = Room.create_id_for_new_room(game_name, self.bet, session)
        self.money_heap = 0
        self.game_name = game_name
        self.users = queuer.get_first_n_players(game_name, self.bet, session, players_amount)

    def __eq__(self, other):
        return self.id == other.id

    def remove_user_from_room(self, id):  # we don't actually modify the list of room users because it would bring a
                                            # pain in the ass due to complexity of the system
                                            # so we just make them null so like they exited the room before the end
        self.users = [x if x[0] != id else [0, 0, '-'] for x in self.users]

    @staticmethod
    def remove_user_from_room_by_id(user_id, bet, game_name, session):
        rooms = session.collection(game_name + 'Rooms').get_field(bet)[0]  # all the room that exist
        for j, room in enumerate(rooms):
            user_ids = [i[0] for i in room.users]
            for i, id in enumerate(user_ids):
                if user_id == id:
                    room.remove_user_from_room(user_id)

    @staticmethod
    def players_table_text_repr(room, you_idx, session):
        list = [i[2] for i in room.users]
        max_value_indices = Room.find_max_value(list)  # since some players can have equal results, it's a list and not just a single max value
        players_string = ''
        results_string = ''
        for i in range(len(room.users)):
            if i != you_idx:
                players_string += session._('Player') + '#' + str(++i) + '  '
            else:
                players_string += session._('You') + '  '
        for i, player in enumerate(room.users):
            if i != you_idx:
                if max_value_indices is not None and i in max_value_indices:
                    results_string += '*' + '      ' + str(player[2]) + '        ' + '*'
                else:
                    results_string += '      ' + str(player[2]) + '        '
            else:
                if max_value_indices is not None and i in max_value_indices:
                    results_string += '*' + '  ' + str(player[2]) + '    ' + '*'
                else:
                    results_string += '  ' + str(player[2]) + '    '
        return session._('Stake') + ': ' + str(room.money_heap) + '\n\n' + players_string + '\n' + results_string

    @staticmethod
    def winners_repr(players, winner_list, partition, is_you, idx, session):
        answer_string = ''
        players = [x for x in players if x[2] != '-']  # get rid of question mark
        max_value = max([i[2] for i in players])
        for i in range(len(players)):
            if players[i][0] in winner_list and players[i][2] == max_value:
                if players[i][0] == winner_list[0]:
                    pass
                else:
                    answer_string += ',' + ' '
                if is_you and i == idx:
                    answer_string += session._('You')
                else:
                    answer_string += session._('Player') + '#' + str(++i)

        if len(winner_list) == 1 and not is_you:
            answer_string += ' ' + session._('WinSingular')
        else:
            answer_string += ' ' + session._('WinPlural')

        answer_string += ' ' + str(partition)

        return answer_string

    @staticmethod
    def find_max_value(list):  # RETURNS INDEX, NOT VALUE!
        clean_list = [x for x in list if x != '?' and x != '-']  # get rid of question mark
        if len(clean_list) == 0:
            return None
        max_value = max(clean_list)
        indices = [i for i, x in enumerate(list) if x == max_value]  # iterates over the list and finds occurrences of max_value
        return indices

    @staticmethod
    def create_id_for_new_room(game_name, bet, session):
        return len(session.collection(game_name + 'Rooms').get_field(bet)) + 1


