# -*- coding: utf-8 -*-
import random
from Referral_Link import referral_link as link

size = 3

chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
digits = "1234567890"

class ReferralGenerator:
    def __init__(self):
        super().__init__()

    @staticmethod
    def generate_invite_link(id):
        prefix = "".join(random.choice(chars) for _ in range(size))
        postfix = "".join(random.choice(chars) for _ in range(size))
        key = prefix + str(id) + postfix
        return link(key)

    @staticmethod
    def generate_referral_id(session):
        if len(session.collection('referrals').get_field('referrals')) > 0:
            referrals = session.collection('referrals').get_field('referrals')[0]
        else:
            referrals = []
        while True:
            potential_referral_identifier = "".join(random.choice(digits) for _ in range(15))
            used_potential_referral_identifier = potential_referral_identifier + 'u'
            if potential_referral_identifier not in referrals and used_potential_referral_identifier not in referrals:
                referrals.append(potential_referral_identifier)
                session.collection('referrals').set_field('referrals', referrals)
                return potential_referral_identifier

    @staticmethod
    def check_referral(query_id, session):
        referrals = session.collection('referrals').get_field('referrals')[0]
        used_referral_query = query_id + 'u'  # we will check in the list if this query has already been used
        is_used = None
        is_not_used_index = None
        if used_referral_query in referrals:
            is_used = True  # referral was user once and cannot be private anymore
        elif query_id in referrals:  # referral is fresh and wasn't used so we can reward much higher
            is_not_used_index = referrals.index(query_id)  # get index of fresh referral so we can waste it
        if is_used and is_not_used_index is None:
            return True  # referral has been used once
        else:
            referrals[is_not_used_index] = query_id + 'u'  # waste the referral
            session.collection('referrals').set_field('referrals', referrals)
            return False
