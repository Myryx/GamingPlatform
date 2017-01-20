import botlab
import config
from coinbase.wallet.client import Client
# from user import User
bot = botlab.BotLab(config.SETTINGS)


# API key and secret
key = '7Cg05IXBaFPBwOCr'
secret = '9FiWjs1S5lUerj3tD0HRPNYHuPc7e8ln'

platform_account_id = "5a42246a-5eb3-5822-a36c-0083099f1a51"
customers_account_id = "4def6901-7e4d-5d99-8cef-9457df54f98a"

client = Client(key, secret)
main_account = client.get_account(platform_account_id)
customers_account = client.get_account(customers_account_id)

class BitcoinWallet:
    def __init__(self, user_id, isThereAccount = False):  # isThereAccount - if it was created on CoinBase, so we shouldn't init it
        self.account = None
        self.id = None
        if not isThereAccount:  # if there's sno account yet(basically constructor called first time)
            self.account = create_bitcoin_account(user_id)
            self.id = self.account.id
        self.waits_for_deposit = False

    def send_money_to(self, to_address, amount):
        self.account.send_money(to=to_address.address, amount=amount, currency='BTC', description='')

    def get_address_for_deposit(self):
        return self.account.create_address().address

    def unload_money_to_platform_bank(self):
        primary_account = client.get_primary_account()
        address = primary_account.create_address().address
        self.account.send_money(to=address, amount=self.account.balance.amount, currency='BTC', description='')

    @staticmethod
    def recreate_bitcoin_wallet(dict):
        if dict == '':
            return ''
        else:
            account = client.get_account(dict['id'])
            wallet = BitcoinWallet(None, True)  # we've got our account already, so don't make another one
            wallet.account = account
            wallet.id = dict['id']
            wallet.waits_for_deposit = dict['waits_for_deposit']
            return wallet

    # @staticmethod
    # def start_observing_for_deposit(time_interval, old_balance, session, message_id, wallet_id):
    #     if User.get_user_by_id(session.chat_id, session).wallet.bitcoin_wallet.waits_for_deposit:
    #         if client.get_account(wallet_id).balance.amount > User.get_user_by_id(session.chat_id, session).wallet.bitcoin_wallet.account.balance.amount
    #             user_obj = User.get_user_by_id(session.chat_id, session)
    #             user_obj
    #
    #     if User.get_user_by_id(session.chat_id, session).information.queue_time is not None and not User.get_user_by_id(
    #             session.chat_id, session).information.is_in_game:
    #         if User.get_user_by_id(session.chat_id, session).current_tab == 0:
    #             bot.edit_message_text(text='Time in queue for ' + game_name + ' ' + str(
    #                 User.get_user_by_id(session.chat_id, session).information.queue_time)
    #                                        + '\n\n',
    #                                   chat_id=session.chat_id,
    #                                   message_id=message_id,
    #                                   reply_markup=menu_maker.tab_menu(session, 0), parse_mode='markdown')
    #         user_obj = User.get_user_by_id(session.chat_id, session)
    #         user_obj.information.queue_time += time_interval
    #         User.record_user(user_obj, session)
    #         threading.Timer(1, ClockTimer.start_queue_clock, [1, session, message_id, game_name]).start()

def create_bitcoin_account(user_id):
    return client.create_account(name=str(user_id))
