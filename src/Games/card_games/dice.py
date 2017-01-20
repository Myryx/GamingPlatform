import jsonpickle as json
import botlab
import config
import telebot
import random
import time
from Games.wallet import Wallet
from Games.gaming_room import Room
from user import User
from menuMaker import menu_maker
from System import System
from PlatformConfiguration import Configuration

bot = botlab.BotLab(config.SETTINGS)


class Dice():
    def __init__(self):
        pass

    @staticmethod
    def start(room, session):
        rooms = []
        # check rooms for emptiness
        if len(session.collection(room.game_name + 'Rooms').get_field(room.bet)) > 0:  # if array of rooms is not empty
            rooms = session.collection(room.game_name + 'Rooms').get_field(room.bet)[0]  # get those that exist
        rooms.append(room)
        session.collection(room.game_name + 'Rooms').set_field(room.bet, rooms)  # put them back

        room_users_ids = [i[0] for i in room.users]  # get id of users in the room

        for id in room_users_ids:  # now take from users their bets
            if id == -1:  # if a bot
                System.add_bot(session)
                room.money_heap += int(room.bet)
                continue
            user = User.get_user_by_id(id, session)
            user.information.is_in_game = True
            user.wallet.manage_money(-int(room.bet))
            User.record_user(user, session)
            room.money_heap += int(room.bet)

        for i, user in enumerate(room.users):  # send messages
            if user[0] == -1:
                continue
            user_obj = User.get_user_by_id(user[0], session)
            msg = Room.players_table_text_repr(room, i, session)
            markup = menu_maker.dice_start(session)
            user_obj.last_message = msg
            user_obj.last_markup = markup
            bot.edit_message_text(text=msg, chat_id=user[0], message_id=user[1], reply_markup=markup,
                                  parse_mode='markdown')  # create games menu
            User.record_user(user_obj, session)
        Dice.send_bots_dice_roll(room, len(rooms) - 1, session)


    @staticmethod
    def send_bots_dice_roll(room, room_idx, session):
        room_bots_idcs = []
        for i, user in enumerate(room.users):
            if user[0] == -1:
                room_bots_idcs.append(i)
        random.shuffle(room_bots_idcs)
        time.sleep(random.randint(1, 10) / 10)

        for index in room_bots_idcs:  # for all bots
            time.sleep(random.randint(1, 10) / 10)
            room.users[index][2] = Dice.dice_roll()
            rooms = session.collection(room.game_name + 'Rooms').get_field(room.bet)[0]  # record that
            rooms[room_idx] = room
            session.collection(room.game_name + 'Rooms').set_field(room.bet, rooms)  # put them back

            for i, user in enumerate(room.users):
                if user[0] == -1 or user[0] == 0:
                    continue
                user_obj = User.get_user_by_id(user[0], session)
                msg = Room.players_table_text_repr(room, i, session)
                markup = menu_maker.dice_start(session)
                user_obj.last_message = msg
                user_obj.last_markup = markup
                if User.get_user_by_id(user[0], session).information.is_in_game:
                    bot.edit_message_text(text=msg, chat_id=user[0], message_id=user[1], reply_markup=markup,
                                          parse_mode='markdown')  # create games menu
                User.record_user(user_obj, session)

        results = [i[2] for i in room.users]
        if '?' not in results:
            Dice.send_win(room, session)

    @staticmethod
    def send_dice_roll(room, user_idx, room_idx, session):
        room.users[user_idx][2] = Dice.dice_roll()  # record user's dice roll result
        rooms = session.collection(room.game_name + 'Rooms').get_field(room.bet)[0]  # record that
        rooms[room_idx] = room
        session.collection(room.game_name + 'Rooms').set_field(room.bet, rooms)  # put them back


        for i, user in enumerate(room.users):
            if user[0] == -1 or user[0] == 0:
                continue
            user_obj = User.get_user_by_id(user[0], session)
            msg = Room.players_table_text_repr(room, i, session)
            markup = menu_maker.dice_start(session)
            user_obj.last_message = msg
            user_obj.last_markup = markup
            bot.edit_message_text(text=msg, chat_id=user[0], message_id=user[1], reply_markup=markup,
                                  parse_mode='markdown')  # create games menu
            User.record_user(user_obj, session)
        time.sleep(1)
        results = [i[2] for i in room.users]
        if '?' not in results:
            Dice.send_win(room, session)

        # time.sleep(1)

    @staticmethod
    def define_winners(players):
        list = [x[2] if x[2] != '-' else 0 for x in players]
        max_value = max(list)
        winners = [i for i, x in enumerate(list) if x == max_value]  # iterates over the list and finds indices of occurrences of max_value
        return [i[0] for x, i in enumerate(players) if x in winners]  # get ids of winners

    @staticmethod
    def send_win(room, session):
        winners_ids = Dice.define_winners(room.users)

        for user in room.users:  # manage losers
            if user[0] not in winners_ids:
                if user[0] == -1:
                    System.add_dice_loss(session, room.bet)
                    continue
                if user[0] == 0:
                    continue
                user_instance = User.get_user_by_id(user[0], session)
                user_instance.wallet.manage_money(int(room.bet))  # since loss always withdraws money, lets put some money to be withdrawn
                user_instance.loss(int(room.bet))  # we need it because amount of lost money affects user stats. Otherwise I would've made it 0

        part_of_money_to_be_given = room.money_heap / len(winners_ids)

        for winner_id in winners_ids:  # manage winners
            if winner_id == -1:
                System.add_dice_win(session, room.bet)
                continue
            if winner_id == 0:
                continue
            winner = User.get_user_by_id(winner_id, session)
            winner.win(part_of_money_to_be_given)  # reward a winner with his prize
            User.record_user(winner, session)

        for i, user in enumerate(room.users):
            if user[0] == -1 or user[0] == 0:  # if bot or leaver
                continue
            user_obj = User.get_user_by_id(user[0], session)
            msg = Room.players_table_text_repr(room, i, session) + '\n\n' + '*' + \
                  Room.winners_repr(room.users, winners_ids, part_of_money_to_be_given, user[0] in winners_ids, i, session) + '*'

            if User.get_money(user[0], session) > Configuration.minimal_bet:
                markup = menu_maker.play_again(session)
            else:
                markup = menu_maker.no_money_menu(session)
            user_obj.last_message = msg
            user_obj.last_markup = markup
            bot.edit_message_text(text=msg,
                                  chat_id=user[0],
                                  message_id=user[1],
                                  reply_markup=markup,
                                  parse_mode='markdown')  # create games menu
            user_obj.set_is_in_game(False)
            user_obj.current_game = None
            User.record_user(user_obj, session)

        rooms = session.collection(room.game_name + 'Rooms').get_field(room.bet)[0]  # release rooms
        if room in rooms:
            rooms.remove(room)
        session.collection(room.game_name + 'Rooms').set_field(room.bet, rooms)  # put them back
        bots_amount = []
        for i, user in enumerate(room.users):
            if user[0] == -1:
                bots_amount.append(i)
        System.release_bots(session, len(bots_amount))


    @staticmethod
    def dice_roll():
        return random.randint(1, 6)

    @staticmethod
    def bets_changed_menu(session, cbq, already_selected, final_text=''):
        final_text += '\n' + session._('YourBalance') + str(User.get_money(session.chat_id, session)) + '\n' + session._('YourBet')
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
                button_array.append(
                    telebot.types.InlineKeyboardButton(text=i, callback_data=i))  # finally add proper buttons

            if int(already_selected) > User.get_money(session.chat_id, session):  # if user can't afford it
                already_selected = bet_array[len(bet_array) - 1]  # make his bet equal to max that he can afford
                session.set_field('bet', str(already_selected))

            k.add(*button_array)
            k.add(telebot.types.InlineKeyboardButton(text=already_selected + ' ' + session._('CoinsDeal'),
                                                     callback_data='deal'))
            k.add(telebot.types.InlineKeyboardButton(text='Back', callback_data='back'))

            user = User.get_user_by_id(session.chat_id, session)
            user.last_message = final_text
            user.last_markup = k
            User.record_user(user, session)
            bot.edit_message_text(text=final_text, chat_id=session.chat_id, message_id=cbq.message.message_id,
                                  reply_markup=k, parse_mode='markdown')  # update bet
            return already_selected
        else:
            # PLEASE REPLACE THIS LATER ON FUNCTION FROM TEST. Couldn't make it because of fucking python import rules
            k = telebot.types.InlineKeyboardMarkup()
            k.add(telebot.types.InlineKeyboardButton(text=session._('FillWallet'), callback_data='fill'))
            k.add(telebot.types.InlineKeyboardButton(text=session._('ShareWithFriend'), callback_data='share'))
            k.add(telebot.types.InlineKeyboardButton(text=session._('BackToMain'), callback_data='back'))
            user = User.get_user_by_id(session.chat_id, session)
            user.last_markup = k
            User.record_user(user, session)
            bot.edit_message_text(text=final_text, chat_id=session.chat_id, message_id=cbq.message.message_id,
                                  reply_markup=k, parse_mode='markdown')  # update bet
