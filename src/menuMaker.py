# -*- coding: utf-8 -*-
import telebot
import jsonpickle as json
import botlab
import config
from user import User

bot = botlab.BotLab(config.SETTINGS)

class menu_maker():
    def __init__(self):
        super().__init__()

    @staticmethod
    def languages():  # function that creates languages menu
        k = telebot.types.InlineKeyboardMarkup()
        k.add(telebot.types.InlineKeyboardButton(text='English', callback_data='en'))
        k.add(telebot.types.InlineKeyboardButton(text='Русский', callback_data='ru'))
        return k

    @staticmethod
    def games_page(session):  # 0
        return [telebot.types.InlineKeyboardButton(text=session._('BlackJack'), callback_data='blackjack'),
                telebot.types.InlineKeyboardButton(text=session._('Dice'), callback_data='dice')]

    @staticmethod
    def money_page(session):  # 1
        return [telebot.types.InlineKeyboardButton(text=session._('Buy'), callback_data='buy'),
                telebot.types.InlineKeyboardButton(text=session._('Sell'), callback_data='sell'),
                telebot.types.InlineKeyboardButton(text=session._('Instruction'), callback_data='instruction')]

    @staticmethod
    def social_page(session, referral_id):  # 2
        return [telebot.types.InlineKeyboardButton(text=session._('Vote'), callback_data='vote'),
                telebot.types.InlineKeyboardButton(text=session._('Feedback'), callback_data='feedback'),
                telebot.types.InlineKeyboardButton(text=session._('Invite'), switch_inline_query=session._('InviteID') + referral_id),
                telebot.types.InlineKeyboardButton(text=session._('Get_Link'), callback_data='get_link')]

    @staticmethod
    def settings_page(session):  # 3
        return [telebot.types.InlineKeyboardButton(text=session._('Change_lang'), callback_data='langs')]

    @staticmethod
    def tab_menu(session, selected_tab):
        user = User.get_user_by_id(session.chat_id, session)
        user.current_tab = selected_tab  # dump his current tab so we will now at each time
        User.record_user(user, session)

        k = telebot.types.InlineKeyboardMarkup(row_width=5)

        games = session._('Games')
        money = session._('Money')
        social = session._('Social')
        settings = session._('Preferences')

        if selected_tab == 0:
            games += '  ' + u'\U00002714'
        elif selected_tab == 1:
            money += '  ' + u'\U00002714'
        elif selected_tab == 2:
            social += '  ' + u'\U00002714'
        elif selected_tab == 3:
            settings += '  ' + u'\U00002714'

        k.add(telebot.types.InlineKeyboardButton(text=games, callback_data='games'),
                telebot.types.InlineKeyboardButton(text=money, callback_data='money'),
                telebot.types.InlineKeyboardButton(text=social, callback_data='social'),
                telebot.types.InlineKeyboardButton(text=settings, callback_data='preferences'))

        if selected_tab == 0:
            menu_button_array = menu_maker.games_page(session)
            k.add(*menu_button_array)
        elif selected_tab == 1:
            menu_button_array = menu_maker.money_page(session)
            k.add(menu_button_array[0],
                  menu_button_array[1])
            k.add(menu_button_array[2])
        elif selected_tab == 2:
            menu_button_array = menu_maker.social_page(session, User.get_referral_id(session.chat_id, session))
            k.add(menu_button_array[0],
                  menu_button_array[1])
            k.add(menu_button_array[2])
            k.add(menu_button_array[3])
        elif selected_tab == 3:
            menu_button_array = menu_maker.settings_page(session)
            k.add(*menu_button_array)

        return k

    @staticmethod
    def bets_menu(default, session):  # function that creates different bets buttons(10,20,50,100,500)
        k = telebot.types.InlineKeyboardMarkup(row_width=5)
        bet_array = ['10', '20', '50', '100', '500']  # it's our bets
        if default is not None:
            bet_array.remove(
                default)  # if we already have a bet, it won't be displayed in order to not being tapped
        if len(bet_array) == 0:
            return menu_maker.no_money_menu(session)

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

    @staticmethod
    def dice_start(session):
        k = telebot.types.InlineKeyboardMarkup()
        k.add(telebot.types.InlineKeyboardButton(text=session._('Roll_The_Dice'), callback_data='dice_roll'))
        k.add(telebot.types.InlineKeyboardButton(text=session._('Exit'), callback_data='dice_exit'))
        return k

    @staticmethod
    def no_money_menu(session):
        k = telebot.types.InlineKeyboardMarkup()
        k.add(telebot.types.InlineKeyboardButton(text=session._('FillWallet'), callback_data='fill'))
        k.add(telebot.types.InlineKeyboardButton(text=session._('ShareWithFriend'), callback_data='share'))
        k.add(telebot.types.InlineKeyboardButton(text=session._('Back'), callback_data='back'))
        return k

    @staticmethod
    def play_again(session):
        k = telebot.types.InlineKeyboardMarkup()
        k.add(telebot.types.InlineKeyboardButton(text=session._('Play_Again'), callback_data='again'))
        k.add(telebot.types.InlineKeyboardButton(text=session._('Exit'), callback_data='exit'))
        return k


