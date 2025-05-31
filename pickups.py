import pygame
from enemy import Enemy

class Pickup(Enemy):
    def __init__(self, x, y, image_path):
        super().__init__(x, y) # call Enemy constructor
        self.image = pygame.image.load(image_path).convert_alpha() # pickup image

    def enemy_took_damage(self, amount):  # overwrite to do nothing
        pass

    def enemy_is_dead(self): # overwrite to do nothing
        return False

class CoinPickup(Pickup):
    def __init__(self, x, y):
        super().__init__(x, y, "images/coin_pickup_texture.png")

class HealthPickup(Pickup):
    def __init__(self,x,y):
        super().__init__(x,y,"images/health_pickup_texture.png")