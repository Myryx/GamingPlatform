from threading import Thread
import threading
import botlab
import config
import time
from user import User
from menuMaker import menu_maker
bot = botlab.BotLab(config.SETTINGS)

class ClockTimer:
    @staticmethod
    def count_deposit_availability_time(time_interval, session, message_id):
        if User.get_user_by_id(session.chat_id, session).wallet.depositTimeLeft > 0:
            if User.get_user_by_id(session.chat_id, session).current_tab == 1:
                bot.edit_message_text(
                    session._('MakeYourBitcoinDeposit') + ' *' + User.get_user_by_id(session.chat_id, session).wallet.depositTemporaryWalletAddress +
                    '*' + '\n\n' + session._('TimeLeft') + '*' +
                    str(User.get_user_by_id(session.chat_id, session).wallet.depositTimeLeft) + '*',
                    session.chat_id, message_id,
                    reply_markup=menu_maker.tab_menu(session, 1), parse_mode='markdown')
            user_obj = User.get_user_by_id(session.chat_id, session)
            user_obj.wallet.depositTimeLeft -= time_interval
            User.record_user(user_obj, session)
            threading.Timer(time_interval, ClockTimer.count_deposit_availability_time, [time_interval, session, message_id]).start()

    @staticmethod
    def start_queue_clock(time_interval, session, message_id, game_name):
        if User.get_user_by_id(session.chat_id, session).information.queue_time is not None and not User.get_user_by_id(
                session.chat_id, session).information.is_in_game:
            if User.get_user_by_id(session.chat_id, session).current_tab == 0:
                bot.edit_message_text(text='Time in queue for ' + game_name + ' ' + str(
                    User.get_user_by_id(session.chat_id, session).information.queue_time)
                                           + '\n\n',
                                      chat_id=session.chat_id,
                                      message_id=message_id,
                                      reply_markup=menu_maker.tab_menu(session, 0), parse_mode='markdown')
            user_obj = User.get_user_by_id(session.chat_id, session)
            user_obj.information.queue_time += time_interval
            User.record_user(user_obj, session)
            threading.Timer(1, ClockTimer.start_queue_clock, [1, session, message_id, game_name]).start()
