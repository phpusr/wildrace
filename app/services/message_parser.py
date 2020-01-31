from typing import List


def debug(message):
    if True:
        print(message)


class MessageParser:
    EXP_DIGIT = r'\d'
    """Digit RegEx"""

    EXP_SPLIT = ' '
    """Split expression"""

    EXP_PLUS = '+'
    """Plus expression"""

    EXP_EQUAL = '='
    """Equal expression"""

    _current_symbol = ''
    """Current analyzing symbol"""

    _current_index = -1
    """Current analyzing symbol index"""

    _current_number: str = None
    """Current number which forming by symbols"""

    _start_sum_number: int = None
    """Start distance sum of runnings"""

    _distance_list: List[int] = []

    _end_sum_number: int = None

    _is_end_parsing = False

    def __init__(self, message: str):
        self.message = message

    def run(self):
        pass
