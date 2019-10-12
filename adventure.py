import random

NAMES = ['Adam', 'Ade', 'Dan', 'David', 'Gav', 'Hugh', 'Itchy', 'Jamie', 'Jen', 'Leo', 'Liam', 'Luke', 'Richard',
         'Ryan', 'Scratchy', 'Vicki', 'Yogi', 'Nick']
CLASSES = ['barbarian', 'fighter', 'paladin', 'bard', 'sorcerer', 'warlock', 'cleric', 'druid', 'monk', 'ranger',
           'rogue', 'wizard', 'hacker', 'programmer', 'delivery manager', 'scrum master', 'business analyst', 'tester']
CHARACTER_SUPERLATIVES = ['awesome', 'phenomenal', 'stupendous', 'mighty', 'magnificent', 'incredible', 'remarkable',
                          'sensational', 'astounding', 'wondrous', 'epic', 'brilliant']
CHARACTER_ADVERBS = ['slayer', 'destroyer', 'crusher', 'exterminator', 'slaughterer', 'wrecker', 'demolisher',
                     'executioner', 'killer', 'smasher', 'basher', 'masher', 'thrasher']
CHARACTER_ENEMIES = ['hippies', 'hipsters', 'people who walk too slowly', 'worlds', 'universes', 'nations', 'vermin',
                     'orcs', 'goblins', 'trolls', 'barbie dolls', 'my little ponies', 'pineapple pizza', 'ghosts',
                     'ghouls', 'skulls', 'evil', 'aliens', 'unvaccinated children', 'the mafia',
                     'people who hog the middle lane on the motorway', 'dragons', 'bacteria', 'viruses',
                     'the common cold', 'trees', 'giants', 'the kraken', 'sharks', 'sharks with lasers']
ENEMIES = ['hippie', 'hipster', 'person who walks too slowly', 'world', 'universe', 'nation', 'vermin',
           'orc', 'goblin', 'troll', 'barbie doll', 'my little pony', 'pineapple pizza slice', 'ghost',
           'ghoul', 'skull', 'evil thing', 'alien', 'unvaccinated child', 'mafia boss',
           'person who hogs the middle lane on the motorway', 'dragon', 'bacterium', 'virus', 'common cold', 'tree',
           'giant', 'kraken', 'shark', 'shark with laser']
OUTDOOR_LOCATION_TYPES = ['field of corn', 'field of wheat', 'field of barley', 'field of hops', 'field of dreams',
                          'heath', 'scrubland', 'muddy wasteland', 'industrial wasteland', 'garden', 'courtyard',
                          'forest', 'wood', 'thicket', 'valley', 'clearing', 'golf course', 'park', 'car park',
                          'botanical garden', 'football pitch', 'frozen lake', 'school playground']
INDOOR_LOCATION_TYPES = ['room', 'cavern', 'bathroom', 'dining room', 'lounge', 'hallway', 'passage', 'cave',
                         'banqueting hall', 'dungeon', 'prison cell', 'cupboard', 'bedroom', 'trophy room', 'pool hall',
                         'bar', 'office', 'meeting room']
ALL_LOCATIONS = OUTDOOR_LOCATION_TYPES + INDOOR_LOCATION_TYPES
BUILDING_TYPES = ['house', 'derelict house', 'haunted house', 'castle', 'ruined castle', 'citadel', 'office block',
                  'shop', 'shopping centre', 'airport terminal', 'den of iniquity', 'tower block', 'bowling alley']
ADJECTIVES = ['ambivalent', 'frumpy', 'idle', 'rusty', 'sharp', 'blunt', 'shiny', 'untrustworthy', 'imperfect',
              'incomplete', 'disappointing', 'regrettable', 'fragile', 'thin', 'fat', 'delicious', 'heavy', 'light',
              'spiky', 'smooth', 'hairy', 'tangled', 'simple', 'complicated', 'intelligent', 'dumb']
NOUNS = ['biscuit', 'potted plant', 'lawnmower', 'dinner plate', 'hi-fi', 'car', 'table', 'chair', 'lamp', 'ornament',
         'sofa', 'bookcase', 'exercise bike', 'dog kennel', 'trophy', 'cattle prod', 'washing machine', 'dustbin']
COLOURS = ['red', 'green', 'blue', 'yellow', 'pink', 'purple', 'orange', 'brown', 'violet', 'ultraviolet', 'infrared',
           'aquamarine', 'turquoise', 'grey', 'beige', 'silver', 'gold']
WEATHER = ['raining', 'sunny', 'windy', 'snowing', 'really really cold', 'foggy', 'scorching hot', 'drizzling',
           'cloudy', 'overcast', 'looking ominous', 'balmy', 'not bad for this time of year',
           'terrible for this time of year']
SIZES = ['huge', 'enormous', 'little', 'minuscule', 'tiny', 'big', 'small', 'microscopic', 'planetary scale', 'average']
COMPASS_POINTS = ['north', 'south', 'east', 'west']
OPPOSITE_DIRECTIONS = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}
VOWELS = "aeiouAEIOU"


def r(source_words):
    random_word = source_words[random.randint(0, len(source_words) - 1)]
    return random_word


def rt(source_words):
    return r(source_words).title()


def check_if_attacked(current_enemy, sworn_enemy):
    if random.randint(0, 100) == 42:
        print(f'You have been attacked and killed by a malevolent {current_enemy}. Game over.')
        exit()

    if random.randint(0, 1000) == 42:
        print(f'You have been attacked and killed by a wild {sworn_enemy} which you were warned about at the '
              f'beginning, so you only have yourself to blame. Game over.')
        exit()


def check_if_game_won(objective_object, objective_location, current_location):
    if objective_object == current_location['object'] and objective_location == (f'{current_location["size"]} '
                                                                                 f'{current_location["type"]}'):
        print(f'Congratulations you have found the {objective_object}. You have completed the game')
        exit()


def display_current_location(current_location, inventory):
    if current_location['enemy_alive']:
        enemy_description = f'There is a harmless {current_location["enemy"]} hanging around.'
    else:
        enemy_description = (f'There is a dead {current_location["enemy"]} lying in a pool of its own blood, '
                             f'where you brutally and needlessly killed it to death in a senseless murder.')

    if current_location["object"]:
        object_description = (f'There is {an(current_location["object"])} lying nearby. This is not the object you are '
                              f'looking for.')
    else:
        object_description = f'There is nothing here worth picking up. You already have a pretty full knapsack anyway.'

    if len(inventory) > 0:
        knapsack_contents = f'Your knapsack contains {", ".join(inventory)}.'
    else:
        knapsack_contents = 'Your knapsack is empty. You should pick stuff up. It might come in handy in future.'

    if current_location['is_indoors']:
        print(f'You are in {an(current_location["size"])} {current_location["type"]} inside '
              f'{an(current_location["building_type"])}. {object_description} {enemy_description} {knapsack_contents}')
    else:
        print(f'You are in {an(current_location["size"])} {current_location["type"]}. {object_description} '
              f'{enemy_description} The weather is currently '
              f'{current_location["weather"]}. {knapsack_contents}')


def an(following_word):
    if following_word[0] in VOWELS:
        return f'an {following_word}'
    else:
        return f'a {following_word}'


def generate_location():
    new_location = {
        "is_indoors": random.randint(0, 1) == 1,
        "size": r(SIZES),
        "object": f'{r(ADJECTIVES)} {r(COLOURS)} {r(NOUNS)}',
        "enemy": f'{r(SIZES)} {r(ADJECTIVES)} {r(COLOURS)} {r(ENEMIES)}',
        "enemy_alive": True
    }

    if new_location["is_indoors"]:
        new_location["building_type"] = r(BUILDING_TYPES)
        new_location["type"] = r(INDOOR_LOCATION_TYPES)
    else:
        new_location["weather"] = r(WEATHER)
        new_location["type"] = r(OUTDOOR_LOCATION_TYPES)

    return new_location


def create_and_describe_options(current_location):
    for compass_direction in COMPASS_POINTS:
        if not current_location.get(compass_direction):
            current_location[compass_direction] = generate_location()
        describe_option(compass_direction, current_location)


def describe_option(compass_direction, location):
    if location[compass_direction]['is_indoors']:
        print(f'To the {compass_direction} there is {an(location[compass_direction]["building_type"])}.')
    else:
        print(f'To the {compass_direction} there is {an(location[compass_direction]["type"])}.')


def go_direction(direction, current_location):
    if direction.lstrip() == "":
        print("Go where?")
        return None
    elif direction == f'{chr(102)}{chr(117)}{chr(99)}{chr(107)} yourself':
        print("That's not very nice!!")
        return None
    elif direction not in COMPASS_POINTS:
        print(f"Don't know how to go {direction}. You can only go north, south, east or west")
        return None

    current_location[direction][OPPOSITE_DIRECTIONS[direction]] = current_location
    return current_location[direction]


def handle_input(current_location, inventory):
    new_location = None

    while not new_location:
        print()
        response = input('What do you want to do?  >>>> ')
        print()

        if response.lower().startswith('go'):
            direction = response.lower().replace("go", "").lstrip()
            new_location = go_direction(direction, current_location)
        elif response.lower().startswith('pick up'):
            item_to_pick_up = response.lower().replace("pick up", "").lstrip()
            if current_location["object"] is None:
                print("There's nothing here for you to pick up. You already picked up anything of any use.")
            elif item_to_pick_up.lstrip() == "":
                print("Pick up what?")
            elif item_to_pick_up == current_location["object"]:
                inventory.append(an(item_to_pick_up))
                current_location["object"] = None
                print(f'You have picked up the {item_to_pick_up} and put it in your knapsack for safekeeping.')
                new_location = current_location
            else:
                print(f'Tried to pick up the {item_to_pick_up} but the instructions were a bit vague. Did you mean '
                      f'to pick up the {current_location["object"]}?')
        elif response.lower() == f'attack {current_location["enemy"]}':
            attack_enemy(current_location)
            new_location = current_location
        elif response.lower() == 'attack':
            print("Attack what?")
        elif response.lower().startswith('attack'):
            print(f'Tried to attack {an(response.lower().replace("attack", "").lstrip())} but the instructions were a '
                  f'bit vague. Did you mean to attack the {current_location["enemy"]}?')
        elif response.lower() == 'quit':
            print("Thanks for playing. Goodbye")
            exit()
        else:
            print("I do not understand your instructions. Try something like 'go', 'attack' or 'pick up'")

    return new_location


def attack_enemy(current_location):
    if random.randint(0, 6) == 3:
        print(f'During your vicious attempted murder you were killed by the {current_location["enemy"]}, which you '
              f'needlessly provoked, so you only have yourself to blame. Game over.')
        exit()
    else:
        print(f'You have attacked and killed the {current_location["enemy"]} which was harmlessly minding its own '
              f'business, in an immoral violent murderous act of unforgivable wickedness.')
        current_location['enemy_alive'] = False


def main():
    current_location = generate_location()
    objective_object = f'{r(ADJECTIVES)} {r(COLOURS)} {r(NOUNS)}'
    objective_location = f'{r(SIZES)} {r(ALL_LOCATIONS)}'
    sworn_enemy = f'{r(SIZES)} {r(ADJECTIVES)} {r(COLOURS)} {r(ENEMIES)}'
    inventory = []

    print(f'Your name is {rt(CHARACTER_SUPERLATIVES)} {rt(NAMES)} the {rt(CLASSES)}, {rt(CHARACTER_ADVERBS)} '
          f'of {rt(CHARACTER_ENEMIES)}, and it is your mission to seek out the {objective_object}, '
          f'which can only be found in a {objective_location}. You must also evade the '
          f'{sworn_enemy}, which is your sworn deadly enemy and will attempt to kill you if it sees you.')

    while True:
        print()

        check_if_attacked(current_location["enemy"], sworn_enemy)
        check_if_game_won(objective_object, objective_location, current_location)
        display_current_location(current_location, inventory)

        print()

        create_and_describe_options(current_location)
        current_location = handle_input(current_location, inventory)


if __name__ == "__main__":
    main()
