from type_chart import get_multiplier


def attack(attacker, defender, move):
    multiplier = get_multiplier(move.type, defender.type)
    damage = int(move.power * multiplier)

    if damage < 1:
        damage = 1

    defender.hp -= damage
    if defender.hp < 0:
        defender.hp = 0

    return damage, multiplier