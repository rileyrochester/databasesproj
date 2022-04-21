

class Pokemon():

    # TODO : maybe add type2=None as default?
    def __init__(self, id, name, type1, type2, total, hp, attack, defense,
                    spAttack, spDefense, speed, generation, legendary):
        self.id = id
        self.name = name
        self.type1 = type1
        self.type2 = type2
        self.total = total
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.spAttack = spAttack
        self.spDefense =spDefense
        self.speed = speed
        self.generation = generation
        self.legendary = legendary

