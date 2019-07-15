import pygame
import os
import tkinter
from tkinter.filedialog import askopenfilename, asksaveasfile
from tkinter.messagebox import showinfo
from gapbuffer import GapBuffor, CellType
from typing import List, Optional


WORKING_DIR = os.path.dirname(os.path.abspath(__file__)) 

class TerminalButton():
    def __init__(self, text: str, pos: List[int], width: Optional[int]=None, height: Optional[int]=None):
        self.pos = pos 
        self.width = width
        self.height = height
        self.font = pygame.font.Font(os.path.join(WORKING_DIR, 'font/Roboto-Regular.ttf'), 16)
        self.text_surface = self.font.render(text, True, (255, 255, 255))
        
        if width == None:
            self.width = self.text_surface.get_rect().width
        if height == None:
            self.height = self.text_surface.get_rect().height
        self.rect = pygame.Rect(pos[0], pos[1], self.width, self.height)

        self.is_clicked = False
        self.clicked = False

        self.hover = False

    def catch_events(self, events: List[pygame.event.Event]) -> None:
        mouse = pygame.mouse.get_pos()
        self.hover = self.rect.collidepoint(mouse[0], mouse[1])
        self.clicked = False
        self.is_clicked = False
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if self.hover:
                    self.clicked = True
        if self.hover and pygame.mouse.get_pressed()[0]:
            self.is_clicked = True

    def click(self) -> bool:
        return self.clicked

    def draw(self, window) -> None:
        if self.is_clicked:
            pygame.draw.rect(window, (0, 200, 0), self.rect)
        else:
            pygame.draw.rect(window, (0, 150 if self.hover else 100, 0), self.rect)
        window.blit(self.text_surface, self.text_surface.get_rect(center=(self.pos[0] + self.width//2, self.pos[1] + self.height//2)))

class Terminal:
    def __init__(self):
        self.menu_height = 100
        self.width = 500
        self.height = 500 + self.menu_height
        self.cell_size = 20
        self.cells_width = self.width // self.cell_size
        self.cells_height = (self.height - self.menu_height) // self.cell_size
        self.buffor = GapBuffor()
        self.debug_mode = False
        self.start()

    def start(self) -> None:
        pygame.init()
        window = pygame.display.set_mode((self.width, self.height))
        font = pygame.font.Font(os.path.join(WORKING_DIR, 'font/RobotoMono-Regular.ttf'), 24)
        exit_button = TerminalButton('Exit', (0, 0), self.width/4, self.cell_size)
        load_button = TerminalButton('Load', (self.width * (1/4), 0), self.width/4, self.cell_size)
        save_button = TerminalButton('Save', (self.width * (2/4), 0), self.width/4, self.cell_size)
        debug_mode_button = TerminalButton('Debug Mode', (self.width * (3/4), 0), self.width/4, self.cell_size)
        tk = tkinter.Tk()
        tk.withdraw()
        clock = pygame.time.Clock()
        run = True
        while run:
            events = pygame.event.get()git push
            for e in events:
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

            exit_button.catch_events(events)
            load_button.catch_events(events)
            save_button.catch_events(events)
            debug_mode_button.catch_events(events)

            if exit_button.click():
                run = False
            if load_button.click():
                self.load_file()
            if save_button.click():
                self.save_file()
            if debug_mode_button.click():
                self.debug_mode = not self.debug_mode

            window.fill((0, 0, 0))
            stop_draw = False
            buffor_index = -1

            for y in range(0, self.cells_height):
                for x in range(0, self.cells_width):
                    pos = [x * self.cell_size, (y + 1) * self.cell_size]
                    new_line = False
                    try:
                        while True:
                            buffor_index += 1
                            char = self.buffor.get_char(buffor_index)

                            if self.buffor.cursor == buffor_index:
                                pygame.draw.line(window, (255, 255, 255), 
                                        (pos[0] + 1, pos[1] + 1), 
                                        (pos[0] + 1, pos[1] + self.cell_size - 1))

                            if self.debug_mode and char == CellType.GAP:
                                char = ''
                                break
                            if type(char) == str:
                                if ord(char) in [10, 13]: # eneter
                                    new_line = True
                                break
                    except IndexError:
                        stop_draw = True
                        break

                    if new_line:
                        break

                    surface = font.render(char, True, (255, 255, 255))
                    surface = pygame.transform.scale(surface, (int(surface.get_rect().width * (9/10)), self.cell_size))
                    window.blit(surface, surface.get_rect(center=(pos[0] + self.cell_size//2, pos[1] + self.cell_size//2)))

                    if self.debug_mode:
                        pygame.draw.rect(window, (100, 100, 100), pygame.Rect(pos[0], pos[1], self.cell_size, self.cell_size), 1)
                        if buffor_index in range(self.buffor.cursor, self.buffor.cursor + self.buffor.current_gap_size):
                            pygame.draw.line(window, (0, 0, 255), 
                                (pos[0], pos[1] + self.cell_size - 1), 
                                (pos[0] + self.cell_size, pos[1] + self.cell_size - 1))
                        if buffor_index == self.buffor.cursor:
                            pygame.draw.line(window, (255, 0, 0), 
                                (pos[0], pos[1] + self.cell_size - 1), 
                                (pos[0] + self.cell_size, pos[1] + self.cell_size - 1))
                if stop_draw:
                    break

            exit_button.draw(window)
            load_button.draw(window)
            save_button.draw(window)
            debug_mode_button.draw(window)
            pygame.display.flip()
            clock.tick_busy_loop(60)

    def load_file(self) -> bool:
        path = askopenfilename()
        if type(path) != str:
            return False
        try:
            with open(path) as file:
                try:
                    text = file.read()
                except UnicodeDecodeError:
                    showinfo('Error', f'Can\'t load {path}')
                    return
                self.buffor.load(text)
                return True
        except FileNotFoundError:
            return False
        return False
    
    def save_file(self) -> bool:
        file = asksaveasfile()
        if file == None:
            return False
        file.write(self.buffor.get_text())
        return True