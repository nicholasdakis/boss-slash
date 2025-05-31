import pygame

class Button: # buttons in the shop
    def __init__(self,rect,text,font,button_clicked):
        self.rect=pygame.Rect(rect)
        self.text=text
        self.font=font
        self.button_clicked=button_clicked
        self.color=(70,70,70)
        self.hovering_color=(100,100,100) # lighter tone when hovering on a button

    def draw(self,surface):
        position=pygame.mouse.get_pos()
        if self.rect.collidepoint(position):
            color=self.hovering_color
        else:
            color=self.color
        pygame.draw.rect(surface,color,self.rect)
        text_surface=self.font.render(self.text,True,(255,255,255))
        text_rect=text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface,text_rect)

    def check_if_clicking(self,position):
        if self.rect.collidepoint(position):
            self.button_clicked()

class Shop:
    def __init__(self,screen,data_manager,player):
        self.screen=screen
        self.data_manager=data_manager
        self.player=player
        self.sound_error = pygame.mixer.Sound("audios/error_sfx.wav")
        self.font=pygame.font.Font(None,30)
        self.max_level=10
        self.upgrade_cost=10
        # upgrades
        self.fire_rate_level=0
        self.damage_level = 0
        self.vitality_level = 0
        self.speed_level = 0
        button_w=220
        button_h=40
        spacing=10
        start_x=50
        start_y=100
        # each button for each upgrade
        self.fire_rate_button = Button(
            (start_x,start_y, button_w, button_h),
            self.get_upgrade_text("Fire Rate", self.fire_rate_level),
            self.font,
            self.buy_fire_rate_upgrade
        )
        self.damage_button = Button(
            (start_x, start_y + (button_h + spacing), button_w, button_h),
            self.get_upgrade_text("Damage", self.damage_level),
            self.font,
            self.buy_damage_upgrade
        )
        self.vitality_button = Button(
            (start_x, start_y + 2*(button_h + spacing), button_w, button_h),
            self.get_upgrade_text("Vitality", self.vitality_level),
            self.font,
            self.buy_vitality_upgrade
        )
        self.speed_button = Button(
            (start_x, start_y + 3*(button_h + spacing), button_w, button_h),
            self.get_upgrade_text("Speed", self.speed_level),
            self.font,
            self.buy_speed_upgrade
        )

    def get_roman(self, n):
        romans = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
        return romans[n-1] if 1 <= n <= 10 else str(n)

    def get_upgrade_text(self, name, level):
        if level >= self.max_level:
            return f"{name} Level Max"
        else:
            next_level=level+1
            return f"{name} {self.get_roman(next_level)} - ${self.upgrade_cost}"

    def buy_fire_rate_upgrade(self):
        self.buy_upgrade("fire_rate")

    def buy_damage_upgrade(self):
        self.buy_upgrade("damage")

    def buy_vitality_upgrade(self):
        self.buy_upgrade("vitality")

    def buy_speed_upgrade(self):
        self.buy_upgrade("speed")

    def buy_upgrade(self, upgrade_name):
        level_attr = f"{upgrade_name}_level"
        current_level = getattr(self, level_attr)
        if current_level >= self.max_level:
            return
        coins = self.data_manager.data.get("coins", 0) # load stored coins
        if coins >= self.upgrade_cost:
            coins -= self.upgrade_cost
            self.data_manager.data["coins"] = coins # update stored coins
            setattr(self, level_attr, current_level + 1)
            self.data_manager.save()
            # update button text
            button_attr = f"{upgrade_name}_button"
            button = getattr(self, button_attr)
            button.text = self.get_upgrade_text(upgrade_name.capitalize(), current_level + 1)
            # update json file
            self.data_manager.store_upgrade(upgrade_name,current_level+1)
        else: # not enough coins to upgrade
            self.sound_error.play()
    
    def load_upgrades(self):
        for upgrade_name in ["fire_rate", "damage", "vitality", "speed"]:
            level = self.data_manager.data.get(upgrade_name, 0)
            setattr(self, f"{upgrade_name}_level", level)
            button = getattr(self, f"{upgrade_name}_button")
            button.text = self.get_upgrade_text(upgrade_name.capitalize(), level)

    def update(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # check if the player clicks an upgrade
                self.fire_rate_button.check_if_clicking(event.pos)
                self.damage_button.check_if_clicking(event.pos)
                self.vitality_button.check_if_clicking(event.pos)
                self.speed_button.check_if_clicking(event.pos)

    def draw(self):
        self.screen.fill((30, 30, 30))
        money = self.data_manager.data.get("coins", 0)
        money_text = self.font.render(f"Money: ${money}", True, (255, 255, 255))
        self.screen.blit(money_text, (50, 50))
        self.fire_rate_button.draw(self.screen)
        self.damage_button.draw(self.screen)
        self.vitality_button.draw(self.screen)
        self.speed_button.draw(self.screen)