import pygame

class Button:

    def __init__(self, x, y, text, screen, width, height, color):
        self.x = x
        self.y = y
        self.text = text
        self.screen = screen
        self.width = width
        self.height = height
        self.color = color
        self.font = pygame.font.SysFont('Arial', 15)
        self.draw_button_with_text()

    def text_objects(self, text, font):
        """Renders font string into image """
        textSurface = font.render(text, True, (255, 255, 255))
        return textSurface, textSurface.get_rect()

    def draw_button_with_text(self):
        """Draws a button with text"""
        pygame.draw.rect(self.screen, self.color, (self.x, self.y, self.width, self.height))
        textSurf, textRect = self.text_objects(self.text, self.font)
        textRect.center = ((self.x + (self.width / 2)), (self.y + (self.height / 2)))
        self.screen.blit(textSurf, textRect)

    def button_hovered(self, mouse, hover_color):
        """
        Checks if mouse hovered above button dimensions, changes to hover color if so
        :param mouse: pygame object
        :param hover_color: rgb tuple
        :return: boolean
        """
        if self.x + self.width > mouse[0] > self.x and self.y + self.height > mouse[
            1] > self.y:
            self.color = hover_color
            self.draw_button_with_text()
            return True
        return False

    def button_clicked(self, click, mouse, hover_color):
        """
        Checks if button is clicked
        :param click: pygame object
        :param mouse: pygame object
        :param hover_color: rgb tuple
        :return: boolean
        """
        if self.button_hovered(mouse, hover_color):
            if click[0] == 1:
                return True
        return False