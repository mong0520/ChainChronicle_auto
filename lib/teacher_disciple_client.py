import utils.poster
import time


IS_DISCIPLE_GRADUATED = False

# Teacher aciont
def toggle_acceptance(sid, accept=1, only_friend=0):
    path = '/teacher/toggle_acceptance'
    poster = utils.poster.Poster
    r = poster.post_data_general(sid, path=path, accept=accept, only_friend=only_friend)
    return r


# Disciple action
def apply_teacher(sid, tid):
    path = '/teacher/apply'
    poster = utils.poster.Poster
    r = poster.post_data_general(sid, path=path, tid=tid)
    return r


# Disciple action
def thanks_achievement(sid, lv):
    path = '/teacher/thanks_achievement'
    poster = utils.poster.Poster
    r = poster.post_data_general(sid, path=path, lv=lv)
    return r


# Disciple action
def reset_from_disciple(sid):
    path = '/teacher/reset_from_disciple'
    poster = utils.poster.Poster
    r = poster.post_data_general(sid, path=path)
    return


# Disciple action
def thanks_thanks_graduate(sid):
    path = '/teacher/thanks_graduate'
    poster = utils.poster.Poster
    r = poster.post_data_general(sid, path=path, friend=0)
    return r
