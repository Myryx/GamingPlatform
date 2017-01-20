from block_io import BlockIo
block_io = BlockIo('c43e-6b4e-6842-dbf1', '9291027649kotik', 2)
bit_address = '31sDkFNrXs5E2yNuZxB2URS3JT5pZXxR2N'
reward_for_public_referral = 0.1
reward_for_private_referral = 1
reward_for_starting_via_referral = 0.5
class Finance:  # class to keep all the info about the user
    def __init__(self):
        self.main_address = bit_address
        # wallets = block_io.get_my_addresses()['data']['addresses']
        # wallets.pop(0)
        # for wallet in wallets:
        #     wallet['user_id'] = -1
        # self.wallets = wallets  # without first element that is our own wallet

    @staticmethod
    def recreate(dict):
        finance = Finance()
        finance.main_address = dict['main_address']
        finance.wallets = dict['wallets']
        return finance

    @staticmethod
    def get_instance(session):
        return Finance.recreate(session.collection('finance').get_field('finance_instance')[0])

    @staticmethod
    def set_instance(session, instance):
        session.collection('finance').set_field('finance_instance', instance.dict_representation())

    @staticmethod
    def get_wallets(session):
        return Finance.get_instance(session).wallets

    @staticmethod
    def update_wallets(session, wallets):
        instance = Finance.get_instance(session)
        instance.wallets = wallets
        Finance.set_instance(session, instance)


    @staticmethod
    def update_wallet_by_address(session, address, wallet_instance):
        wallets = Finance.get_wallets(session)
        index = Finance.get_wallet_index_by_address(session, address)
        print(index[0])
        wallets[index[0]] = wallet_instance
        Finance.update_wallets(session, wallets)

    @staticmethod
    def get_public_invite_reward():
        return reward_for_public_referral

    @staticmethod
    def get_private_invite_reward():
        return  reward_for_private_referral

    @staticmethod
    def get_start_via_invite_reward():
        return reward_for_starting_via_referral





    @staticmethod
    def get_wallet_by_address(session, address):
        return [x for i, x in enumerate(Finance.get_wallets(session)) if x['address'] == address]

    @staticmethod
    def get_wallet_index_by_address(session, address):
        return [i for i, x in enumerate(Finance.get_wallets(session)) if x['address'] == address]

    def dict_representation(self):
        return self.__dict__
