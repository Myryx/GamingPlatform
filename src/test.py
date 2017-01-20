import botlab
import config
import telebot
from Games.game import Game
from ReferralGenerator import ReferralGenerator as generator
from Games.card_games.blackJack import BlackJack
from Games.card_games.dice import Dice
from user import User
from menuMaker import menu_maker
from block_io import BlockIo
from threading import Lock
from Games.queuer import queuer
from Games.gaming_room import Room
from System import System
from Finance import Finance
from PlatformConfiguration import Configuration




mutex = Lock()
block_io = BlockIo('c43e-6b4e-6842-dbf1', '9291027649kotik', 2)

bot = botlab.BotLab(config.SETTINGS)
referral_extra_size = 3
list_item_emoji = u'\U000025AA'

# -----------------------Menus creation-----------------------
def bets_menu(default, session):
    k = telebot.types.InlineKeyboardMarkup(row_width=5)
    bet_array = ['10', '20', '50', '100', '500']  # it's our bets
    if default is not None:
        bet_array.remove(default)  # if we already have a bet, it won't be displayed in order to not being tapped
    button_array = []
    for i in reversed(bet_array):
        if int(i) > User.get_money(session.chat_id, session):
            bet_array.remove(i)

    for i in bet_array:
        button_array.append(telebot.types.InlineKeyboardButton(text=i, callback_data=i))

    k.add(*button_array)

    if int(default) > User.get_money(session.chat_id, session):
        default = bet_array[len(bet_array) - 1]
    k.add(telebot.types.InlineKeyboardButton(text=default + ' ' + session._('CoinsDeal'), callback_data='deal'))
    k.add(telebot.types.InlineKeyboardButton(text=session._('Back'), callback_data='back'))
    return k

def start_playing():
    k = telebot.types.InlineKeyboardMarkup()
    k.add(telebot.types.InlineKeyboardButton(text='Start playing!', callback_data='start_that', url='https://telegram.me/blackJack1Bot?start=v6rlVHcFbHJqO'))
    return k

def edit_message_with_dump(text, chat_id, message_id, reply_markup, parse_mode, session, disable_web_page_preview=None):  # a little wrap for a dump
    user = User.get_user_by_id(chat_id, session)
    user.last_message = text
    user.last_message_id = message_id
    user.last_markup = reply_markup
    User.record_user(user, session)
    bot.edit_message_text(text=text, chat_id=chat_id, message_id=message_id,
                          reply_markup=reply_markup,
                          parse_mode=parse_mode,
                          disable_web_page_preview=disable_web_page_preview)

# -----------------------||||||||||||||||-----------------------

@bot.inline_handler(lambda query: True)
def query_text(session, inline_query):
    # if len(session.collection('queries').get_field('queries')) > 0:
    #     queries = session.collection('queries').get_field('queries')[0]
    #     queries.append(str(inline_query.id))
    # else:
    #     queries = [str(inline_query.id)]
    # session.collection('queries').set_field('queries', queries)  # put them back
    referral_id = User.get_referral_id(inline_query.from_user.id, session)
    url = 'http://www.jewelleryandwatchbirmingham.com/g/2016/logos/invitecolleague.jpg'
    title = session._('Referral_Title')
    invite_link = User.get_user_by_id(session.chat_id, session).referral_link
    message_content = telebot.types.InputTextMessageContent(message_text= session._('Referral_Description') + '\n' + list_item_emoji +
                                                                          session._('Convert_Your') + '\n' + list_item_emoji +
                                                                          session._('Play_With_Other') + '\n' + list_item_emoji +
                                                                          session._('Personal_Approach') + '\n' + session._('Click_this_link')
                                                                          + Configuration.telegram_link + invite_link.key + '@' + str(referral_id),
                                                            parse_mode='markdown', disable_web_page_preview=True)

    referral_content = telebot.types.InlineQueryResultArticle(inline_query.id, title, message_content, thumb_url=url)
    User.generate_user_referral_id(inline_query.from_user.id, session)
    bot.answer_inline_query(inline_query.id, [referral_content])
    edit_message_with_dump(session._('Main_Menu'),
                           inline_query.from_user.id, User.get_last_message_id(inline_query.from_user.id, session),
                           menu_maker.tab_menu(session, 2), 'markdown',
                           session)

@bot.message_handler(state='StartLanguages')
def state_a(session, message):
    if message.text is not None:
        # startup preparations:
        if len(session.collection('system').get_field('system_instance')) < 1:
            session.collection('system').set_field('system_instance', System(Configuration.win_chance).dict_representation())
        if len(session.collection('finance').get_field('finance_instance')) < 1:
            session.collection('finance').set_field('finance_instance', Finance().dict_representation())

        if User.get_user_by_id(message.from_user.id, session) is None:  # user is new
            user = User(message.from_user.id)
            user.generate_referral_id(session)

            if len(message.text.split()) > 1:
                start_text = message.text.split()[1]
                start_text = start_text.split('@')
                inviter_user_id = start_text[0][referral_extra_size:len(start_text[0]) - referral_extra_size]  # cut from start and from the end
                query_id = start_text[1]
                is_used = generator.check_referral(query_id, session)
                user.increase_start_bonus(Finance.get_start_via_invite_reward())
                if is_used:  # means that the referral was posted into a group chat
                    user.information.referral_used = 1
                    User.increase_user_start_bonus(int(inviter_user_id), session, Finance.get_public_invite_reward())
                else:  # if it's personal invite we appreciate it much more
                    user.information.referral_used = 2
                    User.increase_user_start_bonus(int(inviter_user_id), session, Finance.get_private_invite_reward())
            else:
                user.information.referral_used = 0
            User.record_user(user, session)
        else:
            if User.is_in_game(message.from_user.id, session):  # if user interrupted(maybe tried to cheat)
                # free up the room where the user been
                Room.remove_user_from_room_by_id(message.from_user.id, session.get_field('bet')[0], User.get_current_game(message.from_user.id, session), session)
                User.set_is_in_game_by_id(False, message.from_user.id, session)
                User.set_current_game(message.from_user.id, session, None)
                bot.edit_message_text(text=session._('GameWasTerminated'), chat_id=session.chat_id,
                                      message_id=User.get_last_message_id(message.from_user.id, session))
            else:
                bot.edit_message_text(text='––––––––––––––––––––––', chat_id=session.chat_id,
                                      message_id=User.get_last_message_id(message.from_user.id, session))

        session.set_field('last_tab', 0)
        session.reply_message('Which language do you prefer?', reply_markup=menu_maker.languages(), parse_mode='markdown')
    session.set_inline_state('SelectedLang')


@bot.callback_query_handler(inline_state='CameViaReferralButton')
def update_inline_state(session, cbq):
    session.set_field('last_tab', 0)
    session.reply_message('Which language do you prefer?', reply_markup=menu_maker.languages(), parse_mode='markdown')
    session.set_inline_state('SelectedLang')

@bot.callback_query_handler(inline_state='SelectedLang')
def update_inline_state(session, cbq):
    session.set_inline_state('MainMenu')
    session.set_lang(str(cbq.data))
    edit_message_with_dump(session._('Main_Menu'), session.chat_id, cbq.message.message_id,
                           menu_maker.tab_menu(session, session.get_field('last_tab')[0]), 'markdown', session)
    session.set_field('last_tab', 0)


@bot.callback_query_handler(inline_state='MainMenu')  # here we choose what to do
def update_inline_state(session, cbq):

    if cbq.data == 'games':
        text = Game.text_in_game_tab(session)
        edit_message_with_dump(text, session.chat_id, cbq.message.message_id,
                               menu_maker.tab_menu(session, 0), 'markdown', session)

    elif cbq.data == 'money':
        edit_message_with_dump(session._('YourBalance') + str(User.get_money(session.chat_id, session)) + '   ' +
                               session._('DepositBonus') + ': ' + str(User.get_user_bonus(session.chat_id, session)*100) + '%',
                               session.chat_id, cbq.message.message_id,
                               menu_maker.tab_menu(session, 1), 'markdown', session)

    elif cbq.data == 'social':
        edit_message_with_dump(session._('Main_Menu'),
                               session.chat_id, cbq.message.message_id,
                               menu_maker.tab_menu(session, 2), 'markdown', session)

    elif cbq.data == 'preferences':
        edit_message_with_dump(session._('Main_Menu'),
                               session.chat_id, cbq.message.message_id,
                               menu_maker.tab_menu(session, 3), 'markdown', session)


    elif cbq.data == 'get_link':
        link = ''
        if len(session.get_field('public_link')) == 0:
            link = generator.generate_public_link(session)

        edit_message_with_dump(link,
                               session.chat_id, cbq.message.message_id,
                               menu_maker.tab_menu(session, 2), 'markdown', session, True)

    elif cbq.data == 'langs':
        edit_message_with_dump('Which language do you prefer?',
                               session.chat_id, cbq.message.message_id,
                               menu_maker.languages(), 'markdown', session)

        session.set_field('last_tab', 3)
        session.set_inline_state('SelectedLang')

    elif cbq.data == 'back':
        edit_message_with_dump(session._('Main_Menu'),
                               session.chat_id, cbq.message.message_id,
                               menu_maker.tab_menu(session, 0), 'markdown', session)

    elif cbq.data == 'buy':
        # wallet = User.get_user_by_id(session.chat_id, session).wallet.claim_wallet_for_deposit(session)
        # if wallet is not None:
        #     user_obj = User.get_user_by_id(session.chat_id, session)
        #     user_obj.wallet.set_deposit_time(Configuration.deposit_time)
        #     user_obj.wallet.set_deposit_temporary_wallet_address(wallet['address'])
        #     User.record_user(user_obj, session)
            # ClockTimer.count_deposit_availability_time(60, session, cbq.message.message_id)  # 60 sec
        user_obj = User.get_user_by_id(session.chat_id, session)
        user_obj.wallet.create_bitcoin_wallet(str(session.chat_id))
        edit_message_with_dump(
            'Please, deposit your money to this address:\n' + user_obj.wallet.get_address_for_deposit()
            + '\nIt may take up to 20 minutes to proceed your deposit.',
            session.chat_id, cbq.message.message_id,
            menu_maker.tab_menu(session, 1), 'markdown',
            session)
        User.record_user(user_obj, session)



    elif cbq.data == 'vote':
        User.generate_user_referral_id(session.chat_id, session)
        edit_message_with_dump(session._('Main_Menu'),
                               session.chat_id, cbq.message.message_id,
                               menu_maker.tab_menu(session, 2), 'markdown',
                               session)

    elif cbq.data == 'blackjack':
        if User.get_money(session.chat_id, session) > 0 and User.get_money(session.chat_id, session) > Configuration.minimal_bet:
            edit_message_with_dump(session._('YourBalance') + str(
                User.get_money(session.chat_id, session)) + '\n\n' + session._('YourBet'),
                                   session.chat_id, cbq.message.message_id,
                                   bets_menu('50', session), 'markdown', session)

            session.set_field('game', BlackJack(User.get_user_by_id(session.chat_id, session),
                                                 'none').dict_representation())  # create a new one
            session.set_field('bet', 'none')  # create a new one
            session.set_inline_state('Blackjack')
        else:
            edit_message_with_dump(session._('NoMoney'),
                                   session.chat_id, cbq.message.message_id,
                                   menu_maker.no_money_menu(session), 'markdown', session)

    elif cbq.data == 'dice':
        if User.get_current_game(session.chat_id, session) != 'dice':
            if User.get_money(session.chat_id, session) > 0 and User.get_money(session.chat_id, session) > Configuration.minimal_bet:
                edit_message_with_dump(session._('YourBalance') + str(
                    User.get_money(session.chat_id, session)) + '\n\n' + session._('YourBet'),
                                       session.chat_id, cbq.message.message_id,
                                       bets_menu('50', session), 'markdown', session)

                session.set_field('bet', 'none')  # create a new one
                session.set_inline_state('Dice')
            else:
                edit_message_with_dump(session._('NoMoney'),
                                       session.chat_id, cbq.message.message_id,
                                       menu_maker.no_money_menu(session), 'markdown', session)

    elif cbq.data == 'dice_roll':
        session.set_inline_state('Dice')
        a = session.collection('dice' + 'Rooms').get_field(session.get_field('bet')[0])
        rooms = session.collection('dice' + 'Rooms').get_field(session.get_field('bet')[0])[
            0]  # all the room that exist

        needed_room = None  # we should find in which one the user is right now and wants to interact
        user_index = None
        room_index = None
        for j, room in enumerate(rooms):
            user_ids = [i[0] for i in room.users]
            for i, id in enumerate(user_ids):
                if session.chat_id == id:
                    needed_room = room
                    user_index = i
                    room_index = j
                    break
        Dice.send_dice_roll(needed_room, user_index, room_index, session)


# <-------------------------BlackJack-------------------------->


@bot.callback_query_handler(inline_state='Blackjack')  # User's chosen Blackjack
def update_inline_state(session, cbq):
    mutex.acquire()
    try:
        if cbq.data == '10' or cbq.data == '20' or cbq.data == '50' or cbq.data == '100' or cbq.data == '500':
            # bj = BlackJack(User.get_user_by_id(session.chat_id, session), cbq.data)
            # session.set_field('game', bj.dict_representation())
            session.set_field('bet', cbq.data)
            BlackJack.bets_changed_menu(session, cbq, cbq.data)  # save and output current bet

        elif cbq.data == 'deal':
            User.set_is_in_game_by_id(True, session.chat_id, session)
            if session.get_field('bet')[0] == 'none':
                session.set_field('bet', '50')
                session.set_field('game',
                                  BlackJack(User.get_user_by_id(session.chat_id, session),
                                            session.get_field('bet')[0]).dict_representation())
                BlackJack.send_deal(session, cbq)
            else:
                session.set_field('game',
                    BlackJack(User.get_user_by_id(session.chat_id, session),
                              session.get_field('bet')[0]).dict_representation())
                BlackJack.send_deal(session, cbq)

        elif cbq.data == 'hit' and session.get_field('game')[0]['can_continue']:
            BlackJack.send_hit(session, cbq)

        elif cbq.data == 'stand' and session.get_field('game')[0]['can_continue']:
            BlackJack.send_stand(session, cbq)

        elif cbq.data == 'back':
            edit_message_with_dump(session._('Main_Menu'),
                                   session.chat_id, cbq.message.message_id,
                                   menu_maker.tab_menu(session, 0), 'markdown', session)

            session.set_inline_state('MainMenu')
    finally:
        mutex.release()


@bot.callback_query_handler(inline_state='Dice')  # User's chosen Blackjack
def update_inline_state(session, cbq):
    # mutex.acquire()
    # try:
        if cbq.data == '10' or cbq.data == '20' or cbq.data == '50' or cbq.data == '100' or cbq.data == '500':
            session.set_field('bet', cbq.data)
            Dice.bets_changed_menu(session, cbq, cbq.data)  # save and output current bet
        elif cbq.data == 'deal':
            if session.get_field('bet')[0] == 'none':
                session.set_field('bet', '50')
            else:
                if int(session.get_field('bet')[0]) > User.get_money(session.chat_id, session):
                    User.downgrade_to_affordable_bet(session.chat_id, session)  # currently user balance is not null
                                                                                # because we wouldn't let it in the first place

            User.set_current_game(session.chat_id, session, 'dice')
            if queuer.queue_for_game('dice', session.get_field('bet')[0], cbq.message.message_id, session):  # if we have 5 ppl now
                room = Room('dice', 5, session)
                Dice.start(room, session)

            else:  # if there's not enough people yet
                session.set_inline_state('MainMenu')
                edit_message_with_dump('Time in queue for ' + 'dice' + ' ' + str(
                    User.get_user_by_id(session.chat_id, session).information.queue_time) + '\n\n',
                                       session.chat_id, cbq.message.message_id,
                                       menu_maker.tab_menu(session, 0), 'markdown', session)

        elif cbq.data == 'dice_roll':
            rooms = session.collection('dice' + 'Rooms').get_field(session.get_field('bet')[0])[0]  # all the room that exist

            needed_room = None  # we should find in which one the user is right now and wants to interact
            user_index = None
            room_index = None
            for j, room in enumerate(rooms):
                user_ids = [i[0] for i in room.users]
                for i, id in enumerate(user_ids):
                    if session.chat_id == id:
                        needed_room = room
                        user_index = i
                        room_index = j
                        break
            if needed_room:
                if needed_room.users[user_index][2] == '?':
                    Dice.send_dice_roll(needed_room, user_index, room_index, session)
        elif cbq.data == 'again':
            if User.get_money(session.chat_id, session) > 0:
                edit_message_with_dump(session._('YourBalance') + str(
                    User.get_money(session.chat_id, session)) + '\n\n' + session._('YourBet'),
                                       session.chat_id, cbq.message.message_id,
                                       bets_menu(session.get_field('bet')[0], session), 'markdown', session)

            else:
                edit_message_with_dump(session._('NoMoney'),
                                       session.chat_id, cbq.message.message_id,
                                       menu_maker.no_money_menu(session), 'markdown', session)

        elif cbq.data == 'exit' and not User.is_in_game(session.chat_id, session):
            edit_message_with_dump(session._('Main_Menu'),
                                   session.chat_id, cbq.message.message_id,
                                   menu_maker.tab_menu(session, 0), 'markdown', session)

            session.set_inline_state('MainMenu')

        elif cbq.data == 'back':
            edit_message_with_dump(session._('Main_Menu'),
                                   session.chat_id, cbq.message.message_id,
                                   menu_maker.tab_menu(session, 0), 'markdown', session)

            session.set_inline_state('MainMenu')

    # finally:
    #     mutex.release()
bot.polling(timeout=1)


#  <------------------------------------------------------------>
