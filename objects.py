import pygame
pygame.font.init()
#colors

class __Object():

    def __init__(self, position_x:float, position_y:float, screen:pygame.Surface):
        self.position = pygame.Vector2(position_x, position_y)
        self.screen = screen

    def render(self):
        """
        Display your object
        """
        self.screen.blit(self.display,self.position)
    pass


class Text(__Object):
    
    def __init__(self, position_x:float, position_y:float, screen:pygame.Surface, text:str = 'Placeholder', font:str = 'comicsansms', text_size:int = 20, text_color:pygame.Color = pygame.Color(255,255,255)):
        self.text = text
        self.text_color = text_color
        self.text_size = text_size
        self.font = font
        self.display = pygame.font.SysFont(self.font,self.text_size).render(str(self.text),True,self.text_color)
        super().__init__(position_x, position_y, screen)

    def assemble(self):
        self.display = pygame.font.SysFont(self.font,self.text_size).render(str(self.text),True,self.text_color)

    def render(self):
        """
        Display your text
        """
        self.assemble()
        self.screen.blit(self.display,self.position)


class Button(__Object):
    
    def __init__(self, command, position_x:float, position_y:float, screen:pygame.Surface, text:str = 'Placeholder', font:str = 'comicsansms', text_size:int = 20, text_color:pygame.Color = pygame.Color(255,255,255), background_color:pygame.Color = pygame.Color(0,0,0)):
        self.command = command
        self.text = text
        self.text_color = text_color
        self.text_size = text_size
        self.font = font
        self.background_color = background_color
        self.display = pygame.font.SysFont(self.font,self.text_size).render(str(self.text),True,self.text_color, self.background_color)
        super().__init__(position_x, position_y, screen)

    @property
    def clickbox(self):
        clickbox = self.display.get_rect()
        clickbox.x = self.position.x
        clickbox.y = self.position.y
        return clickbox

    def click(self):
        self.command()
            
    def is_clicked(self, event):
            return self.clickbox.collidepoint(event)

    def assemble(self):
        self.display = pygame.font.SysFont(self.font,self.text_size).render(str(self.text),True,self.text_color)

    def render(self):
        """
        Display your text
        """
        self.assemble()
        self.screen.blit(self.display,self.position)


class Image(__Object):

    def __init__(self, position_x:float, position_y:float, screen, scale, image):

        self.scale = scale
        self.image = image
        self.display = pygame.transform.scale(image, (image.get_size()[0]*scale,image.get_size()[1]*scale))

        super().__init__(position_x, position_y,screen)

    pass

