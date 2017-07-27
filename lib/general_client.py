import utils.poster
import utils.global_config


def general_post(sid, path, **kwargs):
    poster = utils.poster.Poster
    ret = poster.post_data_general(sid, path, **kwargs)
    return ret
