import random

NAMES = ['Adam', 'Ade', 'Dan', 'David', 'Gav', 'Hugh', 'Itchy', 'Jamie', 'Jen', 'Leo', 'Liam', 'Luke', 'Richard',
         'Ryan', 'Scratchy', 'Vicki', 'Yogi', 'Nick']
CLASSES = ['barbarian', 'fighter', 'paladin', 'bard', 'sorcerer', 'warlock', 'cleric', 'druid', 'monk', 'ranger',
           'rogue', 'wizard', 'hacker', 'programmer', 'delivery manager', 'scrum master', 'business analyst', 'tester']
CHARACTER_ADJECTIVES = ['awesome', 'phenomenal', 'stupendous', 'mighty', 'magnificent', 'incredible', 'remarkable',
                        'sensational', 'astounding', 'wondrous', 'epic', 'brilliant']
CHARACTER_VERBS = ['slayer', 'destroyer', 'crusher', 'exterminator', 'slaughterer', 'wrecker', 'demolisher',
                   'executioner', 'killer', 'smasher', 'basher', 'masher', 'thrasher']
CHARACTER_ENEMIES = ['hippies', 'hipsters', 'people who walk too slowly', 'worlds', 'universes', 'nations', 'vermin',
                     'orcs', 'goblins', 'trolls', 'barbie dolls', 'my little ponies', 'pineapple pizza', 'ghosts',
                     'ghouls', 'skulls', 'evil', 'aliens', 'unvaccinated children', 'the mafia',
                     'people who hog the middle lane on the motorway', 'dragons', 'bacteria', 'viruses',
                     'the common cold', 'trees', 'giants', 'the kraken', 'sharks', 'sharks with lasers']
ENEMIES = ['hippy', 'hipster', 'person who walks too slowly', 'world', 'universe', 'nation', 'vermin',
           'orc', 'goblin', 'troll', 'barbie doll', 'my little pony', 'pineapple pizza slice', 'ghost',
           'ghoul', 'skull', 'evil thing', 'alien', 'unvaccinated child', 'mafia boss',
           'person who hogs the middle lane on the motorway', 'dragon', 'bacterium', 'virus', 'common cold', 'tree',
           'giant', 'kraken', 'shark', 'shark with laser']
OUTDOOR_LOCATION_TYPES = ['field of corn', 'field of wheat', 'field of barley', 'field of hops', 'field of dreams',
                          'heath', 'scrubland', 'muddy wasteland', 'industrial wasteland', 'garden', 'courtyard',
                          'forest', 'wood', 'thicket', 'valley', 'clearing', 'golf course', 'park', 'car park',
                          'botanical garden']
INDOOR_LOCATION_TYPES = ['room', 'cavern', 'bathroom', 'dining room', 'lounge', 'hallway', 'passage', 'cave',
                         'banqueting hall', 'dungeon', 'prison cell', 'cupboard', 'bedroom', 'trophy room', 'pool hall',
                         'bar', 'office', 'meeting room']
ALL_LOCATIONS = OUTDOOR_LOCATION_TYPES + INDOOR_LOCATION_TYPES
BUILDING_TYPES = ['house', 'derelict house', 'haunted house', 'castle', 'ruined castle', 'citadel', 'office block',
                  'shop', 'shopping centre', 'airport terminal', 'den of iniquity', 'tower block', 'bowling alley']
ADJECTIVES = ['ominous', 'frumpy', 'idle', 'rusty', 'sharp', 'blunt', 'shiny', 'untrustworthy', 'imperfect',
              'incomplete', 'disappointing', 'regrettable', 'fragile', 'thin', 'fat', 'big', 'little', 'heavy', 'light',
              'spiky', 'smooth', 'hairy', 'tangled', 'simple', 'complicated', 'intelligent', 'dumb']
NOUNS = ['biscuit', 'potted plant', 'lawnmower', 'dinner plate', 'hi-fi', 'car', 'table', 'chair', 'lamp', 'ornament',
         'sofa', 'bookcase', 'exercise bike', 'dog kennel', 'trophy', 'cattle prod', 'washing machine', 'dustbin']
COLOURS = ['red', 'green', 'blue', 'yellow', 'pink', 'purple', 'orange', 'brown', 'violet', 'ultraviolet', 'infrared',
           'aquamarine', 'turquoise', 'grey', 'white', 'black']
WEATHER = ['raining', 'sunny', 'windy', 'snowing', 'really really cold', 'foggy', 'scorching hot', 'drizzling',
           'cloudy', 'overcast', 'looking ominous', 'balmy', 'not bad for this time of year',
           'terrible for this time of year']
SIZES = ['huge', 'enormous', 'little', 'minuscule', 'tiny', 'big', 'small', 'microscopic', 'planetary scale', 'average']
VOWELS = "aeiouAEIOU"


def r(source_words):
    random_word = source_words[random.randint(0, len(source_words) - 1)]
    return random_word


def rt(source_words):
    return r(source_words).title()


def random_bool():
    return random.randint(0, 1) == 1


def check_if_attacked(current_enemy, sworn_enemy):
    if random.randint(0, 100) == 42:
        print(f'You have been attacked and killed by a malevolent {current_enemy}. Game over.')
        exit()

    if random.randint(0, 1000) == 42:
        print(f'You have been attacked and killed by a wild {sworn_enemy} which you were warned about at the '
              f'beginning, so you only have yourself to blame. Game over.')
        exit()


def check_if_game_won(objective_object, objective_location, current_location):
    if objective_object == current_location['object'] and objective_location == (f'{an(current_location["size"])} '
                                                                                 f'{current_location["type"]}'):
        print(f'Congratulations you have found the {objective_object}. You have completed the game')
        exit()


def display_current_location(current_location):
    if current_location['is_indoors']:
        print(f'You are in {an(current_location["size"])} {current_location["type"]} inside '
              f'{an(current_location["building_type"])}. There is {an(current_location["object"])} lying nearby. '
              f'This is not the object you are looking for. There is a harmless {current_location["enemy"]} '
              f'hanging around.')
    else:
        print(f'You are in {an(current_location["size"])} {current_location["type"]}. There is '
              f'{an(current_location["object"])} lying nearby. This is not the object you are looking for. There '
              f'is a harmless {current_location["enemy"]} hanging around. The weather is currently '
              f'{current_location["weather"]}.')


def sworn_enemy_appears():
    return random.randint(0, 100) == 42


def an(following_word):
    if following_word[0] in VOWELS:
        return f'an {following_word}'
    else:
        return f'a {following_word}'


def generate_location():
    new_location = {
        "is_indoors": random_bool(),
        "size": r(SIZES),
        "object": f'{r(ADJECTIVES)} {r(COLOURS)} {r(NOUNS)}',
        "enemy": f'{r(SIZES)} {r(ADJECTIVES)} {r(COLOURS)} {r(ENEMIES)}',
    }

    if new_location["is_indoors"]:
        new_location["building_type"] = r(BUILDING_TYPES)
        new_location["type"] = r(INDOOR_LOCATION_TYPES)
    else:
        new_location["weather"] = r(WEATHER)
        new_location["type"] = r(OUTDOOR_LOCATION_TYPES)

    return new_location


def create_and_describe_options(current_location):
    for compass_direction in ['north', 'south', 'east', 'west']:
        if not current_location.get(compass_direction):
            current_location[compass_direction] = generate_location()
        describe_option(compass_direction, current_location)


def describe_option(compass_direction, location):
    if location[compass_direction]['is_indoors']:
        print(f'To the {compass_direction} there is {an(location[compass_direction]["building_type"])}.')
    else:
        print(f'To the {compass_direction} there is {an(location[compass_direction]["type"])}.')


def handle_input(current_location):
    new_location = None

    while not new_location:
        print()
        response = input('What do you want to do?  >>>> ')
        print()

        if response.lower() == 'go north':
            current_location['north']['south'] = current_location
            new_location =  current_location['north']
        elif response.lower() == 'go south':
            current_location['south']['north'] = current_location
            new_location = current_location['south']
        elif response.lower() == 'go east':
            current_location['east']['west'] = current_location
            new_location = current_location['east']
        elif response.lower() == 'go west':
            current_location['west']['east'] = current_location
            new_location = current_location['west']
        elif response.lower() == f'go {chr(102)}{chr(117)}{chr(99)}{chr(107)} yourself':
            print("That's not very nice!!")
        elif response.lower() == 'quit':
            print("Thanks for playing. Goodbye")
            exit()
        else:
            print("I do not understand your instructions. Try something like 'go west'")

    return new_location


def main():
    current_location = generate_location()
    objective_object = f'{r(ADJECTIVES)} {r(COLOURS)} {r(NOUNS)}'
    objective_location = f'{r(SIZES)} {r(ALL_LOCATIONS)}'
    sworn_enemy = f'{r(SIZES)} {r(ADJECTIVES)} {r(COLOURS)} {r(ENEMIES)}'

    print(f'Your name is {rt(CHARACTER_ADJECTIVES)} {rt(NAMES)} the {rt(CLASSES)}, {rt(CHARACTER_VERBS)} '
          f'of {rt(CHARACTER_ENEMIES)} and it is your mission to seek out the {objective_object}, '
          f'which can only be found in the {objective_location}. You must also evade the '
          f'{sworn_enemy}, which is your sworn deadly enemy and will attempt to kill you if it sees you.')

    while True:
        print()

        check_if_attacked(current_location["enemy"], sworn_enemy)
        check_if_game_won(objective_object, objective_location, current_location)
        display_current_location(current_location)

        print()

        create_and_describe_options(current_location)
        current_location = handle_input(current_location)


if __name__ == "__main__":
    main()