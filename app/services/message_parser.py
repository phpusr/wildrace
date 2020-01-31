import inspect
import re
from dataclasses import dataclass
from typing import List

DEBUG = False

EXP_DIGIT = r'\d'
"""Digit RegEx"""

EXP_SPLIT = ' '
"""Split expression"""

EXP_PLUS = '+'
"""Plus expression"""

EXP_EQUAL = '='
"""Equal expression"""


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
        self.debug('run')

        self._reset()

        is_not_last_symbol = self._next_symbol()

        while is_not_last_symbol and not self._is_end_parsing:
            is_digit_symbol = re.match(EXP_DIGIT, self._current_symbol)

            if is_digit_symbol:
                self._current_number = ''
                self._step_digit()
            else:
                is_not_last_symbol = self._next_symbol()

        if self._is_end_parsing:
            return MessageParserOut(self._start_sum_number, self._distance_list, self._end_sum_number)

    def debug(self, message: str = None):
        if not DEBUG:
            return

        if message:
            print(message)
        else:
            parent_fun_name = inspect.currentframe().f_back.f_code.co_name
            print(f'"{self._current_symbol}" -> {parent_fun_name}')

    def _reset(self):
        """Reset state machine"""
        self.debug()

        self._start_sum_number = None
        self._distance_list = []
        self._end_sum_number = None

    def _next_symbol(self) -> bool:
        """Give next message symbol to current_symbol var"""

        if self._current_index + 1 == len(self.message):
            self._current_symbol = ''
            result = False
        else:
            self._current_index += 1
            self._current_symbol = self.message[self._current_index]
            result = True

        self.debug(f'  - next_symbol: "{self._current_symbol}"')

        return result

    def _step_digit(self):
        """Number processing"""
        self.debug()

        self._current_number += self._current_symbol

        self._next_symbol()
        if re.match(EXP_DIGIT, self._current_symbol):
            self._step_digit()
        elif self._current_symbol == EXP_SPLIT:
            self._step_space_after_digit()
        elif self._current_symbol == EXP_PLUS:
            self._step_plus()
        elif self._current_symbol == EXP_EQUAL:
            self._step_equal()
        else:
            self._reset()

    def _step_space_after_digit(self):
        """Space after number processing"""
        self.debug()

        self._next_symbol()
        if self._current_symbol == EXP_SPLIT:
            self._step_space_after_digit()
        elif self._current_symbol == EXP_PLUS:
            self._step_plus()
        elif self._current_symbol == EXP_EQUAL:
            self._step_equal()
        else:
            self._reset()

    def _step_plus(self):
        """Plus sign processing"""
        self.debug()

        if self._start_sum_number is None:
            self._start_sum_number = int(self._current_number)
        else:
            self._distance_list.append(int(self._current_number))

        self.debug(f'  - current number: "{self._current_number}"')
        self._current_number = ''

        self._next_symbol()
        if re.match(EXP_DIGIT, self._current_symbol):
            self._step_digit()
        elif self._current_symbol == EXP_SPLIT:
            self._step_space_after_plus()
        else:
            self._reset()

    def _step_space_after_plus(self):
        """Space sing after plus sing processing"""
        self.debug()

        self._next_symbol()
        if re.match(EXP_DIGIT, self._current_symbol):
            self._step_digit()
        elif self._current_symbol == EXP_SPLIT:
            self._step_space_after_plus()
        else:
            self._reset()

    def _step_equal(self):
        """Equal sign processing"""
        self.debug()

        if self._start_sum_number is None:
            self._reset()
            return

        self._distance_list.append(int(self._current_number))
        self.debug(f'  - current number: "{self._current_number}"')
        self._current_number = ''

        self._next_symbol()
        if re.match(EXP_DIGIT, self._current_symbol):
            self._step_digit_after_equal()
        elif self._current_symbol == EXP_SPLIT:
            self._step_space_after_equal()
        else:
            self._reset()

    def _step_digit_after_equal(self):
        """Processing digit after equal sign """
        self.debug()

        self._current_number += self._current_symbol

        self._next_symbol()
        if re.match(EXP_DIGIT, self._current_symbol):
            self._step_digit_after_equal()
        else:
            self._finish()

    def _step_space_after_equal(self):
        """Processing space sign after equal sign"""
        self.debug()

        self._next_symbol()
        if re.match(EXP_DIGIT, self._current_symbol):
            self._step_digit_after_equal()
        elif self._current_symbol == EXP_SPLIT:
            self._step_space_after_equal()
        else:
            self._reset()

    def _finish(self):
        """Expression processing finish"""
        self.debug()

        self._is_end_parsing = True
        self._end_sum_number = int(self._current_number)

        self.debug(f'start_sum_number: {self._start_sum_number}')
        self.debug(f'distance_list: {self._distance_list}')
        self.debug(f'end_sum_number: {self._end_sum_number}')
