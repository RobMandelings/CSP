from tqdm import tqdm


progressBars = dict()


def monitor(f):
    """ Decorator to time functions and count the amount of calls. """
    def wrapper(*args, **kwargs):
        if f not in progressBars:
            progressBars[f] = tqdm(desc=f.__name__, unit=" calls")
        progress = progressBars[f]
        progress.update(1)
        return f(*args, **kwargs)
    return wrapper
