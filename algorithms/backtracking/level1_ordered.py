from typing import List, Tuple
from .level0_random import RandomKnightWalk

class OrderedKnightWalk(RandomKnightWalk):
    def __init__(self, n: int, level: int = 1):
        super().__init__(n=n, level=level)

    def select_move(self, valid_moves: List[Tuple[int, int]]) -> Tuple[int, int]:
        return valid_moves[0]
