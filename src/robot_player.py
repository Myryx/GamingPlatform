# -*- coding: utf-8 -*-
import user


class Robot(user.User):
    def __init__(self, session):
        id = 1
        robots = []
        if len(session.collection('robots').get_field('robots')) != 0:
            robots = session.collection('robots').get_field('robots')[0]
            id = len(session.collection('robots').get_field('robots')[0]) + 1
        super().__init__(id)
        robots.append(self)
        session.collection('robots').set_field('robots', robots)

