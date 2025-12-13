import time
from typing import List, Tuple
from .level1_ordered import OrderedKnightWalk

# احنا هنورث كل شيء عادي من level 1 و level 0  عشان ال ordered deterministic moves بس هنضيف معاهم خوارزمية بحث
class PureBacktracking(OrderedKnightWalk):
# خد بالك اننا هنضطر نعدل في غالب ال Functions عندنا عشان بس ضيف متغيرين جداد في ال constractor
    def __init__(self, n: int, level: int = 2):
        super().__init__(n=n, level=level)
        self.backtrack_count = 0
        self.recursive_calls = 0
# هنا خوارزمية solve() هي نفس الخوارزميه الي في level 0,1 
# برضه هي المسؤوله عن عمل reset لل Board بس الاختلاف اننا كمان هنعمل reset للمتغيرات الجديده
    def solve(self, start_x: int, start_y: int) -> Tuple[bool, List[Tuple[int, int]]]:
        self.board = [[-1 for _ in range(self.n)] for _ in range(self.n)]
        self.path = []
        self.total_moves = 0
        self.dead_ends_hit = 0
        self.backtrack_count = 0
        self.recursive_calls = 0

        if not self.is_valid_position(start_x, start_y):
            return False, []

        success = self._backtrack(start_x, start_y, 0)
        return success, self.path.copy()
# اهم داله عندنا
#داله ال backtrack الي ال class ده مبني عشانها
    def _backtrack(self, x: int, y: int, move_count: int) -> bool:
        self.recursive_calls += 1 # هنا ده عداد يشوف انا هدخل ال DFS كام مره

        self.board[x][y] = move_count # هنا بيقول للمربع انت اتزرت خلاص
        self.path.append((x, y)) # وهنا انا بضيف النقطه داخل المسار الي انا ماشي عليه

        if move_count == self.n * self.n - 1:  #لو وصلت اني اقفل كل البورد رجع true
            return True

        valid_moves = self.get_valid_moves(x, y)  # ده الداله الي بترجعلي كل ال moves الصالحه

        for next_x, next_y in valid_moves:
            if self._backtrack(next_x, next_y, move_count + 1):  # ده الداله الي بتطبق ال DFS مسؤولة انها تعدي على المربعات ال valid 
                # هنا ده ال recursive calls الي احنا شغالين عليه ال Backtracking
                return True
# طب افرض وصلنا لوحده مش valid ؟
# عادي جدا هعمل backtrack و ارجع القيم تاني -1 بتاعت الرقعات الي انا مشيت عليها و انا بجرب
# و اشيل النقاط الي انا مشيت عليها من ال path
# وازود ال backtrack counter بواحد

# ده ال stack يا اخونااااا
        self.backtrack_count += 1 #return back
        self.board[x][y] = -1 # unvisited
        self.path.pop() 
        return False
