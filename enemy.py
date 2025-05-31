import pygame

class Enemy:
    def __init__ (self,x,y,speed=1.5,health=25):
        self.image=pygame.Surface((40,30))
        self.image.fill((200,50,50))
        self.rect=self.image.get_rect(topleft=(x,y))
        self.speed=speed
        self.health=health

    def update(self):
        self.rect.y+=self.speed # move enemy downward

    def draw(self,screen):
        screen.blit(self.image,self.rect)

    def enemy_took_damage(self,amount):
        self.health-=amount

    def enemy_is_dead(self):
        return self.health<=0
    
    def enemy_off_screen(self,screen_size):
        screen_width,screen_height=screen_size
        return self.rect.top>screen_height # enemy went all the way down and off screen