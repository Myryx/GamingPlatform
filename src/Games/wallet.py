# -*- coding: utf-8 -*-
import botlab
import config
from Finance import Finance
from time import strftime
from Games.BitcoinWallet import BitcoinWallet

bot = botlab.BotLab(config.SETTINGS)
bit_address = '31sDkFNrXs5E2yNuZxB2URS3JT5pZXxR2N'

start_money = 1500
personal_bonus_boost = 0.5  # 50% boost for deposits
public_bonus_money = 0.1  # 10% boost for inviting through group chats

class Wallet:
    def __init__(self, money=start_money):
        self.money = money
        self.depositTemporaryWalletAddress = ''
        self.depositTimeLeft = -1  # in minutes
        self.transactions = []  # history of transactions of this wallet
        self.deposit_bonus = 1  # by default 100% bonus
        self.bitcoin_wallet = None

    def set_deposit_time(self, time):
        self.depositTimeLeft = time

    def set_deposit_temporary_wallet_address(self, address):
        self.depositTemporaryWalletAddress = address

    def create_bitcoin_wallet(self, id):
        self.bitcoin_wallet = BitcoinWallet(id)

    def get_address_for_deposit(self):
        return self.bitcoin_wallet.get_address_for_deposit()

    @staticmethod
    def recreate_wallet(dict):
        wallet = Wallet(dict['money'])
        wallet.depositTemporaryWalletAddress = dict['depositTemporaryWalletAddress']
        wallet.transactions = dict['transactions']
        wallet.depositTimeLeft = dict['depositTimeLeft']
        wallet.deposit_bonus = dict['deposit_bonus']
        if wallet.bitcoin_wallet is not None:
            wallet.bitcoin_wallet = BitcoinWallet.recreate_bitcoin_wallet(dict['bitcoin_wallet'])
        return wallet

    def manage_money(self, amount):
        if self.money + amount >= 0:
            self.money += amount
            return True
        else:
            return False

    def increase_deposit_bonus(self, percent_amount):
        self.deposit_bonus += percent_amount

    @staticmethod
    def transfer_money(from_wallet, to_wallet, amount):
        from_wallet.manage_money(-amount)
        to_wallet.manage_money(amount)
        block_io.withdraw_from_addresses(amounts=amount, from_addresses=from_wallet.bitcoinWalletNumber,
                                         to_addresses=to_wallet.bitcoinWalletNumber)

    def claim_wallet_for_deposit(self, session):
        # wallet_to_claim = None
        wallets = Finance.get_wallets(session)
        free_wallets = [x for i, x in enumerate(Finance.get_wallets(session)) if x['user_id'] == -1]
        if len(free_wallets) > 0:
            wallet_to_claim = free_wallets[0]
        else:
            print("WARNING! NO FREE WALLETS FOR DEPOSIT")
            return None

        wallet_to_claim['user_id'] = session.chat_id  # bind this wallet to the user
        wallet_to_claim['label'] = strftime("%Y-%m-%d %H:%M:%S")  # and get the timestamp when it started
        Finance.update_wallet_by_address(session, wallet_to_claim['address'], wallet_to_claim)
        return wallet_to_claim
        # archived = [i['address'] for i in block_io.get_my_archived_addresses()['data']['addresses']]
        # print(archived)



