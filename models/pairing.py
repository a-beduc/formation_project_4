import random
import copy
from typing import List, Set, Tuple, Dict


class Pairing:
    """
    This class is used to handle the pairing of players for every round of a
    tournament.
    It uses the circle method found in the wikipedia page of
    Round-robin_Tournament
    url : https://en.wikipedia.org/wiki/Round-robin_tournament
    Two priorities arise:
        1 - No repeat of a pairing
        2 - Try to pitch the players with better scores against each others
    """
    def __init__(self,
                 list_of_players: List[str],
                 new_pairing: bool = True):
        """
        Initialize a new instance of Pairing
        :param list_of_players: ['p_1', 'p_2', 'p_4' ...]
        :param new_pairing: If True, it will randomize the first round.
        For a reload, it must be False because, the 'initial configuration'
        will be used as a reference to recreate the others configurations.
        """
        self.list_of_players = list_of_players
        self.possibles_configurations: List[Set[Tuple[str, str]]] = []
        self.played_matches: Set[Tuple[str, str]] = set()
        if new_pairing:
            self.initial_configuration = self.randomize_players()
            self.generate_circle_configurations()

    @staticmethod
    def get_player_number(player_id):
        return int(player_id.split('_')[1])

    def randomize_players(self) -> Tuple[str, ...]:
        shuffled_list = self.list_of_players.copy()
        random.shuffle(shuffled_list)
        return tuple(shuffled_list)

    @staticmethod
    def rearrange_list(old_list: List[str]) -> List[str]:
        """
        This method will create the next circle configuration from the current
        configuration.
        It will move the position as it's explained here:
        https://en.wikipedia.org/wiki/Round-robin_tournament
        :return new_list: a list where the position are modified
        [i[0], i[-1], i[1], i[2] ... i[-2]]
        """
        new_list = [old_list[0], old_list[-1]]
        new_list.extend(old_list[1:-1])
        return new_list

    def generate_pairing(self, list_configuration: List[str]) -> (
            Set)[Tuple[str, str]]:
        """
        Generate every configuration possible when doing a full circle from
        the initial position.
        From a list [1, 5, 3, 4, 2, 6]
        it will return {(1, 6), (2, 5), (3, 4)}

        :param list_configuration: The list_configuration must have an even
        number of players

        :return set_configuration: Set[Tuple[str, str]]
        """
        set_configuration = set()
        for i in range(int(len(list_configuration) / 2)):
            pair = [list_configuration[i], list_configuration[-i-1]]
            pair = tuple(sorted(pair, key=self.get_player_number))
            set_configuration.add(pair)
        return set_configuration

    def generate_circle_configurations(self):
        """
        Generate every possibles configurations from an initial list
        It creates a list of set of tuples.
        """
        current_configuration = list(copy.deepcopy(self.initial_configuration))
        i = 1
        while i < len(self.initial_configuration):
            current_configuration = self.rearrange_list(current_configuration)
            current_set = self.generate_pairing(current_configuration)
            self.possibles_configurations.append(current_set)
            i += 1

    def add_to_memory(self, round_matches: Set[Tuple[str, str]]):
        """
        Add played match (tuple) to a Set that is used as memory.
        :param round_matches: ('p_1', 'p_2')
        """
        for match in round_matches:
            self.played_matches.add(match)

    def generate_first_round_configuration(self) -> Set[Tuple[str, str]]:
        """
        Generate the first configuration of pairs for the first round of a
        tournament
        (without taking score into account)

        :return matches: {('p_6', 'p_8'),('p_3', 'p_5'), ...}
        """
        matches = self.possibles_configurations.pop()
        self.add_to_memory(matches)
        return matches

    def generate_round_configuration_from_match(self, match: Tuple[str, str]) \
            -> Set[Tuple[str, str]]:
        """
        Search into the possibles configurations, the set of matches that
        contains the 'match'
        :param match: ('p_1', 'p_6')
        :return next_round_configuration: {('p_6', 'p_8'),('p_3', 'p_5'), ...}
        """
        for configuration in self.possibles_configurations:
            if match in configuration:
                next_round_configuration = configuration
                self.possibles_configurations.remove(configuration)
                self.add_to_memory(next_round_configuration)
                return next_round_configuration

    def try_to_generate_next_round(self, list_of_players: List[str]) -> (
            Set)[Tuple[str, str]]:
        """
        Test possibles match-up from a list of players and return a
        configuration if one of the match-up is possible

        :param list_of_players: ['p_3', 'p_6', 'p_2']

        :return next_round: {('p_6', 'p_8'),('p_3', 'p_5'), ...} The
        configuration for next round
        """
        for i in range(len(list_of_players)):
            for j in range(i+1, len(list_of_players)):
                match_test = [list_of_players[i], list_of_players[j]]
                match_test = tuple(sorted(match_test,
                                          key=self.get_player_number))
                if match_test not in self.played_matches:
                    next_round = self.generate_round_configuration_from_match(
                        match_test)
                    return next_round

    def generate_next_round_from_ranking(self,
                                         dict_ranking: Dict[str, List[str]]):
        """
        Use the actual ranking in a tournament to create the next matches.
        The Key represents the rank of the players and the value the list of
        Players with that rank.
        :param dict_ranking: {'1':['p_3'], '2':['p_1', 'p_4'], '3':...}
        :return result: {('p_1', 'p_3'),('p_4', 'p_5'), ...} The configuration
        for next round
        this method will always try to look for matches that haven't been
        played yet.
        """
        ranking_key = sorted(dict_ranking.keys(), key=int)
        accumulated_list = []
        result = None
        i = 0
        while i < len(ranking_key) and not result:
            accumulated_list.extend(dict_ranking[ranking_key[i]])
            result = self.try_to_generate_next_round(accumulated_list)
            i += 1
        return result

    @classmethod
    def instantiate_pairing(cls,
                            list_of_players: List[str],
                            initial_configuration: Tuple[str],
                            list_played_matches: List[Tuple[str, str]]):
        """
        Instantiate a Pairing object from the initial configuration of a list
        and remove the configurations that contains matches that already
        happened during the tournament.

        :param list_of_players: ['p_1', 'p_2', 'p_4', 'p_8']
        :param initial_configuration: (['p_4', 'p_2', 'p_1', 'p_8'])
        :param list_played_matches: [('p_1', 'p_4'), ('p_2', 'p_8')]
        :return instance: a Pairing Object
        """
        instance = cls(list_of_players=list_of_players,
                       new_pairing=False)
        instance.initial_configuration = initial_configuration
        instance.generate_circle_configurations()
        instance.played_matches.update(list_played_matches)
        instance.possibles_configurations = \
            [config for config in instance.possibles_configurations
             if not config & instance.played_matches]
        return instance
