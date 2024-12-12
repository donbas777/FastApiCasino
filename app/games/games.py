import random


def play_rollet():
    r = random.randint(0, 37)
    cl = "xxxx"
    if r == 0:
        cl = "green"
    if r in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]:
        cl = "red"
    else:
        cl = "black"
    return [r, cl]

def play_slots():
    variants = ["7", "0", "1", "9", "8", "4"]
    result = []
    for i in range(3):
        res = []
        for j in range(3):
            r = random.choice(variants)
            res.append(r)
        result.append(res)
    return result

def play_roll_dice():
    result = []
    for i in range(2):
        r = random.randint(1, 7)
        result.append(r)
    return result
