from enum import Enum

class CellType(Enum):
    GAP = 1
    ENDFILE = 2

class GapBuffor:
    def __init__(self):
        self.gap_size = 16
        self.buffor = [CellType.GAP] * self.gap_size
        self.current_gap_size = self.gap_size
        self.cursor = 0
    
    def write(self, text: str) -> None:
        for ch in text:
            self.buffor[self.cursor] = ch
            self.cursor += 1
            self.current_gap_size -= 1

            if self.current_gap_size <= 0:
                last_index = len(self.buffor) - 1
                self.current_gap_size = self.gap_size
                self.buffor += [CellType.GAP] * self.gap_size
                for i in range((last_index + 1) - self.cursor):
                    self.buffor[last_index - i], self.buffor[last_index + self.gap_size - i] = self.buffor[last_index + self.gap_size - i], self.buffor[last_index - i]

    def move_cursor(self, x: int) -> None:
        if x == 0: return
        elif x > 0:
            missed_space = self.cursor + self.current_gap_size + x - len(self.buffor)
            if missed_space > 0:
                return
            start = self.cursor
            end = self.cursor + self.current_gap_size
            for _ in range(x):
                self.buffor[start] = self.buffor[end]
                self.buffor[end] = CellType.GAP
                start += 1
                end += 1
            self.cursor += x
        else:
            start = self.cursor - 1
            end = self.cursor + self.current_gap_size - 1
            for _ in range(-x):
                if self.cursor <= 0:
                    break
                self.cursor -= 1
                self.buffor[end] = self.buffor[start]
                self.buffor[start] = CellType.GAP
                start -= 1
                end -= 1

    def delete(self, amount: int) -> None:
        if amount > 0:
            self.buffor = self.buffor[:max(self.cursor - amount, 0)] + self.buffor[self.cursor:]
            self.cursor -= amount
            if self.cursor < 0: self.cursor = 0
                
    def get_char(self, index: int) -> None:
        if index == len(self.buffor):
            return CellType.ENDFILE
        return self.buffor[index]

    def clear(self) -> None:
        self.buffor.clear()
        self.buffor = [CellType.GAP] * self.gap_size
        self.current_gap_size = self.gap_size
        self.cursor = 0

    def load(self, data: str) -> None:
        self.clear()
        self.buffor += list(data)

    def get_text(self) -> str:
        res = ''
        for cell in self.buffor:
            if type(cell) == str:
                res += cell
        return res