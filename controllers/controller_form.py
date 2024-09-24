import re
from views.view_form import ViewForm
from models.player import Player
from models.tournament import Tournament


class ControllerForm:
    def __init__(self, stdscr, element):
        self.element = element
        self.form_view = ViewForm(stdscr, element)

    def start(self):
        self.form_view.initialize()
        error_msg = ""
        while True:
            action = self.form_view.start_view(error_msg)
            if action == 'BACK':
                return None
            elif 'VALIDATE' in action:
                answer = self.try_to_create_element(action[1], action[2])
                error_msg = self.handle_answer(answer)
                if not error_msg:
                    return self.element

    def try_to_create_element(self, element, data):
        if element == 'NEW_PLAYER':
            return self.try_to_create_new_player(data)
        elif element == 'NEW_TOURNAMENT':
            return self.try_to_create_tournament(data)

    @staticmethod
    def reformat_date(date_string):
        date_list = re.findall(r'\d+', date_string)
        for idx, number in enumerate(date_list):
            if len(number) < 2:
                date_list[idx] = '0' + number
        return '-'.join(date_list)

    def try_to_create_new_player(self, data):
        if len(data) != 4:
            return 'ERROR', 'INCOMPLETE'

        chess_id = data[3]
        if len(chess_id) != 7:
            return 'ERROR', 'CHESS_ID'

        date = self.reformat_date(data[2])
        if len(date) != 10:
            return 'ERROR', 'DATE'

        new_player = Player(first_name=data[0],
                            last_name=data[1],
                            date_of_birth=date,
                            chess_id=chess_id)
        new_player.save_to_database()

    def try_to_create_tournament(self, data):
        date_start = self.reformat_date(data[2])
        if len(date_start) != 10:
            return 'ERROR', 'DATE'

        date_end = self.reformat_date(data[3])
        if len(date_end) != 10:
            return 'ERROR', 'DATE'

        new_tournament = Tournament(
            name=data[0],
            place=data[1],
            date_start=date_start,
            date_end=date_end,
            description=data[5],
            rounds_number=int(data[4])
        )
        new_tournament.save_to_database()

    @staticmethod
    def handle_answer(answer):
        if answer:
            if 'INCOMPLETE' in answer:
                return 'Form is incomplete'
            elif 'CHESS_ID' in answer:
                return 'Invalid Chess ID must follow : AA00000'
            elif 'DATE' in answer:
                return 'Date is invalid'
        else:
            return ''
