import pygame

class Bullet:
    def __init__ (self,x,y,bullet_speed=5):
        self.image=pygame.Surface((5,10))
        self.image.fill((255,255,0))
        self.rect = self.image.get_rect(center=(x, y))
        self.bullet_speed=bullet_speed

    def update(self):
        self.rect.y-=self.bullet_speed # move bullet upward

    def draw(self,screen):
        screen.blit(self.image,self.rect)

    def bullet_off_screen(self,height_of_screen):
        return self.rect.bottom<0 # if bullet is off screen, remove it
