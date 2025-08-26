#src\utils\throttle.py
import time
import random

def polite_sleep(min_s: float = 1.0, max_s: float = 2.0):
    time.sleep(random.uniform(min_s, max_s))
