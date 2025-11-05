import random 

dices = [4, 6, 8, 10, 12, 20, 100]

def roll_dice(num_dice, num_sides):
    return [random.randint(1, num_sides) for _ in range(num_dice)]