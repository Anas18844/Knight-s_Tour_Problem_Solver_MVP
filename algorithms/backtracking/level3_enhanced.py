from typing import List, Tuple
from .level2_backtracking import PureBacktracking

# هنا احنا بناخد ال Pure Backtracking من المستوى اللي قبله
# وهنضيف عليه بس شوية تحسينات عشان يكون أذكى في البحث

class EnhancedBacktracking(PureBacktracking):

    def __init__(self, n: int, level: int = 3):
        super().__init__(n=n, level=level)
# الداله فكرتها انها بتشوف
# لو الحصان راح للرقعة ده 
# كام رقعه بعدها يمكن انه يتحرك ليها
# و طبعا كلما زاد العدد ، زاد احتماليه اني ميقعش في خانات مسدودة
#  و ده الي هنعتمد عليه ك heuristic 
    def _get_degree(self, x: int, y: int) -> int:
        count = 0
        for dx, dy in self.KNIGHT_MOVES:
            next_x, next_y = x + dx, y + dy
            if self.is_valid_position(next_x, next_y) and self.is_unvisited(next_x, next_y):
                count += 1
        return count
# هنا انا بتأكد ان المكان الي انا هروحه مش هيحبسني 
# ازاي يعني ؟؟
# عن طريق اني اشوف هل الخانه الي هروحها ده ليها جران سهل اني اروحهم و ارجع والا لا
# طب لو لا ، بغير حاله الخانه ده مؤقتا ل 999 عشان الدوال تشوف انها مقفولة
    def _has_isolated_neighbor(self, x: int, y: int) -> bool:
        temp_board_state = self.board[x][y]
        self.board[x][y] = 999
# هنا انا بعدي على كل جيران الخانه و اشوف هل اقدر اتحرك والا لا
        for dx, dy in self.KNIGHT_MOVES:
            nx, ny = x + dx, y + dy
            if self.is_valid_position(nx, ny) and self.is_unvisited(nx, ny):
                if self._get_degree(nx, ny) == 0:
                    self.board[x][y] = temp_board_state
                    return True
# ده بترجع البورد لحالته الاصلية عشان التغيير الي كنا عاملينه كان مؤقت
        self.board[x][y] = temp_board_state
        return False
# دول نفس دوال level 2 بالظبطمع شوية اضافات
    def _backtrack(self, x: int, y: int, move_count: int) -> bool:
        self.recursive_calls += 1

        self.board[x][y] = move_count
        self.path.append((x, y))

        if move_count == self.n * self.n - 1:
            return True

        valid_moves = self.get_valid_moves(x, y)
# هنا ده جزء كمان مهمه 
# هنا انا بشوف ايه المكان الي اروحه في اقل عدد اختيارات
# ده بيسهل على ال backtracking في الحل ، كل اما قللنا الخيرات الي قدامه ، فهنقلل ال time و ال space complixty
        moves_with_degree = []
        for next_x, next_y in valid_moves:
            degree = self._get_degree(next_x, next_y)
            moves_with_degree.append((next_x, next_y, degree))

        moves_with_degree.sort(key=lambda m: m[2])

        for next_x, next_y, _ in moves_with_degree:
            if self._backtrack(next_x, next_y, move_count + 1):
                return True
# وده ال Backtrack نفسه نفس ال level الي قبله
        self.backtrack_count += 1
        self.board[x][y] = -1
        self.path.pop()
        return False


#الخلاصه
#Level 2 : Backtracking pure

# بعتمد على تجربة كل احتمال بنفس الترتيب.

#Level 3 : Enhanced Backtracking

# بنزود عليه:

#Sorting moves by degree

#Avoiding isolated neighbors

#Pruning bad branches early
