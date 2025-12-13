import random
from typing import List, Tuple
#  الكلاس ده فكرته هي اننا نعمل لاعب بيلعب بطريقه عشوائية و يجرب لحد اما يتزنق
# الهدف منه اننا نعرف ازاي الحصان بيتصرف على البورد و يكون القاعده الاساسية الي هنبني عليها
# ال Classes الي بعده 
class RandomKnightWalk:
    
    # هنا احنا بنعرف كل الحركات المسموحه للحصان انه يتحرك فيها
    # فبنجمع او بنطرح من الازواج ده و بعدها اشوف النقطه الي هتطلع جديده ده هتكون valid و الا لا ؟
    
    KNIGHT_MOVES = [(-2, -1),(-2, 1),(-1, -2),(-1, 2),(1, -2),(1, 2),(2, -1),(2, 1)]
    
# هنا انا بعرف ال Constructor بتاع ال class 
# بيعمل تهيئة لل board و يشوف حجمها و حدودها و يعرف المتغيرات الي هتساعدنا على تحليل تحركاته

    def __init__(self, n: int, level: int = 0):
        self.n = n  # ده عبارة عن حجم اللوح الي بيكون n*n 
        self.level = level  # متغير بيحدد ينا المستوى الحالي الي بنستخدمه 
        self.board: List[List[int]] = [[-1 for _ in range(n)] for _ in range(n)] # ليسته من اليستات بنخزن فيها رقم الخطوة لكل خانة، و-1 معناها مش مزارة.
        self.path: List[Tuple[int, int]] = [] # ده الي احنا بنخزن فيه ال path الي حصان مشي فيه فقط
        self.total_moves = 0 # متغير بيحسب عدد الحركات الكلية
        self.dead_ends_hit = 0 # متغير بيحسب عدد النهايات المقفولة الي وصلنا ليها 

# دالة بستخدمها عشان اعرف ازاي كانت الخطوة الي جايه الي هعملها داخل حدود ال board و الا لا 
    def is_valid_position(self, x: int, y: int) -> bool:
        return 0 <= x < self.n and 0 <= y < self.n
    #تبص لو الخانة دي مزارة قبل كده ولا لأ
    def is_unvisited(self, x: int, y: int) -> bool:
        return self.board[x][y] == -1
# ترجع لك قائمة الحركات الصالحة من المربع الحالي (داخل البورد ومش مزارة).
    def get_valid_moves(self, x: int, y: int) -> List[Tuple[int, int]]:
        valid_moves = [] #8 to 1 -> if 0 "dead end"
        for dx, dy in self.KNIGHT_MOVES:
            next_x, next_y = x + dx, y + dy
            if self.is_valid_position(next_x, next_y) and self.is_unvisited(next_x, next_y):
                valid_moves.append((next_x, next_y))
        return valid_moves
# يخلط القايمة ويختار أول حاجة — ده بيخلي السلوك عشوائي.
    def select_move(self, valid_moves: List[Tuple[int, int]]) -> Tuple[int, int]:
        random.shuffle(valid_moves)
        return valid_moves[0]
# الداله مهمه
# بياخد ال start position الي انت بدأت منه
    def random_walk(self, start_x: int, start_y: int) -> bool:
        current_x, current_y = start_x, start_y
        # يحط رقم 0 للخطوة الي هيبدأ منها و يبدأ يضيف على نفس المتغير ده كل ما يتحرك
        move_number = 0
        self.board[current_x][current_y] = move_number
        self.path.append((current_x, current_y))  # يضيفها عنده في بدايه قائمة ال path 
        self.total_moves += 1 
        target_moves = self.n * self.n # يبدأ يحط ال target الي هو عايز يوصل ليه وهو n *n 
# هنبدأ بقه هنا نكرر بعض الخطوات بشكل مكرر 
# اولا هنحط شرط ان لو عدد الخطوات بتاعي وصل لل target يقف
        while move_number < target_moves - 1:
            # هشوف اذا كان فيه حركات Valid و الا لا في الخطوة الي جايه
            valid_moves = self.get_valid_moves(current_x, current_y)
            if not valid_moves: 
                self.dead_ends_hit += 1 # لو لا رجع false و اقف وزود نقاط ال dead_ends
                return False
            # لو اه غير ال current position بتاعك لل position الجديد
            # زود ال path بالنقطه الجديده و كمان زود ال move_number و غير موقعك على ال Board بالمكان الجديد و رجع true
            next_x, next_y = self.select_move(valid_moves)
            current_x, current_y = next_x, next_y
            move_number += 1
            self.board[current_x][current_y] = move_number
            self.path.append((current_x, current_y))
            self.total_moves += 1
        return True
# ده الي بتعمل reset لل board في كل مره بتنادي على ال Algorithm 
# بترجعلك false لو مفيش اي حلول من الموقع الحالي الي هو ال start
# او true بان الحل خلص و يرجعلك نسخه كامله من المسار
    def solve(self, start_x: int, start_y: int) -> Tuple[bool, List[Tuple[int, int]]]:
        self.board = [[-1 for _ in range(self.n)] for _ in range(self.n)]
        self.path = []
        self.total_moves = 0
        self.dead_ends_hit = 0
        if not self.is_valid_position(start_x, start_y):
            return False, []
        success = self.random_walk(start_x, start_y)
        return success, self.path.copy()
# ده بترجعلك كل المتغيرات الي هنستخدمها في التحليل
    def get_stats(self) -> dict:
        return {
            'total_moves': self.total_moves,
            'dead_ends_hit': self.dead_ends_hit,
            'coverage_percent': 100 * len(self.path) / (self.n * self.n) if self.n > 0 else 0,
            'board_size': self.n
        }
