import pygame
import random
import math
import sys

# Inicialización de Pygame y de los sonidos
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("Sonido.mp3")
pygame.mixer.music.play(-1)
muerte_zombie_sound = pygame.mixer.Sound("sonido muerte zombie.mp3")
muerte_zombie_sound.set_volume(0.5)
grito_perder_sound = pygame.mixer.Sound("gameover.mp3")
grito_perder_sound.set_volume(0.5)

# Configuración de pantalla y reloj
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("EndZone")
clock = pygame.time.Clock()

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PINK = (255, 105, 180)        
LIGHT_PINK = (255, 182, 193)  
GRAY = (100, 100, 100)
CYAN = (0, 255, 255)
GREEN = (0, 200, 0)
DARK_RED = (150, 0, 0)


# Tipografía utilizada
button_font = pygame.font.SysFont("Arial", 25)
info_font = pygame.font.SysFont("Arial", 20)

# Función para cargar imágenes desde una ruta y redimensionarlas
def cargar_imagen_ruta(ruta, ancho_objetivo, alto_objetivo):
    imagen = pygame.image.load(ruta).convert_alpha()
    original_ancho, original_alto = imagen.get_size()
    ratio = min(ancho_objetivo / original_ancho, alto_objetivo / original_alto)
    nuevo_tamano = (int(original_ancho * ratio), int(original_alto * ratio))
    imagen_redimensionada = pygame.transform.smoothscale(imagen, nuevo_tamano)
    return imagen_redimensionada

# Carga de imágenes para personajes, enemigos, proyectiles, etc.
personaje_img = cargar_imagen_ruta("Personaje.png", 150, 150)
enemigo_imgs = [cargar_imagen_ruta(f"enemigo{i}.png", 80, 80) for i in range(1, 15)]  
#personaje2_img = cargar_imagen_ruta("Personaje2.png", 125, 125)
#personaje3_img = cargar_imagen_ruta("Personaje3.png", 140, 140)
proyectil_img = cargar_imagen_ruta("Proyectil.png", 20, 20)
proyectil_jefe_img = cargar_imagen_ruta("ProyectilZombie.png", 30, 30)
#enemigo_grande_img1 = cargar_imagen_ruta("enemigo_grande1.png", 150, 150)
#enemigo_grande_img2 = cargar_imagen_ruta("enemigo_grande2.png", 150, 150)

# Enemigos grandes en las esquinas
#menu_enemigos = [
    #{'x': 50, 'y': 50, 'dx': random.choice([-0.7, 0.7]), 'dy': random.choice([-0.7, 0.7]), 'img': enemigo_grande_img1},
    #{'x': WIDTH - 50, 'y': 50, 'dx': random.choice([-0.7, 0.7]), 'dy': random.choice([-0.7, 0.7]), 'img': enemigo_grande_img2},
    #{'x': 50, 'y': HEIGHT - 50, 'dx': random.choice([-0.7, 0.7]), 'dy': random.choice([-0.7, 0.7]), 'img': enemigo_grande_img1},
    #{'x': WIDTH - 50, 'y': HEIGHT - 50, 'dx': random.choice([-0.7, 0.7]), 'dy': random.choice([-0.7, 0.7]), 'img': enemigo_grande_img2}
#]


jefe_imgs = {
    1: cargar_imagen_ruta("JefeFinal1.png", 100, 100),
    2: cargar_imagen_ruta("JefeFinal2.png", 130, 130),
    3: cargar_imagen_ruta("JefeFinal3.png", 150, 150)
}

# Nueva imagen de mancha de sangre
blood_stain_img = cargar_imagen_ruta("Sangre.png", 50, 50) # Tamaño ajustable

show_menu = True #variables de estado
run_game = False
show_instructions = False

# Logotipo para menú
logotipo_img = cargar_imagen_ruta("Logotipo.png", 400, 400)

# Crea una lista de partículas (brasas) que caen lentamente en pantalla
menu_brasas = [{'x': random.randint(0, WIDTH), 'y': random.randint(0, HEIGHT), 'speed': random.uniform(0.2, 0.6)} for _ in range(60)]

# Dibuja un botón con texto, colores y acción cuando se hace clic
def draw_button(text, x, y, w, h, base_color, hover_color, action=None):
    mouse = pygame.mouse.get_pos()  # Obtiene posición del mouse
    click = pygame.mouse.get_pressed()  # Detecta clic
    rect = pygame.Rect(x, y, w, h)  # Crea rectángulo del botón
    is_hovered = rect.collidepoint(mouse)  # Verifica si el mouse está encima

    # Dibuja contorno blanco y relleno según si el mouse está encima
    pygame.draw.rect(screen, WHITE, rect, border_radius=10)
    inner_rect = rect.inflate(-4, -4)
    pygame.draw.rect(screen, hover_color if is_hovered else base_color, inner_rect, border_radius=8)

    # Dibuja el texto centrado
    text_surf = button_font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

    # Si se hace clic en el botón, ejecuta la acción asociada
    if is_hovered and click[0] == 1 and action:
        pygame.time.wait(150)  # Espera para evitar múltiples clics
        action()

# Dibuja una barra de salud con etiqueta (arriba o abajo)
def draw_health_bar(x, y, width, height, current_health, max_health, border_color, fill_color, back_color, label="", label_pos="above"):
    
    # Si hay texto y debe ir arriba
    if label and label_pos == "above":
        label_surf = info_font.render(label, True, WHITE)
        screen.blit(label_surf, (x, y - label_surf.get_height() - 5)) 

    # Dibuja fondo de la barra
    back_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, back_color, back_rect)

    # Calcula el ancho de la barra de vida según salud actual
    fill_width = int(width * (current_health / max_health))
    fill_rect = pygame.Rect(x, y, fill_width, height)
    pygame.draw.rect(screen, fill_color, fill_rect)

    # Dibuja el borde de la barra
    pygame.draw.rect(screen, border_color, back_rect, 2)
    
    # Si hay texto y debe ir debajo
    if label and label_pos == "below":
        label_surf = info_font.render(label, True, WHITE)
        screen.blit(label_surf, (x, y + height + 5)) 

# Dibuja las brasas  en movimiento
def draw_brasas(brazas):
    for b in brazas:
        b['y'] += b['speed']
        if b['y'] > HEIGHT:  # Si se salen por abajo, reaparecen arriba
            b['y'] = 0
            b['x'] = random.randint(0, WIDTH)
        pygame.draw.circle(screen, RED, (int(b['x']), int(b['y'])), 2)

# Muestra una pantalla de información como la historia o el mensaje de muerte
def mostrar_pantalla_info(titulo, descripcion, volver_a_menu=False):
    esperando = True

    # Fuentes para título, descripción e instrucciones
    titulo_font = pygame.font.SysFont("Arial Black", 36)
    descripcion_font = pygame.font.SysFont("Arial", 24)
    instruccion_font = pygame.font.SysFont("Arial", 20)

    while esperando:
        screen.fill(BLACK)
        draw_brasas(menu_brasas)  # Fondo animado

        # Panel con transparencia
        panel_rect = pygame.Surface((600, 300), pygame.SRCALPHA)
        panel_rect.fill((0, 0, 0, 180))  
        screen.blit(panel_rect, (WIDTH // 2 - 300, HEIGHT // 2 - 150))

        # Título centrado, rojo si es de muerte
        titulo_surf = titulo_font.render(titulo, True, PINK if "¡Has muerto!" not in titulo else RED)
        screen.blit(titulo_surf, (WIDTH // 2 - titulo_surf.get_width() // 2, HEIGHT // 2 - 130))

        # Muestra línea por línea la descripción
        lineas = descripcion.split("\n")
        for i, linea in enumerate(lineas):
            texto_surf = descripcion_font.render(linea, True, WHITE)
            screen.blit(texto_surf, (WIDTH // 2 - texto_surf.get_width() // 2, HEIGHT // 2 - 60 + i * 35))

        # Instrucción para continuar
        instruccion_text = "Presiona ENTER para continuar..."
        if volver_a_menu:
            instruccion_text = "Presiona ENTER para volver al menú..."
        instruccion = instruccion_font.render(instruccion_text, True, CYAN)
        screen.blit(instruccion, (WIDTH // 2 - instruccion.get_width() // 2, HEIGHT // 2 + 100))

        pygame.display.flip()

        # Eventos: salir o continuar con ENTER
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                esperando = False

 # En esta parte agregué la historia que cambia según el nivel con la función mostrar_historia().
# También mejoré el fondo agregando partículas tipo brasas para dar más ambientación.
# Añadí habilidades como doble tiro, velocidad y ralentización, que se activan por nivel.
# Cambié el sistema de disparo para que funcione con el mouse y tenga múltiples proyectiles si hay habilidad activa.
# Además empecé a preparar la lógica para los jefes, aunque aún no está activa.
               
# Muestra una historia diferente dependiendo del nivel
def mostrar_historia(nivel):
    historias = {
        1: ("APARICIONES INEXPLICABLES",
            "Criaturas horribles comenzaron a surgir desde las sombras.\nNadie sabe de dónde vienen ni cómo detenerlas..."),
        2: ("TIERRAS DEVASTADAS",
            "Los monstruos arrasaron pueblos y ciudades.\nSolo unos pocos sobrevivientes se esconden en ruinas."),
        3: ("LA BATALLA FINAL",
            "Eres la última esperanza.\nElimina a las criaturas antes de que consuman todo lo que queda.")
    }

    if nivel in historias:
        titulo, descripcion = historias[nivel]
        mostrar_pantalla_info(titulo, descripcion)

def game_loop():
    global run_game, show_menu

    # Partículas tipo brasas que se mueven en el fondo durante el juego
    particles = [{'x': random.randint(0, WIDTH), 'y': random.randint(0, HEIGHT), 'radius': random.randint(1, 3),
                  'speed': random.uniform(0.2, 0.6)} for _ in range(120)]

    # Posición inicial del jugador (centro de pantalla)
    player_pos = [WIDTH // 2, HEIGHT // 2]
    player_radius = 25  # Para calcular colisiones

    # Estadísticas iniciales del jugador
    base_speed = 4
    player_speed = base_speed
    player_health = 100
    player_max_health = 100
    player_xp = 0
    player_level = 1
    xp_to_next = 50

    # Nivel y habilidades
    nivel_actual = 1
    max_nivel = 3
    habilidad_actual = 1
    habilidad_nombres = {1: "Doble Tiro", 2: "Relentizador", 3: "Velocidad"}

    # Control de habilidad de relentizar
    ralentizar_enemigos = False
    ralentizador_fin = 0

    # Lista de proyectiles del jugador
    projectiles = []
    projectile_speed = 7
    shoot_delay = 500
    last_shot_time = pygame.time.get_ticks()

    # Enemigos normales
    enemies = []
    enemy_spawn_delay = 1500
    last_enemy_spawn = pygame.time.get_ticks()
    enemy_base_speed = 1.5
    enemy_speed = enemy_base_speed

    # Jefe del nivel
    jefe_activo = False
    jefe_pos = None
    jefe_vida = 0
    jefe_max_vida = 0
    jefe_danio = 10
    jefe_speed = 2
    jefe_proyectiles = []
    jefe_disparo_delay = 1000
    ultimo_disparo_jefe = 0

    # Lista de manchas de sangre que se desvanecen con el tiempo
    blood_stains = []

    # Mostrar historia del primer nivel
    mostrar_historia(nivel_actual)

    running = True

    while running:
        dt = clock.tick(60)  # Limita a 60 FPS
        screen.fill((15, 15, 15))  # Fondo negro oscuro

        # Dibuja brasas animadas
        for p in particles:
            pygame.draw.circle(screen, RED, (int(p['x']), int(p['y'])), p['radius'])
            p['y'] -= p['speed']
            if p['y'] < 0:  # Si sale de la pantalla, reaparece abajo
                p['x'] = random.randint(0, WIDTH)
                p['y'] = HEIGHT + random.randint(0, 100)
                p['speed'] = random.uniform(0.2, 0.6)

        # Dibuja las manchas de sangre con transparencia
        for stain in blood_stains[:]:
            stain_surface = blood_stain_img.copy()
            stain_surface.set_alpha(stain['alpha'])  # Aplica opacidad
            screen.blit(stain_surface, (stain['x'] - stain_surface.get_width() // 2,
                                        stain['y'] - stain_surface.get_height() // 2))
            stain['alpha'] -= 1  # Se va desvaneciendo
            if stain['alpha'] <= 0:
                blood_stains.remove(stain)

        # Eventos del sistema: salir del juego
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Movimiento del jugador con teclas W, A, S, D
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: player_pos[1] -= player_speed
        if keys[pygame.K_s]: player_pos[1] += player_speed
        if keys[pygame.K_a]: player_pos[0] -= player_speed
        if keys[pygame.K_d]: player_pos[0] += player_speed

        # Limita que el jugador no se salga de los bordes de la pantalla
        player_pos[0] = max(player_radius, min(player_pos[0], WIDTH - player_radius))
        player_pos[1] = max(player_radius, min(player_pos[1], HEIGHT - player_radius))

        # Tiempo actual para controlar disparos, enemigos, etc.
        now = pygame.time.get_ticks()

                # Disparar proyectiles automáticamente (cada shoot_delay milisegundos)
        if now - last_shot_time >= shoot_delay:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx = mouse_x - player_pos[0]
            dy = mouse_y - player_pos[1]
            dist = math.hypot(dx, dy)  # Calcula distancia entre jugador y mouse

            if dist != 0:  # Normaliza dirección del disparo
                dx /= dist
                dy /= dist

            # Disparo principal
            projectiles.append({'x': player_pos[0], 'y': player_pos[1], 'dx': dx, 'dy': dy})

            # Si tiene la habilidad de "Doble Tiro", dispara 2 proyectiles extra en ángulo
            if habilidad_actual == 1:
                offset = math.pi / 12  # Ángulo de separación
                cos_off = math.cos(offset)
                sin_off = math.sin(offset)

                # Crea dos disparos en dirección desviada a izquierda y derecha
                dx1, dy1 = dx * cos_off - dy * sin_off, dx * sin_off + dy * cos_off
                dx2, dy2 = dx * cos_off + dy * sin_off, -dx * sin_off + dy * cos_off

                projectiles.append({'x': player_pos[0], 'y': player_pos[1], 'dx': dx1, 'dy': dy1})
                projectiles.append({'x': player_pos[0], 'y': player_pos[1], 'dx': dx2, 'dy': dy2})

            last_shot_time = now  # Reinicia el temporizador del disparo

        # Movimiento de proyectiles en pantalla
        for p in projectiles[:]:
            p['x'] += p['dx'] * projectile_speed
            p['y'] += p['dy'] * projectile_speed

            # Si se sale de pantalla, eliminarlo
            if not (0 <= p['x'] <= WIDTH and 0 <= p['y'] <= HEIGHT):
                projectiles.remove(p)

        # Si se acaba el efecto de ralentizar, restablece la velocidad
        if ralentizar_enemigos and now > ralentizador_fin:
            ralentizar_enemigos = False
            enemy_speed = enemy_base_speed

        # Spawnea un nuevo enemigo si no hay jefe activo y ha pasado el tiempo
        if not jefe_activo and now - last_enemy_spawn >= enemy_spawn_delay:
            side = random.choice(['top', 'bottom', 'left', 'right'])  # Elige desde qué borde aparecerá

            # Posición inicial según el lado
            if side == 'top':
                x, y = random.randint(0, WIDTH), 0
            elif side == 'bottom':
                x, y = random.randint(0, WIDTH), HEIGHT
            elif side == 'left':
                x, y = 0, random.randint(0, HEIGHT)
            else:
                x, y = WIDTH, random.randint(0, HEIGHT)

            # Escoge un tipo aleatorio de enemigo
            tipo = random.randint(0, len(enemigo_imgs) - 1)

            # Agrega enemigo a la lista
            enemies.append({'x': x, 'y': y, 'speed': enemy_speed, 'tipo': tipo})
            last_enemy_spawn = now  # Actualiza último tiempo de aparición

            # Movimiento de enemigos hacia el jugador
        for enemy in enemies[:]:
            dx = player_pos[0] - enemy['x']
            dy = player_pos[1] - enemy['y']
            dist = math.hypot(dx, dy)
            if dist != 0:
                dx /= dist
                dy /= dist
            enemy['x'] += dx * enemy['speed']
            enemy['y'] += dy * enemy['speed']

        # Colisiones entre enemigos y jugador / proyectiles
        for enemy in enemies[:]:

            # Si un enemigo está cerca del jugador, le quita salud
            if math.hypot(enemy['x'] - player_pos[0], enemy['y'] - player_pos[1]) < 40:
                player_health -= 1

            # Detecta si un proyectil impacta al enemigo
            for p in projectiles[:]:
                if math.hypot(enemy['x'] - p['x'], enemy['y'] - p['y']) < 30:
                    if enemy in enemies:
                        # Añade una mancha de sangre
                        blood_stains.append({'x': enemy['x'], 'y': enemy['y'], 'alpha': 255})

                        # Sonido de muerte del enemigo
                        muerte_zombie_sound.play()
                        # Cuando un enemigo es alcanzado por un proyectil:
                        enemies.remove(enemy)  # Elimina al enemigo impactado de la lista de enemigos
                        projectiles.remove(p)  # Elimina el proyectil que impactó para que no siga activo
                        player_xp += 10        # Incrementa la experiencia del jugador

                         # Comprobar si el jugador ha subido de nivel
                        if player_xp >= xp_to_next:
                            player_level += 1       # Aumenta el nivel del jugador
                            player_xp = 0           # Reinicia la experiencia acumulada
                            xp_to_next += 25        # Incrementa la experiencia necesaria para el siguiente nivel
                        
                            # Según el nivel y nivel_actual, activa al jefe y configura sus atributos
                            if player_level == 2 and nivel_actual == 1:
                                jefe_activo = True
                                jefe_proyectiles.clear()  # Limpia proyectiles previos del jefe
                                jefe_pos = [random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100)]  # Posición aleatoria inicial del jefe
                                jefe_vida = jefe_max_vida = 8
                                jefe_speed = 2
                                jefe_danio = 10
                                jefe_disparo_delay = 1200
                                enemies.clear()  # Limpia enemigos normales al aparecer jefe

                            elif player_level == 3 and nivel_actual == 2:# Configuración similar para jefe en nivel 2 con dificultad aumentada
                                jefe_activo = True
                                jefe_proyectiles.clear()
                                jefe_pos = [random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100)]
                                jefe_vida = jefe_max_vida = 15
                                jefe_speed = 3
                                jefe_danio = 15
                                jefe_disparo_delay = 800
                                enemies.clear()
                             
                            if player_level == 4 and nivel_actual == 3: # Configuración para jefe en nivel 3 con parámetros aún más agresivos
                                jefe_activo = True
                                jefe_proyectiles.clear()
                                jefe_pos = [random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100)]
                                jefe_vida = jefe_max_vida = 15 
                                jefe_speed = 3 
                                jefe_danio = 15 
                                jefe_disparo_delay = 600 
                                enemies.clear() 
                        
                            # Actualización de la habilidad actual basada en nivel del jugador
                        if player_level == 2 and habilidad_actual < 2:
                            habilidad_actual = 2
                        elif player_level >= 3 and habilidad_actual < 3:
                            habilidad_actual = 3

        # Movimiento del jefe hacia la posición del jugador
        if jefe_activo:
            dx = player_pos[0] - jefe_pos[0]
            dy = player_pos[1] - jefe_pos[1]
            dist = math.hypot(dx, dy)
            if dist != 0:
                dx /= dist  # Normalizar vector dirección para mantener velocidad constante
                dy /= dist
            jefe_pos[0] += dx * jefe_speed
            jefe_pos[1] += dy * jefe_speed

            if now - ultimo_disparo_jefe >= jefe_disparo_delay:# Control del disparo del jefe, respetando delay entre disparos
                jdx = player_pos[0] - jefe_pos[0]
                jdy = player_pos[1] - jefe_pos[1]
                dist = math.hypot(jdx, jdy)
                if dist != 0:
                    jdx /= dist
                    jdy /= dist
                jefe_proyectiles.append({'x': jefe_pos[0], 'y': jefe_pos[1], 'dx': jdx, 'dy': jdy})# Agregar un nuevo proyectil que va hacia el jugador
                ultimo_disparo_jefe = now

               # Actualizar la posición de los proyectiles del jefe y manejar colisiones
            for j in jefe_proyectiles[:]:  # Iterar sobre copia para poder modificar la lista
                j['x'] += j['dx'] * 5  # Mover proyectil en X
                j['y'] += j['dy'] * 5  # Mover proyectil en Y
                # Si el proyectil sale de la pantalla, eliminarlo
                if not (0 <= j['x'] <= WIDTH and 0 <= j['y'] <= HEIGHT):
                    jefe_proyectiles.remove(j)
                # Si el proyectil colisiona con el jugador, reducir su salud y eliminar proyectil
                elif math.hypot(j['x'] - player_pos[0], j['y'] - player_pos[1]) < player_radius:
                    player_health -= jefe_danio
                    jefe_proyectiles.remove(j)

            if math.hypot(jefe_pos[0] - player_pos[0], jefe_pos[1] - player_pos[1]) < player_radius + 25: # Si el jefe colisiona físicamente con el jugador, causar daño menor
                player_health -= jefe_danio // 2


