from settings import * 
from sprites import * 
from groups import AllSprites
from support import * 
from timer import Timer
from random import randint

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Platformer')
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = 'menu'

        # fonts
        font_path = pygame.font.match_font('minecraft')
        self.font = pygame.font.Font(font_path, 30) if font_path else pygame.font.Font(None, 30)
        self.font_large = pygame.font.Font(font_path, 60) if font_path else pygame.font.Font(None, 60)
        
        robus_path = join('data', 'fonts', 'Robus-BWqOd.otf')
        self.font_robus = pygame.font.Font(robus_path, 60)

        # groups 
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # load game 
        self.load_assets()
        self.setup()

        # timers 
        self.bee_timer = Timer(100, func = self.create_bee, autostart = True, repeat = True)
    
    def create_bee(self):
        Bee(frames = self.bee_frames, 
            pos = ((self.level_width + WINDOW_WIDTH),(randint(0,self.level_height))), 
            groups = (self.all_sprites, self.enemy_sprites),
            speed = randint(300,500))

    def create_bullet(self, pos, direction):
        x = pos[0] + direction * 34 if direction == 1 else pos[0] + direction * 34 - self.bullet_surf.get_width()
        Bullet(self.bullet_surf, (x, pos[1]), direction, (self.all_sprites, self.bullet_sprites))
        Fire(self.fire_surf, pos, self.all_sprites, self.player)
        self.audio['shoot'].play()

    def load_assets(self):
        # graphics 
        self.player_frames = import_folder('images', 'player')
        self.bullet_surf = import_image('images', 'gun', 'bullet')
        self.fire_surf = import_image('images', 'gun', 'fire')
        self.bee_frames = import_folder('images', 'enemies', 'bee')
        self.worm_frames = import_folder('images', 'enemies', 'worm')
        self.logo = import_image('images', 'logo')

        # sounds 
        self.audio = audio_importer('audio')

    def setup(self):
        tmx_map = load_pygame(join('data', 'maps', 'world.tmx'))
        self.level_width = tmx_map.width * TILE_SIZE
        self.level_height = tmx_map.height * TILE_SIZE

        for x, y, image in tmx_map.get_layer_by_name('Main').tiles():
            Sprite((x * TILE_SIZE,y * TILE_SIZE), image, (self.all_sprites, self.collision_sprites))
        
        for x, y, image in tmx_map.get_layer_by_name('Decoration').tiles():
            Sprite((x * TILE_SIZE,y * TILE_SIZE), image, self.all_sprites)
        
        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites, self.player_frames, self.create_bullet)
            if obj.name == 'Worm':
                Worm(self.worm_frames, pygame.FRect(obj.x, obj.y, obj.width, obj.height), (self.all_sprites, self.enemy_sprites))

        # self.audio['music'].play(loops = -1)
        self.audio['music'].play(loops = -1)

    def reset_game(self):
        self.all_sprites.empty()
        self.collision_sprites.empty()
        self.bullet_sprites.empty()
        self.enemy_sprites.empty()
        self.audio['music'].stop()
        self.setup()
        self.state = 'game'

    def collision(self):
        # bullets -> enemies 
        for bullet in self.bullet_sprites:
            sprite_collision = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
            if sprite_collision:
                self.audio['impact'].play()
                bullet.kill()
                for sprite in sprite_collision:
                    sprite.destroy()
        
        # enemies -> player
        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask):
            self.state = 'game_over'

    def run_game(self, dt):
        self.bee_timer.update()
        self.all_sprites.update(dt)
        self.collision()
        self.display_surface.fill(BG_COLOR)
        self.all_sprites.draw(self.player.rect.center)

    def draw_menu_background(self):
        self.display_surface.fill(BG_COLOR)
        # Draw the game world but focused on player or center
        # We can use the current player position
        self.all_sprites.draw(self.player.rect.center)
        
        # Darken
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0,0,0))
        self.display_surface.blit(overlay, (0,0))

    def run_menu(self):
        self.draw_menu_background()
        
        # Logo
        logo_rect = self.logo.get_rect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 4))
        self.display_surface.blit(self.logo, logo_rect)

        # Play Button
        play_text = self.font_large.render('PLAY', True, 'White')
        play_rect = play_text.get_rect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        
        # Draw button background (hover effect)
        mouse_pos = pygame.mouse.get_pos()
        if play_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.display_surface, (100, 100, 100), play_rect.inflate(20, 10))
            if pygame.mouse.get_pressed()[0]:
                self.state = 'game'
        else:
            pygame.draw.rect(self.display_surface, (50, 50, 50), play_rect.inflate(20, 10))
        
        self.display_surface.blit(play_text, play_rect)

    def run_game_over(self):
        self.draw_menu_background()
        
        # Game Over Text
        game_over_text = self.font_robus.render('Game Over', True, 'Red')
        game_over_rect = game_over_text.get_rect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 3))
        self.display_surface.blit(game_over_text, game_over_rect)

        # Restart Button
        restart_text = self.font_large.render('Restart', True, 'White')
        restart_rect = restart_text.get_rect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))

        # Stop the audio
        
        
        # Draw button background (hover effect)
        mouse_pos = pygame.mouse.get_pos()
        if restart_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.display_surface, (100, 100, 100), restart_rect.inflate(20, 10))
            if pygame.mouse.get_pressed()[0]:
                self.reset_game()
        else:
            pygame.draw.rect(self.display_surface, (50, 50, 50), restart_rect.inflate(20, 10))
        
        self.display_surface.blit(restart_text, restart_rect)

    def run(self):
        while self.running:
            dt = self.clock.tick(FRAMERATE) / 1000 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False 
            
            if self.state == 'menu':
                self.run_menu()
            elif self.state == 'game':
                self.run_game(dt)
            elif self.state == 'game_over':
                self.run_game_over()
            
            pygame.display.update()
        
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run() 