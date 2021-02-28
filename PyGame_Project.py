from settings import *
import random


pg.init()
screen = pg.display.set_mode(SIZE)
screen.fill(pg.Color('black'))
clock = pg.time.Clock()
# ============================================ звуки и музыка ==========================================================
pg.mixer.music.load(os.path.join('DATA', 'music.mp3'))
pg.mixer.music.play(-1)
pg.mixer.music.set_volume(0.3)

blaster_sound = pg.mixer.Sound(os.path.join('DATA', 'blaster_sound.mp3'))
take_damage_sound = pg.mixer.Sound(os.path.join('DATA', 'take_damage_sound.mp3'))
healing_sound = pg.mixer.Sound(os.path.join('DATA', 'healing_sound.mp3'))
boom_sounds = [pg.mixer.Sound(os.path.join('DATA', 'boom_sound1.mp3')),
               pg.mixer.Sound(os.path.join('DATA', 'boom_sound2.mp3')),
               pg.mixer.Sound(os.path.join('DATA', 'boom_sound3.mp3'))]
for sound in boom_sounds:
    sound.set_volume(0.8)
blaster_sound.set_volume(0.05)
take_damage_sound.set_volume(0.5)
healing_sound.set_volume(0.5)


def load_image(name, colorkey=None):
    path = os.path.join('DATA', name)
    if not os.path.isfile(path):
        terminate()
    image = pg.image.load(path)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image

# =========================================== здесь меняю музыку, когда надо ===========================================
def change_music(status, loops):
    pg.mixer.music.stop()
    if status == 2:
        pg.mixer.music.load(os.path.join('DATA', 'game_end.mp3'))
    elif status == 1:
        pg.mixer.music.load(os.path.join('DATA', 'music.mp3'))
        pg.mixer.music.set_volume(0.3)
    else:
        pg.mixer.music.load(os.path.join('DATA', 'intro_music.mp3'))
        pg.mixer.music.set_volume(1.5)
    pg.mixer.music.play(loops)

# ======================================= здесь фон двигается ==========================================================
def moving_fon():
    global fon_x, fon_x1, score, cur_level, reached_fones, fon_left, fon_right
    if fon_left == -WIDTH or fon_left - cur_level < -WIDTH:
        fon_left = 0
    if fon_left % 12 == 0 and player.hp > 0:
        update_score(1)
    fon_left -= cur_level
    screen.blit(fon, (fon_left, 0))
    screen.blit(fon, (fon_left + WIDTH, 0))

# ======================================================= интро ========================================================
def show_intro():
    change_music(0, -1)
    run = True
    colors = {'Space Race': 'white', 'Нажмите любую клавишу для продолжения': 'grey'}
    lines = ['Space Race', 'Нажмите любую клавишу для продолжения']
    font = pg.font.Font(None, 50)
    y = HEIGHT // 2 - 50
    for line in lines:
        string = font.render(line, 1, pg.Color(colors[line]))
        rect = string.get_rect()
        y += 10
        rect.top = y
        rect.x = WIDTH // 2 - rect.w // 2
        y += rect.h
        screen.blit(string, rect)
        font = pg.font.Font(None, 25)
    while run:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            if event.type == pg.KEYDOWN or event.type == pg.MOUSEBUTTONDOWN:
                run = False
        pg.display.flip()
        clock.tick(FPS)
    menu()

# ============================================= проиграть какой-то звук ================================================


def play_sound(sound):
    sound.play()


# =============================================== обновить счетчик очков и увеличить сложность =========================


def update_score(step):
    global score, next_level, min_chance_of_enemy_birth
    if score <= next_level < score + step:
        next_level += 1000
        min_chance_of_enemy_birth += 0.01
    score += step


# ============================================== меню ==================================================================


def menu():
    global player_pos
    screen.blit(fon, (0, 0))
    buttons = []
    start_button_w = 350
    start_button_h = 100
    # ==================================== создарние кнопки start ======================================================
    start_button = Button(WIDTH // 2 - start_button_w // 2, HEIGHT // 2 - start_button_h // 2, start_button_w,
                          start_button_h, 'white', buttons, fon, all_spites)
    start_button.set_title('Start', 'white', 100)
    # ============================================= центр для логотипа =================================================
    logo_center = logo_image.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    while start_button in all_spites:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            if event.type == pg.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button.get_pos(*event.pos):
                        player_pos = event.pos
                        button.kill()
                        change_music(1, -1)
            if event.type == pg.MOUSEMOTION:
                for button in buttons:
                    if button.get_pos(*event.pos):
                        button.change_color(True)
                    else:
                        button.change_color(False)
        screen.blit(fon, (0, 0))
        # ===================================== рисуем сам логотип =====================================================
        screen.blit(logo_image, logo_center)
        all_spites.draw(screen)
        pg.display.flip()
        clock.tick(FPS)
    game_cycle()


# ============================================= создать противника =====================================================
def create_entity():
    # ========================================= выбираем противника из списка возможных ================================
    chance_of_enemy_birth = random.random()
    # ============================================= если шанс на создание противника подходит, то создаем ==============
    if 0.002 < chance_of_enemy_birth < min_chance_of_enemy_birth:
        entity = random.choice(entities)
        if entity == 0:
            x = WIDTH + 100
            y = random.randint(0, HEIGHT - ENTITY_HEIGHT)
            Asteroid(x, y, all_spites, enemy_sprites)
        elif entity == 1:
            x = WIDTH + 30
            y = random.randint(0, HEIGHT - ENTITY_HEIGHT)
            # ================================= специальный спрайт для проверки ========================================
            check = SpriteWithoutImage(0, y, WIDTH, ENTITY_HEIGHT)
            # проверка, есть ли на линии создание инопланетного корабля астероиды, чтобы не стрелять в них
            if check.check_collision(enemy_sprites):
                if check.check_collision(other_sprites):
                    AlienShip(x, y, all_spites, enemy_sprites)
            check.kill()
    elif chance_of_enemy_birth < 0.002:
        x = WIDTH + 100
        y = random.randint(0, HEIGHT - HP_ENTITY_HEIGHT)
        check = SpriteWithoutImage(0, y, WIDTH, HP_ENTITY_HEIGHT)
        if check.check_collision(enemy_sprites):
            HpEntity(x, y, all_spites, other_sprites)
        check.kill()


# =========================================== закрытие программы =======================================================
def terminate():
    pg.quit()
    sys.exit()


# ================================================ класс кнопки ========================================================


class Button(pg.sprite.Sprite):
    def __init__(self, x, y, w, h, color, buttons, fon, *group):
        super().__init__(*group)
        self.color = color
        self.image = pg.Surface([w, h])
        self.image.blit(fon.subsurface(pg.Rect((x, y), (w, h))), (0, 0))
        self.rect = pg.Rect(x, y, w, h)
        pg.draw.rect(self.image, pg.Color(self.color), (0, 0, w, h), border_radius=20, width=5)
        # ======================= добавить новоиспеченную кнопку в группу кнопок =======================================
        buttons.append(self)

    def get_pos(self, x, y):
        # ======================================== отслеживаем, не находится ли курсор в пределах кнопки ===============
        if self.rect.x <= x <= self.rect.x + self.rect.w:
            if self.rect.y <= y <= self.rect.y + self.rect.h:
                return True
            return False
        return False

    def change_color(self, change):
        # ================================ если курсор в пределах кнопки, меняем ее цвет ===============================
        if change:
            pg.draw.rect(self.image, pg.Color('green'), (0, 0, self.rect.w, self.rect.h), border_radius=20, width=5)
        else:
            pg.draw.rect(self.image, pg.Color(self.color), (0, 0, self.rect.w, self.rect.h),
                         border_radius=20, width=5)

    def set_title(self, title, color, font_size):
        # ========================================== надпись на кнопке =================================================
        font = pg.font.Font(None, font_size)
        title = font.render(title, True, pg.Color(color))
        title_rect = title.get_rect(center=(self.rect.w // 2, self.rect.h // 2))
        self.image.blit(title, title_rect)

    '''def action(self):
        self.kill()'''


# ==================================================== класс еффектов ==================================================
class Effect(pg.sprite.Sprite):
    def __init__(self, x, y, sheet, rows, columns, speed, *group):
        super().__init__(*group)
        # ==================================== фреймы для анимации =====================================================
        self.frames = []
        # номер текущего фрейма
        self.cur_frame = 0
        # текущая итерация
        self.iteration = 0
        self.sheet = sheet
        self.rows = rows
        self.columns = columns
        # на какой итерации обнавлять фрейм
        self.speed = speed
        self.count_of_frames = self.rows * self.columns - 1
        self.rect = pg.Rect(x, y, self.sheet.get_width() // self.columns,
                            self.sheet.get_height() // self.rows)
        self.rect.center = x, y
        for i in range(self.rows):
            for j in range(self.columns):
                frame = (self.rect.w * j, self.rect.h * i)
                self.frames.append(self.sheet.subsurface(pg.Rect(frame, self.rect.size)))
        self.image = self.frames[self.cur_frame]

    def update(self):
        self.iteration += 1
        if self.rect.right <= 0 or self.cur_frame == self.count_of_frames:
            self.kill()
        if self.iteration % self.speed == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(-PLAYER_SPEED, 0)


# ============================================ спрайт для проверки на занятую полосу ===================================
class SpriteWithoutImage(pg.sprite.Sprite):
    def __init__(self, x, y, w, h, *group):
        super().__init__(*group)
        self.rect = pg.Rect(x, y, w, h)
        self.mask = self.rect

    def check_collision(self, check_target):
        # ======================================= проверка на столкновение с другими спрайтами =========================
        if pg.sprite.spritecollide(self, check_target, False):
            return False
        return True


class Player(pg.sprite.Sprite):
    def __init__(self, x, y, *sprite_group):
        super().__init__(*sprite_group)
        self.image = pg.transform.scale(load_image('ship.png'), (100, 100))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.hp = HP
        self.iteration = 0
        self.mask = pg.mask.from_surface(self.image)

    def update(self):
        # ============================= проверка на столкновение с другими спрайтами ===================================
        for sprite in enemy_sprites:
            if pg.sprite.collide_mask(self, sprite):
                self.take_damage(sprite.damage)
                sprite.take_damage(100)
        for sprite in enemy_bullet_sprites:
            if pg.sprite.collide_mask(self, sprite):
                self.take_damage(sprite.damage)
                sprite.take_damage(100)
        for sprite in other_sprites:
            if pg.sprite.collide_mask(self, sprite):
                if self.hp < 3:
                    self.take_damage(sprite.damage)
                sprite.take_damage(100)
        for sprite in bullet_sprites:
            if sprite.iteration < 6:
                sprite.rect.x = self.rect.right - 5
                sprite.rect.centery = self.rect.centery

    def move(self, x, y):
        # ================================= движение ===================================================================
        # ==================================== текущий угол направления ================================================
        angle = atan2(y - self.rect.centery, x - self.rect.centerx)
        # ==================================================== расстояние от текузей позиции игрока до курсора =========
        dx = x - self.rect.centerx
        dy = y - self.rect.centery
        # ======================================= движение по прямой до позиции курсора ================================
        if abs(dx) >= PLAYER_STEP:
            self.rect.centerx += cos(angle) * PLAYER_STEP
        else:
            self.rect.centerx += cos(angle) * abs(dx)
        if abs(dy) >= PLAYER_STEP:
            self.rect.centery += sin(angle) * PLAYER_STEP
        else:
            self.rect.centery += sin(angle) * abs(dy)

    def get_pos(self):
        return self.rect

    def get_width(self):
        return self.rect.w

    def get_height(self):
        return self.rect.h

    def take_damage(self, damage):
        # ======================================= получение урона ======================================================
        self.hp -= damage
        if damage > 0:
            play_sound(take_damage_sound)
        if self.hp <= 0:
            Effect(self.rect.centerx, self.rect.centery, boom_image, 2, 4, 5, all_spites)
            self.kill()

    def create_player_bullet(self):
        # =================================== создание пули ============================================================
        if self.iteration == 15:
            Bullets(self.rect.right - 5, self.rect.centery, all_spites, bullet_sprites)
            play_sound(blaster_sound)
        self.iteration += 1
        if self.iteration == 16:
            self.iteration = 0


# ================================================= класс огня из двигателя игрока (да, звучит глупо) ==================
class Flame(pg.sprite.Sprite):
    def __init__(self, x, y, *sprite_group):
        super().__init__(*sprite_group)
        # тут я поленился делать анимацию, как в классе Effect =========================================================
        self.frames = ['flame1.png', 'flame2.png', 'flame3.png']
        self.cur_frame = -1
        self.image = pg.transform.scale(load_image(self.frames[self.cur_frame]), (40, 40))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x - self.rect.w, y + 30
        self.iteration = 0
        self.hp = 1

    def update(self):
        if self.iteration == 15:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = pg.transform.scale(load_image(self.frames[self.cur_frame]), (40, 40))
        self.iteration += 1
        if self.iteration == 16:
            self.iteration = 0

    def move(self):
        self.rect.center = player.rect.centerx - self.rect.w * 1.62, player.rect.centery

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.kill()


# ================================================ пули игрока =========================================================


class Bullets(pg.sprite.Sprite):
    def __init__(self, x, y, *group):
        super().__init__(*group)
        self.image = player_bullet_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.centery = y
        self.mask = pg.mask.from_surface(self.image)
        self.hp = 1
        self.iteration = 0

    def update(self):
        if self.rect.left >= WIDTH:
            self.kill()
        for sprite in enemy_sprites:
            if pg.sprite.collide_mask(self, sprite):
                self.take_damage(100)
                sprite.take_damage(1)
        if self.iteration == 5:
            # на пятой итерации пуля вылетает из пушки
            self.image = load_image('player_bullet.png')
            self.mask = pg.mask.from_surface(self.image)
            self.move()
        elif self.iteration > 5:
            # после пятой итерации пуля летит вперед
            self.move()
        self.iteration += 1

    def move(self):
        self.rect = self.rect.move(PLAYER_SPEED * 3, 0)

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.kill()


# ========================================= пули инопланетных кораблей =================================================
class AlienBullets(Bullets):
    def __init__(self, x, y, parent, *group):
        super().__init__(x, y, *group)
        self.rect.right = x
        self.image = alien_bullet_image
        self.parent = parent
        self.damage = 1

    def update(self):
        global player
        if self.rect.right <= 0:
            self.kill()
        if self.iteration == 5:
            self.image = pg.transform.scale(load_image('b.png'), (40, 30))
            self.mask = pg.mask.from_surface(self.image)
            self.move()
        elif self.iteration > 5:
            self.move()
        elif self.iteration < 5:
            self.rect.right = self.parent.rect.x - 1
        self.iteration += 1

    def move(self):
        self.rect = self.rect.move(-PLAYER_SPEED * 3, 0)


# ====================================== инопланетный корабль ==========================================================


class AlienShip(pg.sprite.Sprite):
    def __init__(self, x, y, *group):
        super().__init__(*group)
        self.image = pg.transform.scale(load_image('alien_ship.png'), ENTITY_SIZE)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.mask = pg.mask.from_surface(self.image)
        self.hp = ENEMY_HP
        self.iteration = 10
        self.damage = 1

    def update(self):
        if len(pg.sprite.spritecollide(self, enemy_sprites, False)) > 1:
            self.kill()
        elif self.rect.right <= 0:
            self.kill()
        else:
            self.move()
            self.create_alien_bullet()

    def move(self):
        self.rect = self.rect.move(-PLAYER_SPEED, 0)

    def create_alien_bullet(self):
        # ============================= создать пулю ===================================================================
        if self.iteration == 17:
            AlienBullets(self.rect.x - 1, self.rect.centery, self, all_spites, enemy_bullet_sprites)
        self.iteration += 1
        if self.iteration == 18:
            self.iteration = 0

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            update_score(50)
            Effect(self.rect.centerx, self.rect.centery, boom_image, 2, 4, 5, all_spites)
            play_sound(random.choice(boom_sounds))
            # создать осколки после смерти классом Particle
            particle_step_x = range(-20, 20)
            particle_step_y = range(-10, 10)
            [Particle(self.rect.centerx, self.rect.centery, random.choice(particle_step_x),
                      random.choice(particle_step_y), random.choice(alien_ship_particle_image),
                      1, all_spites) for i in range(15)]
            Particle(self.rect.centerx, self.rect.centery, -10, 1, score_particle_50, 0, all_spites)
            self.kill()


# ============================================= астероид ===============================================================


class Asteroid(pg.sprite.Sprite):
    def __init__(self, x, y, *group):
        super().__init__(*group)
        self.image = pg.transform.scale(load_image('asteroid.png'), ENTITY_SIZE)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.mask = pg.mask.from_surface(self.image)
        self.hp = ENEMY_HP
        self.damage = 1

    def update(self):
        if len(pg.sprite.spritecollide(self, enemy_sprites, False)) > 1:
            self.kill()
        elif self.rect.right <= 0:
            self.kill()
        else:
            self.rect = self.rect.move(-PLAYER_SPEED, 0)

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            update_score(20)
            Effect(self.rect.centerx, self.rect.centery, boom_image, 2, 4, 5, all_spites)
            play_sound(random.choice(boom_sounds))
            particle_step_x = range(-20, 20)
            particle_step_y = range(-10, 10)
            [Particle(self.rect.centerx, self.rect.centery, random.choice(particle_step_x),
                      random.choice(particle_step_y), random.choice(asteroid_particle_image), 1, all_spites) for i in range(15)]
            Particle(self.rect.centerx, self.rect.centery, -10, 1, score_particle_20, 0, all_spites)
            self.kill()


# ================================================ аптечка-сердечко ====================================================


class HpEntity(pg.sprite.Sprite):
    def __init__(self, x, y, *group):
        super().__init__(*group)
        self.image = hp_entity_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hp = 1
        self.damage = -1

    def update(self):
        if self.rect.right <= 0:
            self.kill()
        elif len(pg.sprite.spritecollide(self, enemy_sprites, False)) >= 1:
            self.kill()
        self.move()

    def move(self):
        self.rect = self.rect.move(-PLAYER_SPEED, 0)

    def create_particles(self):
        particle_step_x = range(-20, 20)
        particle_step_y = range(-10, 10)
        [Particle(self.rect.centerx, self.rect.centery, random.choice(particle_step_x),
                     random.choice(particle_step_y), hp_particle_image, 0, all_spites) for i in range(10)]

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.create_particles()
            Effect(self.rect.centerx, self.rect.centery, fog_image, 6, 5, 5, all_spites)
            play_sound(healing_sound)
            self.kill()


# ============================================ отображение очков =======================================================


class Points:
    def __init__(self, font_size, color):
        self.font = pg.font.Font(None, font_size)
        self.color = color

    def update(self, title):
        title = self.font.render(title, True, pg.Color(self.color))
        title_rect = HP_DISPLAY_POS[0] * HP + HP_DISPLAY_WIDTH * HP, HP_DISPLAY_POS[1]
        screen.blit(title, title_rect)
        for i in range(player.hp):
            screen.blit(hp_display_image, (HP_DISPLAY_POS[0] + i * HP_DISPLAY_WIDTH, HP_DISPLAY_POS[1]))


# ==================================================== частицы =========================================================


class Particle(pg.sprite.Sprite):
    def __init__(self, x, y, dx, dy, image, rotation=0, *group):
        super().__init__(*group)
        self.rotation = rotation
        # ====================== вращать, если rotation True ===========================================================
        if self.rotation:
            image = pg.transform.rotate(image, random.randint(0, 360))
            # =================================== угол вращения ========================================================
            self.angle = random.randint(-30, 30)
            # =========================================== на сколько градусов увеличивать угол вращения ================
            self.step_angle = abs(self.angle)
        self.image = self.image_original = image
        self.rect = self.image.get_rect()
        # ======================================= рандомное направление движения частицы ===============================
        self.velocity_x, self.velocity_y = dx, dy
        self.rect.x = x
        self.rect.y = y
        # ======================================== скорость движения ===================================================
        self.step = PLAYER_SPEED // 5

    def update(self):
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        if self.rect.right <= 0 or self.rect.bottom <= 0 or self.rect.top >= HEIGHT:
            self.kill()
        if self.velocity_x > -PLAYER_SPEED:
            self.velocity_x -= 1
        if self.rotation:
            self.rotate()

    def rotate(self):
        self.image = pg.transform.rotate(self.image_original, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        if self.angle > 0:
            self.angle += self.step_angle
        else:
            self.angle -= self.step_angle


# ==================================================== класс результатов игры ==========================================


class Scoreboard(pg.sprite.Sprite):
    def __init__(self, x, y, w, h, *group):
        super().__init__(*group)
        self.image = pg.Surface([w, h])
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = x, y
        pg.draw.rect(self.image, (255, 255, 255), (0, 0, w, h), width=2)

    def draw_score(self, points):
        font = pg.font.Font(None, 100)
        score = font.render(str(points), True, (255, 255, 255))
        score_rect = score.get_rect(center=(self.rect.w // 2, self.rect.h // 2 - 20))
        title = font.render('Your score:', True, (0, 255, 0))
        title_rect = title.get_rect(center=(self.rect.w // 2, 70))
        self.image.blit(score, score_rect)
        self.image.blit(title, title_rect)


# ================================ здесь у меня все картинки и некоторые константы =====================================
score = 0
entity_pos = []
next_level = 1000
min_chance_of_enemy_birth = 0.02
# ================================================= все группы спрайтов ================================================
all_spites = pg.sprite.Group()
player_sprites = pg.sprite.Group()
enemy_sprites = pg.sprite.Group()
bullet_sprites = pg.sprite.Group()
enemy_bullet_sprites = pg.sprite.Group()
other_sprites = pg.sprite.Group()
# =================================================== все картинки =====================================================
asteroid_image = pg.transform.scale(load_image('asteroid.png'), ENTITY_SIZE)
score_particle_20 = pg.Surface([100, 50])
score_particle_50 = pg.Surface([100, 50])
font = pg.font.Font(None, 40)
title_20 = font.render('+20', True, pg.Color('green'))
title_rect_20 = pg.Rect(0, 0, 100, 50)
title_50 = font.render('+50', True, pg.Color('red'))
title_rect_50 = pg.Rect(0, 0, 100, 50)
score_particle_20.blit(title_20, title_rect_20)
score_particle_20.set_colorkey(score_particle_20.get_at((0, 0)))
score_particle_50.blit(title_50, title_rect_50)
score_particle_50.set_colorkey(score_particle_50.get_at((0, 0)))
alien_ship_image = pg.transform.scale(load_image('alien_ship.png'), ENTITY_SIZE)
player_bullet_image = load_image('player_bullet_flame.png')
alien_bullet_image = pg.transform.scale(load_image('a.png'), ALIEN_BULLET_SIZE)
boom_image = pg.transform.scale(load_image('boom.png'), BOOM_SIZE)
fog_image = pg.transform.scale(load_image('fog.png'), FOG_SIZE)
hp_entity_image = pg.transform.scale(load_image('hp.png'), HP_ENTITY_SIZE)
hp_particle_image = pg.transform.scale(load_image('hp.png'), HP_PARTICLE_SIZE)
hp_display_image = pg.transform.scale(load_image('hp.png'), HP_DISPLAY_SIZE)
asteroid_particle_image = [load_image('asteroid_particle.png')]
alien_ship_particle_image = [load_image('alien_ship_particle1.png'), load_image('alien_ship_particle2.png')]
logo_image = load_image('logo.png')
# ==================================количество очков в процессе игры ===================================================
hp_and_score = Points(50, 'white')
cur_level = LEVEL
running = True
# ==================================== эти переменные нужны для движущиегося фона =====================================
fon_x = 0
fon_x1 = 0

fon_left = 0
fon_right = 0
# ======================================================================================================================
# ========================================================== сам фон ===================================================
fon = pg.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
screen.blit(fon, (0, 0))
# пламя от космического корабля игрока
flame = None
player_start = 100, HEIGHT // 2 - 50
player = Player(*player_start, all_spites, player_sprites)
# позиция игрока
player_pos = 0, 0

entities = [0, 1]
# ======================================================================================================================
# ================================ здесь все настраивается для игры ====================================================


def start_game():
    global all_spites, player_sprites, enemy_sprites, bullet_sprites, other_sprites, score, next_level
    global player_start, flame, player, running, fon_x, fon_x1, player_pos, min_chance_of_enemy_birth
    all_spites = pg.sprite.Group()
    player_sprites = pg.sprite.Group()
    enemy_sprites = pg.sprite.Group()
    bullet_sprites = pg.sprite.Group()
    other_sprites = pg.sprite.Group()

    player_pos = 0, 0

    screen.blit(fon, (0, 0))

    player_start = 100, HEIGHT // 2 - 50
    flame = None
    player = Player(*player_start, all_spites, player_sprites)
    fon_x = 0
    fon_x1 = 0
    score = 0
    min_chance_of_enemy_birth = 0.02
    next_level = 1000
    running = True
    # ======================================== перехрд в меню =========================================================
    menu()


def game_cycle():
    global player_pos, flame, cur_level, running
    flame = Flame(*player_start, all_spites, player_sprites)
    pg.mouse.set_visible(False)
    restart_buttons = []
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            if event.type == pg.MOUSEMOTION:
                # ==================================== движение игрока =================================================
                player_pos = event.pos
                # ====================================== если курсор в пределах кнопки Menu, меняем ее цвет ============
                if player.hp < 0:
                    for button in restart_buttons:
                        if button.get_pos(*event.pos):
                            button.change_color(True)
                        else:
                            button.change_color(False)
            if event.type == pg.MOUSEBUTTONDOWN:
                # ================================ если нажали на кнопку Menu, то перекидывает игрока в меню ===========
                for button in restart_buttons:
                    if button.get_pos(*event.pos):
                        # ==================================== удаляем кнопку Menu и отображение результата игры =======
                        for sprite in restart_buttons:
                            sprite.kill()
                        score_board.kill()
                        change_music(0, -1)
                        running = False
        screen.fill(pg.Color('black'))
        # ======================================= двигаем фон ==========================================================
        moving_fon()
        # ========================================= обновляем счет очков ===============================================
        hp_and_score.update(str(score))
        # ======================================= пока игрок жив, то делаем игровые события ============================
        if player.hp > 0:
            player.move(*player_pos)
            flame.move()
            player.create_player_bullet()
            pg.draw.circle(screen, pg.Color('red'), player_pos, 10, width=1)
            create_entity()
        # ======================================== иначе, отбражаем результаты игры и удаляем все спрайты ==============
        elif player.hp == 0:
            flame.kill()
            change_music(2, 1)
            for sprite in enemy_bullet_sprites:
                sprite.kill()
            for sprite in enemy_sprites:
                sprite.kill()
            for sprite in other_sprites:
                sprite.kill()
            pg.mouse.set_visible(True)
            score_board = Scoreboard(WIDTH // 2, HEIGHT // 2, 500, 400, all_spites)
            score_board.draw_score(score)
            restart_button = Button(5, 250, 250, 100, 'white', restart_buttons, score_board.image, all_spites)
            restart_button.rect.center = WIDTH // 2, HEIGHT // 2 + 100
            restart_button.set_title('Menu', 'white', 75)
            player.hp -= 1
        all_spites.update()
        all_spites.draw(screen)
        pg.display.flip()
        clock.tick(FPS)
    start_game()


# ================================================== здесь игра начинается =============================================
show_intro()