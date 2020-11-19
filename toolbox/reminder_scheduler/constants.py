"""
Derived from:
https://collaborate2.ons.gov.uk/confluence/display/SDC/RMC-293+-+Print+reminder+letters+and+questionnaires
https://collaborate2.ons.gov.uk/confluence/display/SDC/RM+Census+Initial+Contact+Run+Book+-+2021
"""

ACTION_TYPES_FOR_WAVE = {
    1: ['P_RL_1RL1_1', 'P_RL_1RL2B_1'],
    2: ['P_RL_2RL1', 'P_RL_2RL2B']
}

WAVE_CLASSIFIERS = {
    1: "treatment_code IN ('HH_LP1E', 'HH_LP1W', 'HH_LP2E', 'HH_LP2W') AND survey_launched = 'f'",

    2: "treatment_code IN ('HH_LP1E', 'HH_LP1W', 'HH_LP2E', 'HH_LP2W') AND survey_launched = 'f'"
}

ACTION_TYPE_CLASSIFIERS = {
    'P_RL_1RL1_1': "treatment_code IN ('HH_LP1E', 'HH_LP2E') AND survey_launched = 'f'",

    'P_RL_1RL2B_1': "treatment_code IN ('HH_LP1W', 'HH_LP2W') AND survey_launched = 'f'",

    'P_RL_2RL1': "treatment_code IN ('HH_LP1E', 'HH_LP2E') AND survey_launched = 'f'",

    'P_RL_2RL2B': "treatment_code IN ('HH_LP1W', 'HH_LP2W') AND survey_launched = 'f'"
}


ACTION_TYPES_FOR_RESPONSE_DRIVEN_REMINDER = [
    'P_RD_RNP41',
    'P_RD_RNP42B',
    'P_RD_RNP51',
    'P_RD_RNP52B',
]
