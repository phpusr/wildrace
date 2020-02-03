import re
from dataclasses import dataclass
from typing import List

SUM_REGEX = r'(((\d+)\s*\+\s*)+)(\d+)\s*=\s*(\d+)'
TERM_REGEX = r'\d+'


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


def parse(message: str):
    sum_regex_res = re.search(SUM_REGEX, message)
    if sum_regex_res is None:
        return None

    terms = re.findall(TERM_REGEX, sum_regex_res.group(1))

    distance_list = [int(x) for x in terms[1::]]
    distance_list.append(int(sum_regex_res.group(4)))

    return MessageParserOut(
        start_sum_number=int(terms[0]),
        distance_list=distance_list,
        end_sum_number=int(sum_regex_res.group(5))
    )
