class Information:  # class to keep all the info about the user
    def __init__(self, referral_used=-1):  # 0 - came by himself(or found the link to bot); 1 - public referral; 2 - personal referral
        self.referral_used = referral_used
        self.queue_time = None
        self.is_in_game = False

    @staticmethod
    def recreate(dict):
        info = Information(dict['referral_used'])
        info.queue_time = dict['queue_time']
        info.is_in_game = dict['is_in_game']

        return info

    def set_is_in_game(self, true_or_false):
        self.is_in_game = true_or_false