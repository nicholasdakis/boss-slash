import sys, pygame, random
from player import Player
from enemy import Enemy
from pickups import CoinPickup
from pickups import HealthPickup
from data_manager import DataManager
from shop import Shop

class Main:
    def __init__ (self):
        pygame.init() # constructor
        size = width,height = 1280, 720
        self.screen = pygame.display.set_mode(size,pygame.RESIZABLE)
        self.clock = pygame.time.Clock() # controls frame rate
        self.fps=60 # cap fps to 60 initially
        self.state="mainmenu"
        self.update_mainmenu_buttons() # dynamically update menu button hitboxes
        # add the background image for the main menu
        self.background_image=pygame.image.load(f"images/mainMenuBG.png").convert_alpha()
        # flag to see if the mouse is hovering
        self.hovering=False
        #load menu theme indefinitely
        pygame.mixer.music.load("audios/menu_theme.wav")
        pygame.mixer.music.play(-1)
        # load sounds
        self.sound_hover = pygame.mixer.Sound("audios/button_hover.wav")
        self.sound_click = pygame.mixer.Sound("audios/button_click.wav")
        self.sound_enemy_death = pygame.mixer.Sound("audios/enemy_death.wav")
        self.sound_coin_pickup = pygame.mixer.Sound("audios/coin_pickup.wav")
        self.sound_heart_pickup = pygame.mixer.Sound("audios/heart_pickup.wav")
        # create the buttons on the main menu
        self.play_button_rect = None
        self.settings_button_rect = None
        self.credits_button_rect = None
        self.achievements_button_rect = None
        # load player
        self.player = None
        # load hover button
        self.hovered_button = None
        # load game data manager
        self.data_manager = DataManager()
        # pickups (dropped from enemies)
        self.coins=[]
        self.hearts=[]
        # enemies
        self.enemies=[]
        self.enemy_spawn_delay=random.randint(3000,3500) # spawn delay of enemies is between 3 and 3.5 seconds
        self.last_enemy_spawn_time=pygame.time.get_ticks()
        # load PERSISTENT items
        self.data_manager.load()
        self.persistent_coin_count = self.data_manager.data.get("coins", 0)  # load coins count if exists

    def run(self):
        running=True
        while running:
            events = pygame.event.get()
            for event in events:
                
                if event.type==pygame.QUIT:
                    running=False

                elif event.type==pygame.VIDEORESIZE:
                    self.screen=pygame.display.set_mode((event.w,event.h),pygame.RESIZABLE) # handle resizing
                    # make sure the player stays at the bottom of the screen after the user resizes the window
                    before_width,before_height=self.screen.get_size()
                    after_width,after_height=event.w,event.h
                    if self.state == "play" and self.player:
                        self.reposition_player_x(before_width, before_height, after_width, after_height)

                    # detect mouse motions
                elif event.type==pygame.KEYDOWN:
                    # escape goes to main menu, except in play it goes to pause menu, and pause menu goes to main menu or back to play
                    if (event.key==pygame.K_ESCAPE):
                        if self.state=="play":
                            self.state="pausemenu"
                            pygame.mixer.music.set_volume(0.5)
                        elif self.state=="settings" or self.state=="achievements" or self.state=="credits":
                            self.state="mainmenu" # don't start the song over, since they have the same theme as main menu
                        elif self.state=="mainmenu": # if you press ESC while on main menu, close the game
                            running=False
                        else:
                            self.state="mainmenu"
                            pygame.mixer.music.stop() # stop play theme
                            pygame.mixer.music.load("audios/menu_theme.wav")
                            pygame.mixer.music.play(-1)
                    # pressing space while in pause menu goes back to play
                    if (event.key==pygame.K_SPACE):
                        if self.state=="pausemenu": # if in pause menu, simply resume current game
                            self.state="play"
                        elif self.state=="mainmenu": # if in main menu, start a fresh game
                            self.state="play"
                            pygame.mixer.music.stop() # stop menu theme
                            pygame.mixer.music.load("audios/play_theme.wav")
                            pygame.mixer.music.play(-1)
                            self.reset_game()

                            pygame.mixer.music.set_volume(1.0)
                            
                elif event.type == pygame.MOUSEMOTION and self.state=="mainmenu":
                    if not self.buttons_ready(): # check if the buttons are initialized
                        continue  # skip if not initialized (prevents crashing if hovering too early after bootup)
                        # detect which button is hovered over
                    pos = event.pos
                    hovered_now = None
                    if self.play_button_rect.collidepoint(pos):
                        hovered_now = "play"
                    elif self.settings_button_rect.collidepoint(pos):
                        hovered_now = "settings"
                    elif self.credits_button_rect.collidepoint(pos):
                        hovered_now = "credits"
                    elif self.achievements_button_rect.collidepoint(pos):
                        hovered_now = "achievements"
                    if hovered_now != getattr(self, "hovered_button", None): # if currently hovering over a new button or over the first button
                        self.hovered_button = hovered_now # update which button is hovered over
                        if (hovered_now is not None): # only make a sound when hovering on a button, not when going off of it
                            self.sound_hover.play()

                elif event.type == pygame.MOUSEBUTTONDOWN and self.state=="mainmenu":
                    # make sure buttons are not hovered too early
                    if not self.buttons_ready():
                            continue
                    # handle clicking different buttons
                    pos = event.pos
                    clicked_now = None
                    if self.play_button_rect.collidepoint(pos):
                        clicked_now = "play"
                    elif self.settings_button_rect.collidepoint(pos):
                        clicked_now = "settings"
                    elif self.credits_button_rect.collidepoint(pos):
                        clicked_now = "credits"
                    elif self.achievements_button_rect.collidepoint(pos):
                        clicked_now = "achievements"
                    if clicked_now:
                        self.sound_click.play() # click sound
                        self.state=clicked_now # change state (game scene) to what was clicked
                    # change to play theme
                    if (clicked_now=="play"):
                        pygame.mixer.music.stop() # stop menu theme
                        pygame.mixer.music.load("audios/play_theme.wav")
                        pygame.mixer.music.play(-1)
                        self.reset_game() # start the game from the start if the player exits

            #update player every frame
            if self.state=="play" and self.player:
                self.player.update()
                # if player dies, save coin amount and go to shop
                if self.player.player_died():
                    self.data_manager.store_coins(self.player.coins) # update the json data file
                    self.persistent_coin_count = self.player.coins # update persistent coin count, since player didn't leave mid-playthrough
                    self.state="shop"
                    pygame.mixer.music.stop() # stop menu theme
                    pygame.mixer.music.load("audios/shop_theme.wav")
                    pygame.mixer.music.play(-1)
                # spawn enemies
                current_time=pygame.time.get_ticks()
                if current_time-self.last_enemy_spawn_time>self.enemy_spawn_delay:
                    screen_w, _ = self.screen.get_size() # height not needed
                    enemy_x = random.randint(0, screen_w - 40)  # enemy width=40
                    enemy = Enemy(enemy_x, -30)  # spawn above screen
                    self.enemies.append(enemy)
                    self.last_enemy_spawn_time = current_time
                    self.enemy_spawn_delay = random.randint(3000, 3500)  # reset delay
                # update enemies
                for enemy in self.enemies:
                    enemy.update()
                    enemy.draw(self.screen)
                    if enemy.enemy_off_screen(self.screen.get_size()): # if enemy is off screen before player kills, player loses health
                        self.player.current_health-=10
                        self.enemies.remove(enemy)
                        self.player.sound_player_hurt.play()
                # update coins
                for coin in self.coins[:]:
                    coin.update()
                    coin.draw(self.screen)
                    if coin.enemy_off_screen(self.screen.get_size()): # coin inherits enemy, so uses same logic
                        self.coins.remove(coin)
                # update hearts
                for heart in self.hearts[:]:
                    heart.update()
                    heart.draw(self.screen)
                    if heart.enemy_off_screen(self.screen.get_size()):
                        self.hearts.remove(heart)

                # updates / checks
                self.update_bullets_and_enemies()
                self.player.check_player_and_enemy_collide(self.enemies) # check if the enemy and player are touching
                self.check_coin_pickup() # check if player and a coin are touching
                self.check_heart_pickup()
              

            # show appropriate screen based on game scene:
            if self.state=="mainmenu":
                self.draw_mainmenu()
            elif self.state=="play":
                self.draw_play()
            elif self.state=="pausemenu":
                self.draw_pausemenu()
            elif self.state=="settings":
                self.draw_settings()
            elif self.state=="achievements":
                self.draw_achievements()
            elif self.state=="credits":
                self.draw_credits()
            elif self.state == "shop": # shop is handled in its own class
                self.shop.update(events)
                self.shop.draw()
            
            pygame.display.set_caption(f"Boss Slash - {self.clock.get_fps():.2f} FPS") # caption (currently shows fps also)
            pygame.display.flip() # update display
            self.clock.tick(self.fps) # cap at user's chosen fps
    
    def draw_mainmenu(self):
            self.update_mainmenu_buttons() # dynamically update menu button hitboxes
            # scale the image appropriately
            scaled_image = pygame.transform.scale(self.background_image, (self.screen.get_width(), self.screen.get_height())) # scale image based on user's window
            self.screen.blit(scaled_image,(0,0))

    def draw_play(self):
        self.screen.fill((50,50,50))
        if self.player:
            self.screen.blit(self.player.image,self.player.rect)
            # draw bullets
            for bullet in self.player.bullets:
                bullet.draw(self.screen)
            # draw enemies
            for enemy in self.enemies:
                enemy.draw(self.screen)
            # draw coin pickups
            for coin in self.coins:
                coin.draw(self.screen)
            # draw health pickups
            for heart in self.hearts:
                heart.draw(self.screen)
            # below are drawn last to appear on top
            self.draw_player_health() #hp bar
            self.draw_player_coins() # coins bar

    def draw_settings(self):
        self.screen.fill((50,50,50))

    def draw_credits(self):
        self.screen.fill((50,50,50))

    def draw_achievements(self):
        self.screen.fill((50,50,50))

    def draw_pausemenu(self):
        self.screen.fill((20,60,20))

    def update_mainmenu_buttons(self):
        # size of each button's hitbox
        screen_w, screen_h = self.screen.get_size()
        play_width = int(screen_w * 0.26)
        settings_width = int(screen_w * 0.45)
        credits_width = int(screen_w * 0.45)
        achievements_width = int(screen_w * 0.75)
        button_height = int(screen_h * 0.12) # all have same height
        # position on the screen as fractions of the width and height
        play_x = int(screen_w * 0.36)
        play_y = int(screen_h * 0.26)
        # add gaps between each button and manually align positions on screen
        settings_x = play_x-110
        settings_y = play_y + button_height + 20 
        credits_x = play_x-110
        credits_y = settings_y + button_height + 20
        achievements_x = play_x-310
        achievements_y = credits_y + button_height + 30 # 25 instead of 20 to cover all the text
        # add the hitboxes
        self.play_button_rect = pygame.Rect(play_x, play_y, play_width, button_height)
        self.settings_button_rect = pygame.Rect(settings_x, settings_y, settings_width, button_height)
        self.credits_button_rect = pygame.Rect(credits_x, credits_y, credits_width, button_height)
        self.achievements_button_rect = pygame.Rect(achievements_x, achievements_y, achievements_width, button_height)

    def draw_player_health(self):
        if self.player:
            x,y=20,20 # health in top left corner
            health_width,health_height=100,20
            ratio=self.player.current_health / self.player.max_health
            pygame.draw.rect(self.screen, (50, 50, 50), (x, y, health_width, health_height))
            pygame.draw.rect(self.screen, (255, 0, 0), (x, y, int(health_width * ratio), health_height))
            pygame.draw.rect(self.screen, (255, 255, 255), (x, y, health_width, health_height), 2) # health border
            font = pygame.font.Font(None, 20)
            health_text = font.render(f"{self.player.current_health}", True, (255, 255, 255))
            self.screen.blit(health_text, (x + 36, y + 4))

    def draw_player_coins(self):
        if self.player:
            x,y=20,50 # coins under health bar
            font = pygame.font.SysFont(None, 18)
            text = font.render(f"Coins: {self.player.coins}", True, (255, 215, 0))
            self.screen.blit(text, (x,y))



    def buttons_ready(self):
        if (
            self.play_button_rect is not None and
            self.settings_button_rect is not None and
            self.credits_button_rect is not None and
            self.achievements_button_rect is not None
        ):
            return True
        else:
            return False
        
    def reposition_player_x(self,before_width,before_height,after_width,after_height): # make sure the player stays in the correct relative x position after the window is resized
        if self.player:
            if before_width!=0:
                relative_x=self.player.rect.centerx / before_width
            else:
                relative_x=0.5 # default to center otherwise
            new_center=int(relative_x * after_width)
            # make sure the player stays 20 pixels above the bottom, while maintaining the correct x
            new_midbottom=(new_center,after_height-20)
            self.player.rect.midbottom=new_midbottom

    def update_bullets_and_enemies(self):
        for bullet in self.player.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.rect.colliderect(enemy.rect): # if a bullet hits an enemy
                    self.player.bullets.remove(bullet)
                    enemy.health-=self.player.damage_dealt # subtract health based on shot damage
                    if (enemy.health<=0):
                        self.sound_enemy_death.play()
                        self.enemies.remove(enemy)
                        if (random.random()<0.25): # 25% chance for enemy to drop coin on death
                            coin=CoinPickup(enemy.rect.x,enemy.rect.y)
                            self.coins.append(coin)
                        elif random.random()<0.25: # chance to drop health if a coin does not drop
                            heart=HealthPickup(enemy.rect.x,enemy.rect.y)
                            self.hearts.append(heart)
                    break # bullet should only hit one enemy each

    def check_coin_pickup(self): # checks if the player collided with an on-screen coin
        for coin in self.coins[:]:
            if self.player.rect.colliderect(coin.rect):
                self.player.coins += 1 # current coin count (not persistent unless player dies)
                self.sound_coin_pickup.play()
                self.coins.remove(coin)

    def check_heart_pickup(self): # checks if the player collided with an on-screen heart
        for heart in self.hearts[:]:
            if self.player.rect.colliderect(heart.rect):
                if (self.player.current_health+5>=self.player.max_health):
                    self.player.current_health = self.player.max_health
                else:
                    self.player.current_health+=5
                self.sound_heart_pickup.play()
                self.hearts.remove(heart)

    def reset_game(self):
        screen_w, screen_h = self.screen.get_size()
        # load the stored upgrades
        upgrades = {
            "fire_rate": self.data_manager.data.get("fire_rate", 0),
            "damage": self.data_manager.data.get("damage", 0),
            "vitality": self.data_manager.data.get("vitality", 0),
            "speed": self.data_manager.data.get("speed", 0)
        }
        self.player = Player(screen_w // 2, screen_h - 20,upgrades=upgrades) # reset player position
        self.shop = Shop(self.screen,self.data_manager,self.player)
        self.player.coins=self.persistent_coin_count
        self.enemies = [] # clear enemies
        self.coins = [] # clear coins
        self.hearts = [] # clear hearts
        self.last_enemy_spawn_time = pygame.time.get_ticks()
        self.enemy_spawn_delay = random.randint(3000, 3500)

if __name__=="__main__":
    game=Main()
    game.run()
    pygame.quit()
    sys.exit()