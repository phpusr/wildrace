import re
from dataclasses import dataclass
from typing import List

EXP_DIGIT = r'\d'
"""Digit RegEx"""

EXP_SPLIT = ' '
"""Split expression"""

EXP_PLUS = '+'
"""Plus expression"""

EXP_EQUAL = '='
"""Equal expression"""


def debug(message):
    if True:
        print(message)


@dataclass
class MessageParserOut:
    start_sum_number: int
    """Start sum of running distances"""

    distance_list: List[int]
    """List of running distances"""

    end_sum_number: int
    """Finish sum of running distances"""

    @property
    def distance(self):
        return sum(self.distance_list)


class MessageParser:

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

    def run(self) -> MessageParserOut:
        debug('>> run')

        self._reset()

        is_not_last_symbol = self._next_symbol()

        while is_not_last_symbol and not self._is_end_parsing:
            debug(f'start: {self._current_symbol}')

            is_digit_symbol = re.match(EXP_DIGIT, self._current_symbol)

            if is_digit_symbol:
                self._current_number = ''
                self._step_1()
            else:
                is_not_last_symbol = self._next_symbol()

        if self._is_end_parsing:
            return MessageParserOut(self._start_sum_number, self._distance_list, self._end_sum_number)

    def _reset(self):
        """Reset state machine"""
        debug(f'reset: {self._current_symbol}')

        self._start_sum_number = None
        self._distance_list = []
        self._end_sum_number = None

    def _next_symbol(self) -> bool:
        """Give next message symbol to current_symbol var"""
        debug('  - next_symbol')

        if self._current_index + 1 == len(self.message):
            self._current_symbol = ''
            return False

        self._current_index += 1
        self._current_symbol = self.message[self._current_index]
        return True

    def _step_1(self):
        """Number processing"""
        debug(f'step_1: {self._current_symbol}')

        self._current_number += self._current_symbol

        self._next_symbol()
        if re.match(EXP_DIGIT, self._current_symbol):
            self._step_1()
        elif self._current_symbol == EXP_SPLIT:
            self._step_2()
        elif self._current_symbol == EXP_PLUS:
            self._step_3()
        elif self._current_symbol == EXP_EQUAL:
            self._step_4()
        else:
            self._reset()

    def _step_2(self):
        """Space after number processing"""
        debug(f'step_2: {self._current_symbol}')

        self._next_symbol()
        if self._current_symbol == EXP_SPLIT:
            self._step_2()
        elif self._current_symbol == EXP_PLUS:
            self._step_3()
        elif self._current_symbol == EXP_EQUAL:
            self._step_4()
        else:
            self._reset()

    def _step_3(self):
        """Plus sign processing"""
        debug(f'step_3: {self._current_symbol}')

        if self._start_sum_number is None:
            self._start_sum_number = int(self._current_number)
        else:
            self._distance_list.append(int(self._current_number))

        self._current_number = ''

        self._next_symbol()
        if re.match(EXP_DIGIT, self._current_symbol):
            self._step_1()
        elif self._current_symbol == EXP_SPLIT:
            self._step_2_2()
        else:
            self._reset()

    def _step_2_2(self):
        """Space sing after plus sing processing"""
        debug(f'step_2_2: {self._current_symbol}')

        self._next_symbol()
        if re.match(EXP_DIGIT, self._current_symbol):
            self._step_1()
        elif self._current_symbol == EXP_SPLIT:
            self._step_2_2()
        else:
            self._reset()

    def _step_4(self):
        """Equal sign processing"""
        debug(f'step_4: {self._current_symbol}')

        if self._start_sum_number is None:
            self._reset()
            return

        self._distance_list.append(int(self._current_number))
        self._current_number = ''

        self._next_symbol()
        if re.match(EXP_DIGIT, self._current_symbol):
            self._step_5()
        elif self._current_symbol == EXP_SPLIT:
            self._step_6()
        else:
            self._reset()

    def _step_5(self):
        """Processing space sign after equal sign """
        debug(f'step_5: {self._current_number}')

        self._current_number += self._current_symbol

        self._next_symbol()
        if re.match(EXP_DIGIT, self._current_symbol):
            self._step_5()
        else:
            self._finish()

    def _step_6(self):
        """Processing number after equal sign"""
        debug(f'step_6: {self._current_symbol}')

        self._next_symbol()
        if re.match(EXP_DIGIT, self._current_symbol):
            self._step_5()
        elif self._current_symbol == EXP_SPLIT:
            self._step_6()
        else:
            self._reset()

    def _finish(self):
        """Expression processing finish"""
        debug(f'finish: {self._current_number}')

        self._is_end_parsing = True
        self._end_sum_number = int(self._current_number)

        debug(f'start_sum_number: {self._start_sum_number}')
        debug(f'distance_list: {self._distance_list}')
        debug(f'end_sum_number: {self._end_sum_number}')
