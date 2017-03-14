# -*- coding: utf-8 -*-
downgrade_coefficient = 10

class referral_link():
    def __init__(self, key):
        super().__init__()
        self.key = key
        self.is_updated = True
        self.current_coeff = 100

    @staticmethod
    def recreate_link(dictionary):
        link = referral_link(dictionary['key'])
        link.is_updated = dictionary['is_updated']
        link.current_coeff = dictionary['current_coeff']
        return link

    def downgrade_link(self):
        self.current_coeff = max(self.current_coeff - downgrade_coefficient, downgrade_coefficient)