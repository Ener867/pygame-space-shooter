import pygame
import random
import os

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Godzilla vs Kong")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

def load_image(name, size=None):
    try:
        img = pygame.image.load(os.path.join("assets", name)) 
        if size:
            img = pygame.transform.scale(img, size)#
        return img
    except:
        return None

background_img = load_image("fondo.jpeg", (WIDTH, HEIGHT))
rocket_img = load_image("godzilla.png", (70, 100))
enemy_img = load_image("kong.webp", (60, 60))  
projectile_img = load_image("corazon.webp", (20, 30)) 
heart_img = load_image("heart.webp", (30, 30)) or None  
bonus_img = load_image("mothra.png", (30, 30)) or None  

class Rocket:
    def __init__(self):
        self.width = 70
        self.height = 100
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - self.height - 20
        self.speed = 7
        self.invincible = False
        self.invincible_timer = 0
        
    def draw(self):
        if rocket_img:
            screen.blit(rocket_img, (self.x, self.y))
        else:
            color = BLUE if self.invincible else WHITE
            pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
            
    def move(self, direction):
        if direction == "left" and self.x > 0:
            self.x -= self.speed
        if direction == "right" and self.x < WIDTH - self.width:
            self.x += self.speed
            
    def update(self):
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

class Projectile:
    def __init__(self, x, y):
        self.width = 20
        self.height = 30
        self.x = x
        self.y = y
        self.speed = 10
        
    def draw(self):
        if projectile_img:
            screen.blit(projectile_img, (self.x, self.y))
        else:
            pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
            
    def move(self):
        self.y -= self.speed
        return self.y < 0

class Enemy:
    def __init__(self, speed=1):
        self.width = 60
        self.height = 60
        self.x = random.randint(0, WIDTH - self.width)
        self.y = random.randint(-150, -40)
        self.speed = speed
        
    def draw(self):
        if enemy_img:
            screen.blit(enemy_img, (self.x, self.y))
        else:
            pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))
            
    def move(self):
        self.y += self.speed
        return self.y > HEIGHT

class Bonus:
    def __init__(self):
        self.width = 30
        self.height = 30
        self.x = random.randint(0, WIDTH - self.width)
        self.y = random.randint(-100, -40)
        self.speed = 2
        self.active = False
        self.timer = 0
        
    def draw(self):
        if bonus_img:
            screen.blit(bonus_img, (self.x, self.y))
        else:
            pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))
            
    def move(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.reset()
            
    def reset(self):
        self.x = random.randint(0, WIDTH - self.width)
        self.y = random.randint(-100, -40)
        self.active = False

def main():
    clock = pygame.time.Clock()
    rocket = Rocket()
    projectiles = []
    enemies = []
    bonuses = [Bonus() for _ in range(2)]  # Dos bonus en pantalla
    score = 0
    enemy_spawn_timer = 0
    bonus_spawn_timer = 0
    lives = 3
    game_over = False
    level = 1
    enemy_speed = 1
    spawn_rate = 50

    font = pygame.font.SysFont(None, 36)
    big_font = pygame.font.SysFont(None, 72)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    projectiles.append(Projectile(rocket.x + rocket.width // 2 - 10, rocket.y))
                if event.key == pygame.K_r and game_over:
                    lives = 3
                    score = 0
                    level = 1
                    enemy_speed = 1
                    spawn_rate = 50
                    enemies.clear()
                    projectiles.clear()
                    for bonus in bonuses:
                        bonus.reset()
                    game_over = False
        
        if not game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                rocket.move("left")
            if keys[pygame.K_RIGHT]:
                rocket.move("right")
            
            rocket.update()

            for proj in projectiles[:]:
                if proj.move():
                    projectiles.remove(proj)

            if score >= level * 500:
                level += 1
                enemy_speed += 0.5
                spawn_rate = max(20, spawn_rate - 5) 

            enemy_spawn_timer += 1
            if enemy_spawn_timer >= spawn_rate:
                enemies.append(Enemy(enemy_speed))
                enemy_spawn_timer = 0
            
            bonus_spawn_timer += 1
            if bonus_spawn_timer >= 300:  
                for bonus in bonuses:
                    if not bonus.active:
                        bonus.active = True
                        bonus.reset()
                        break
                bonus_spawn_timer = 0
 
            for enemy in enemies[:]:
                if enemy.move():
                    enemies.remove(enemy)

                if (not rocket.invincible and 
                    rocket.x < enemy.x + enemy.width and
                    rocket.x + rocket.width > enemy.x and
                    rocket.y < enemy.y + enemy.height and
                    rocket.y + rocket.height > enemy.y):
                    
                    enemies.remove(enemy)
                    lives -= 1
                    rocket.invincible = True
                    rocket.invincible_timer = 60 
                    if lives <= 0:
                        game_over = True

            for bonus in bonuses:
                if bonus.active:
                    bonus.move()
                    
                    if (rocket.x < bonus.x + bonus.width and
                        rocket.x + rocket.width > bonus.x and
                        rocket.y < bonus.y + bonus.height and
                        rocket.y + rocket.height > bonus.y):
                        
                        bonus.reset()
                        lives += 1  

            for proj in projectiles[:]:
                for enemy in enemies[:]:
                    if (proj.x < enemy.x + enemy.width and
                        proj.x + proj.width > enemy.x and
                        proj.y < enemy.y + enemy.height and
                        proj.y + proj.height > enemy.y):
                        
                        if proj in projectiles:
                            projectiles.remove(proj)
                        if enemy in enemies:
                            enemies.remove(enemy)
                        score += 10

                        if score % 300 == 0:
                            for bonus in bonuses:
                                if not bonus.active:
                                    bonus.active = True
                                    bonus.reset()
                                    break
                        break

        if background_img:
            screen.blit(background_img, (0, 0))
        else:
            screen.fill(BLACK)
        
        rocket.draw()
        for proj in projectiles:
            proj.draw()
        for enemy in enemies:
            enemy.draw()
        for bonus in bonuses:
            if bonus.active:
                bonus.draw()

        score_text = font.render(f"Puntuación: {score}", True, WHITE)
        level_text = font.render(f"Nivel: {level}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 50))
        
        if heart_img:
            for i in range(lives):
                screen.blit(heart_img, (WIDTH - 40 - i * 35, 10))
        else:
            lives_text = font.render(f"Vidas: {lives}", True, WHITE)
            screen.blit(lives_text, (WIDTH - 150, 10))

        if game_over:
            over_text = big_font.render("GAME OVER", True, RED)
            restart_text = font.render("Presiona R para reiniciar", True, WHITE)
            screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2 - 50))
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 20))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
