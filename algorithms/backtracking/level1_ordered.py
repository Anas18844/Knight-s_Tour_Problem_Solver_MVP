from typing import List, Tuple
from .level0_random import RandomKnightWalk
# هنا احنا بنورث كل المتغيرات و كل الدوال من ال Class السابق بتاع ال Random Walk
class OrderedKnightWalk(RandomKnightWalk):
    def __init__(self, n: int, level: int = 1):
        super().__init__(n=n, level=level)
# هنا هو عمل override على داله اختيار الحركه و خلاه يختبار دايما اول واحده هتظهر امامه
# بدل اما كان بيستخدم random.suffle() عشان يطبق العشوائية
    def select_move(self, valid_moves: List[Tuple[int, int]]) -> Tuple[int, int]:
        return valid_moves[0]

# الداله الي عكسها في ال Random Walk
"""
# يخلط القايمة ويختار أول حاجة — ده بيخلي السلوك عشوائي.
    def select_move(self, valid_moves: List[Tuple[int, int]]) -> Tuple[int, int]:
        random.shuffle(valid_moves)
        return valid_moves[0]
"""


# التغيير الوحيد في هذا ال class هو فقط تغيير داله الاختيار لتختار اول حركه valid بدل العشوائية