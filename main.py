import pygame, os

WORKING_DIR = os.path.dirname(os.path.abspath(__file__)) 

class GapBuffor:
    def __init__(self):
        self.gap_size = 16
        self.buffor = [''] * self.gap_size
        self.current_gap_size = self.gap_size
        self.cursor = 0
    
    def write(self, text: str):
        for ch in text:
            self.buffor[self.cursor] = ch
            self.cursor += 1
            self.current_gap_size -= 1

            if self.current_gap_size <= 0:
                last_index = len(self.buffor) - 1
                self.current_gap_size = self.gap_size
                self.buffor += [''] * self.gap_size
                for i in range((last_index + 1) - self.cursor):
                    self.buffor[last_index - i], self.buffor[last_index + self.gap_size - i] = self.buffor[last_index + self.gap_size - i], self.buffor[last_index - i]

    def move_cursor(self, x: int):
        if x == 0: return
        elif x > 0:
            missed_space = self.cursor + self.current_gap_size + x - len(self.buffor)
            if missed_space > 0:
                self.buffor.extend(missed_space * [''])
            start = self.cursor
            end = self.cursor + self.current_gap_size
            for _ in range(x):
                self.buffor[start] = self.buffor[end]
                self.buffor[end] = ''
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
                self.buffor[start] = ''
                start -= 1
                end -= 1

    def delete(self, amount: int):
        if amount > 0:
            self.buffor = self.buffor[:max(self.cursor - amount, 0)] + self.buffor[self.cursor:]
            self.cursor -= amount
            if self.cursor < 0: self.cursor = 0
                
    def get_char(self, index: int):
        return self.buffor[index]

    def print(self):
        for i, ch in enumerate(self.buffor):
            if i == self.cursor:
                print('>', end='')
            if ch is not None:
                print(ch, end='')
        print()

class Terminal:
    def __init__(self):
        self.width = 500
        self.height = 500
        self.cell_size = 20
        self.cells_width = self.width // self.cell_size
        self.cells_height = self.height // self.cell_size
        self.buffor = GapBuffor()
        self.start()

    def start(self):
        pygame.init()
        window = pygame.display.set_mode((self.width, self.height))
        font = pygame.font.Font(os.path.join(WORKING_DIR, 'font/RobotoMono-Regular.ttf'), 20)
        run = True
        while run:
            for e in pygame.event.get():
                if e.type == pygame.QUIT: 
                    run = False
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_RIGHT: 
                        self.buffor.move_cursor(1)
                    elif e.key == pygame.K_LEFT: 
                        self.buffor.move_cursor(-1)
                    elif e.key == pygame.K_BACKSPACE: 
                        self.buffor.delete(1)
                    else:
                        self.buffor.write(e.unicode)


            window.fill((0, 0, 0))
            stop_draw = False
            for y in range(0, self.cells_height):
                for x in range(0, self.cells_width):
                    buffor_index = y * self.cells_height + x
                    try:
                        char = self.buffor.get_char(buffor_index)
                    except IndexError:
                        stop_draw = True
                        break

                    pos = [x * self.cell_size, y * self.cell_size]
                    pygame.draw.rect(window, (100, 100, 100), pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size), 1)
                    surface = font.render(char, True, (255, 255, 255))
                    surface = pygame.transform.scale(surface, (int(surface.get_rect().width * (9/10)), self.cell_size))
                    window.blit(surface, surface.get_rect(center=(pos[0] + self.cell_size//2, pos[1] + self.cell_size//2)))
                    
                    if buffor_index in range(self.buffor.cursor, self.buffor.cursor + self.buffor.current_gap_size):
                        pygame.draw.line(window, (0, 0, 255), 
                            (x * self.cell_size, y * self.cell_size + self.cell_size - 1), 
                            ((x + 1) * self.cell_size, y * self.cell_size + self.cell_size - 1))
                    if buffor_index == self.buffor.cursor:
                        pygame.draw.line(window, (255, 0, 0), 
                            (x * self.cell_size, y * self.cell_size + self.cell_size - 1), 
                            ((x + 1) * self.cell_size, y * self.cell_size + self.cell_size - 1))
                if stop_draw:
                    break
            pygame.display.flip()

terminal = Terminal()