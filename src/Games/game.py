import botlab
import config
from user import User
# bot = botlab.BotLab(config.SETTINGS)


class Game:
    def __init__(self):
        None

    @staticmethod
    def text_in_game_tab(session):
        user = User.get_user_by_id(session.chat_id, session)
        if user.information.queue_time is not None:  # if user's in queue
            return 'Time in queue for ' + str(user.current_game) + ' ' + str(user.information.queue_time)
        else:
            return session._('Games')