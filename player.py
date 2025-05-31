import pygame, random
from bullet import Bullet
from enemy import Enemy

class Player:
    def __init__(self, x, y, speed=7.5, max_health=0, damage_dealt=12.5, coins=0, upgrades=None):
        self.upgrades=upgrades or {}
        # placeholder player
        self.image = pygame.Surface((50,30))
        self.image.fill((50,30,30)) # player visual
        self.rect=self.image.get_rect(midbottom=(x,y)) # player hitbox
        self.current_health=max_health
        # bullets / firing
        self.bullets=[] # holds active bullets
        self.last_fire_time=0
        # the upgradeable perks: default + the effect of the purchased upgrades, if any
        fire_rate_level = self.upgrades.get("fire_rate", 0)
        damage_level = self.upgrades.get("damage", 0)
        vitality_level = self.upgrades.get("vitality", 0)
        speed_level = self.upgrades.get("speed", 0)
        # base values
        base_fire_rate = 1
        base_damage = damage_dealt
        base_health = max_health
        base_speed = speed
        # updated values (based on upgrades unlocked)
        actual_fire_rate=base_fire_rate+0.2*fire_rate_level
        actual_damage=base_damage+2*damage_level
        actual_health=base_health+5*vitality_level
        actual_speed=base_speed+0.5*speed_level
        self.fire_delay = int(1000 / actual_fire_rate)
        self.damage_dealt = actual_damage
        self.max_health = actual_health
        self.speed = actual_speed
        self.coins = coins

        # player hurt sound
        self.sound_player_hurt = pygame.mixer.Sound("audios/player_hurt.wav")
        # player bullet sound
        self.player_bullet_shot = pygame.mixer.Sound("audios/player_bullet_shot.wav")
        self.player_bullet_shot.set_volume(0.08) # less annoying
        
    def player_took_damage(self,damage_count):
        self.current_health-=damage_count
        if self.current_health<0:
            self.current_health=0

    def player_died(self):
        return self.current_health<=0
    
    def player_inputs(self):
        # left and right movement
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] or key[pygame.K_a]:
            self.rect.x -= self.speed
        if key[pygame.K_RIGHT] or key[pygame.K_d]:
            self.rect.x += self.speed

    def draw(self,screen):
        screen.blit(self.image,self.rect)

    def update(self):
        keys = pygame.key.get_pressed()  # get all key states
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
            # stay in screen bounds based on user's window
        if self.rect.right > pygame.display.get_surface().get_width():
            self.rect.right = pygame.display.get_surface().get_width()
        if self.rect.left < 0:
            self.rect.left=0

        # handle firing
        current_time=pygame.time.get_ticks()
        if current_time - self.last_fire_time >= self.fire_delay: # shoot every fire_delay milliseconds
            self.fire()
            self.last_fire_time=current_time
            self.fire_delay = int(1000/(1+0.2*(self.upgrades.get("fire_rate", 0))))
        
        # update bullets
        screen_height=pygame.display.get_surface().get_height()
        for bullet in self.bullets[:]: # slice the list
            bullet.update()
            if bullet.bullet_off_screen(screen_height):
                self.bullets.remove(bullet)
            
    def fire(self):
        bullet_x=self.rect.centerx # bullets are shot from the player
        bullet_y=self.rect.top
        self.player_bullet_shot.play() # bullet sfx, one per bullet
        self.bullets.append(Bullet(bullet_x,bullet_y)) # add to list of active bullets

    def check_player_and_enemy_collide(self, enemies):
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                self.player_took_damage(10) # if enemy touches player lose 10 health (fixed amount)
                self.sound_player_hurt.play()
                enemies.remove(enemy)
