import time
from time import sleep
from typing import Callable

import pygame
import pygame_widgets
import pygame_widgets.button
import pygame_widgets.textbox
from pygame_widgets.button import Button

YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREY = (200, 200, 200)

STORY1 = """FIRST LINE OF TEXT
second line of text
third line of text
** last line of text that fits
this line should force scroll up
and here again for
each line the follows"""

STORY2 = """No man is an island, 
Entire of itself, 
Every man is a piece of the continent, 
A part of the main.

If a clod be washed away by the sea,
Europe is the less.
As well as if a promontory were.
As well as if a manor of thy friend’s

Or of thine own were:
Any man’s death diminishes me,
Because I am involved in mankind,
And therefore never send to 
know for whom the bell tolls;
It tolls for thee.
  -- John Donne (Year 1624 AD)"""


class TextScroll:
    def __init__(self, area, font, fg_color, bk_color, text, ms_per_line=800):
        """object to display lines of text scrolled in with a delay between each line
        in font and fg_color with background o fk_color with in the area rect"""

        super().__init__()
        self.rect = area.copy()
        self.fg_color = fg_color
        self.bk_color = bk_color
        self.size = area.size
        self.surface = pygame.Surface(self.size, flags=pygame.SRCALPHA)
        self.surface.fill(bk_color)
        self.font = font
        self.lines = text.split("\n") if text else ""
        self.ms_per_line = ms_per_line
        self.y = 0
        self.y_delta = self.font.size("M")[1]
        self.next_time = None
        self.dirty = False

    def set_text(self, text: str):
        self.lines = text.split("\n")

    def _update_line(self, line):  # render next line if it's time
        if self.y + self.y_delta > self.size[1]:  # line does not fit in remaining space
            self.surface.blit(self.surface, (0, -self.y_delta))  # scroll up
            self.y += -self.y_delta  # backup a line
            pygame.draw.rect(self.surface, self.bk_color, (0, self.y, self.size[0], self.size[1] - self.y), border_radius=10)

        text = self.font.render(line, True, self.fg_color)
        # pygame.draw.rect(text, GREY, text.get_rect(), 1)  # for demo show render area
        self.surface.blit(text, (0, self.y))

        self.y += self.y_delta

    # call update from pygame main loop
    def update(self):
        time_now = time.time()
        if (self.next_time is None or self.next_time < time_now) and self.lines:
            self.next_time = time_now + self.ms_per_line / 1000
            line = self.lines.pop(0)
            self._update_line(line)
            self.dirty = True
            self.update()  # do it again to catch more than one event per tick

    # call draw from pygam main loop after update
    def draw(self, screen):
        if self.dirty:
            screen.blit(self.surface, self.rect)
            self.dirty = False


class WidgetFactory:
    @staticmethod
    def create_button(x: int, y: int, text: str, action: Callable = None) -> pygame_widgets.button.Button:
        surface = pygame.display.get_surface()
        icolor = (211, 211, 211)
        hcolor = (169, 169, 169)
        pcolor = (30, 144, 255)
        result = Button(surface, x, y, 150, 30, text=text, fontSize=20, margin=10, radius=5, inactiveColour=icolor, hoverColour=hcolor, pressedColour=pcolor)
        if action:
            result.onClick = action
        return result


class Application:
    def __init__(self, app_name: str = "Title"):
        pygame.init()
        self.text_font = pygame.font.SysFont("Verdana", 20, bold=True)
        self.display = pygame.display
        self.surface = pygame.display.get_surface()
        self.display.set_caption(app_name)
        self.screen = pygame.display.set_mode((970, 550))
        self.screen.fill("white")
        self.clock = pygame.time.Clock()

        self.message = TextScroll(pygame.Rect(10, 10, 950, 470), self.text_font, YELLOW, BLACK, "", ms_per_line=300)

        button_pos_y = 500
        self.btn_first = WidgetFactory.create_button(10, button_pos_y, "First", action=lambda: self.message.set_text("First"))
        self.btn_next = WidgetFactory.create_button(210, button_pos_y, "Next", action=lambda: self.message.set_text("Next"))
        self.btn_play_pause = WidgetFactory.create_button(410, button_pos_y, "Play / Pause", action=lambda: self.message.set_text("Play / Pause"))
        self.btn_prev = WidgetFactory.create_button(610, button_pos_y, "Prev", action=lambda: self.message.set_text("Prev"))
        self.btn_last = WidgetFactory.create_button(810, button_pos_y, "Last", action=lambda: self.message.set_text("Last"))

        self.display.update()

    def run(self):
        running = True
        while running is True:
            events = pygame.event.get()
            for event in events:
                match event.type:
                    case pygame.QUIT:
                        running = False
                    case _:
                        ...
            else:
                self.message.update()
                self.message.draw(self.screen)
                pygame.display.flip()
                self.clock.tick(60)

            sleep(0.02)
            pygame_widgets.update(events)  # Call once every loop to allow widgets to render and listen
            pygame.display.update()

        pygame.quit()


if __name__ == "__main__":
    application = Application("DAISY 2.02 Digital Talking Book Reader")
    application.run()
