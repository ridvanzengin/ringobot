import logging
import time
import datetime


def timing(f):
    def wrap(*args):
        now = datetime.datetime.now()
        logging.info(f"{f.__name__} started at {now}")
        print(f"[{now}] {f.__name__} started")

        time1 = time.time()
        ret = f(*args)
        time2 = time.time()

        duration_ms = (time2 - time1) * 1000.0
        logging.info(f"{f.__name__} took {duration_ms:.3f} ms")
        print(f"[{now}] {f.__name__} took {duration_ms:.3f} ms")

        return ret

    return wrap


def calculate_max_qty(price, budget, min_quantity):
    max_lots = int(budget / price / min_quantity)
    quantity = round(max_lots * min_quantity, 6)  # Round to 6 decimal places
    return quantity


def calculate_max_sell_qty(asset_balance, min_quantity):
    max_qty = int(asset_balance / min_quantity) * min_quantity
    return round(max_qty, 6)  # Round to 6 decimal places


class Standardize(object):
    def __init__(self, means, stds):
        """function generating function
        it carries mean of the dataset to 0,
        and std of the dataset to 1

        Args:
            means (list): means of features 1d vector
            stds (list): stds of features 1d vector
        """
        self.means = means
        self.stds = stds

    def __call__(self, windows):
        return (windows - self.means) / self.stds

    @staticmethod
    def apply(windows, means, stds):
        return (windows - means) / stds
