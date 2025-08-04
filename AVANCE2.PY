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
clock = pygame.time.Clock() #para controlar la velocidad de fotogramas

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
info_font = pygame.font.SysFont("Arial", 20)#informacion HUD

# Función para cargar imágenes desde una ruta y redimensionarlas
def cargar_imagen_ruta(ruta, ancho_objetivo, alto_objetivo):
    imagen = pygame.image.load(ruta).convert_alpha()
    original_ancho, original_alto = imagen.get_size()
    ratio = min(ancho_objetivo / original_ancho, alto_objetivo / original_alto)
    nuevo_tamano = (int(original_ancho * ratio), int(original_alto * ratio))
    imagen_redimensionada = pygame.transform.smoothscale(imagen, nuevo_tamano)
    return imagen_redimensionada

# Carga de imágenes para personajes, enemigos, proyectiles, etc.
escudo_img = cargar_imagen_ruta("escudop.png", 60, 60) 
personaje_img = cargar_imagen_ruta("Personaje.png", 150, 150)
enemigo_imgs = [cargar_imagen_ruta(f"enemigo{i}.png", 80, 80) for i in range(1, 15)]  
#personaje2_img = cargar_imagen_ruta("Personaje2.png", 125, 125)
#personaje3_img = cargar_imagen_ruta("Personaje3.png", 140, 140)
proyectil_img = cargar_imagen_ruta("Proyectil.png", 20, 20)
proyectil_jefe_img = cargar_imagen_ruta("ProyectilZombie.png", 30, 30)
#enemigo_grande_img1 = cargar_imagen_ruta("enemigo_grande1.png", 150, 150)
#enemigo_grande_img2 = cargar_imagen_ruta("enemigo_grande2.png", 150, 150)
fondo_juego = pygame.image.load("fondoJuego.png").convert()
fondo_juego = pygame.transform.scale(fondo_juego, (WIDTH, HEIGHT))

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
proyectiles_jefe = []

# Logotipo para menú
logotipo_img = cargar_imagen_ruta("Logotipo.png", 400, 400)

# Crea una lista de partículas (brasas) que caen lentamente en pantalla
menu_brasas = [{'x': random.randint(0, WIDTH), 'y': random.randint(0, HEIGHT), 'speed': random.uniform(0.2, 0.6)} for _ in range(60)]

# Dibuja un botón interactivo
def draw_button(text, x, y, w, h, base_color, hover_color, action=None):
    mouse = pygame.mouse.get_pos()  # Obtiene posición del mouse
    click = pygame.mouse.get_pressed()  # Detecta clic
    rect = pygame.Rect(x, y, w, h)  # Crea rectángulo del botón
    is_hovered = rect.collidepoint(mouse)  # Verifica si el mouse está encima

    # Dibuja contorno y relleno según si el mouse está encima 
    pygame.draw.rect(screen, WHITE, rect, border_radius=10) #DIBUJA EL CONTORNO Y RELLENO
    inner_rect = rect.inflate(-4, -4)
    pygame.draw.rect(screen, hover_color if is_hovered else base_color, inner_rect, border_radius=8)

    # Dibuja el texto centrado
    text_surf = button_font.render(text, True, BLACK)#crea una superficie de texto con el texto del boton
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect) #dinuja el texto en la pantalla

    # Si se hace clic en el botón, ejecuta la acción asociada
    if is_hovered and click[0] == 1 and action:
        pygame.time.wait(150)  # pausa para evitar múltiples clics
        action()

# Dibuja una barra de salud con etiqueta (arriba o abajo)
def draw_health_bar(x, y, width, height, current_health, max_health, border_color, fill_color, back_color, label="", label_pos="above"):
    
    # Si hay texto y debe ir arriba
    if label and label_pos == "above":
        label_surf = info_font.render(label, True, WHITE)#crea una imagen de texto, con la informacion de info
        screen.blit(label_surf, (x, y - label_surf.get_height() - 5)) #dibuja el texto en pantalla, espacio de 5 pixeles

    # Dibuja fondo de la barra
    back_rect = pygame.Rect(x, y, width, height) #Crea el rectángulo de fondo de la barra
    pygame.draw.rect(screen, back_color, back_rect)#Dibuja el fondo de la barra

    # Calcula el ancho de la barra de vida según salud actual
    fill_width = int(width * (current_health / max_health))
    fill_rect = pygame.Rect(x, y, fill_width, height) #Crea el rectángulo de relleno
    pygame.draw.rect(screen, fill_color, fill_rect) #relleno de la barra
    # Dibuja el borde de la barra
    pygame.draw.rect(screen, border_color, back_rect, 2)
    
    # Si hay texto y debe ir debajo
    if label and label_pos == "below": # Verifica si hay una etiqueta (label) y si debe mostrarse debajo de la barra.
        label_surf = info_font.render(label, True, WHITE)
        screen.blit(label_surf, (x, y + height + 5)) 

# Dibuja las brasas  en movimiento
def draw_brasas(brazas):
    for b in brazas:
        b['y'] += b['speed']
        if b['y'] > HEIGHT:  # Si se salen por abajo, reaparecen arriba
            b['y'] = 0
            b['x'] = random.randint(0, WIDTH)
        pygame.draw.circle(screen, RED, (int(b['x']), int(b['y'])), 2)# Dibuja cada brasa como un círculo rojo pequeño.

# Muestra una pantalla de información como la historia o el mensaje de muerte, etc
def mostrar_pantalla_info(titulo, descripcion, volver_a_menu=False):
    esperando = True

    # Fuentes para título, descripción e instrucciones
    titulo_font = pygame.font.SysFont("Arial Black", 36)
    descripcion_font = pygame.font.SysFont("Arial", 24)
    instruccion_font = pygame.font.SysFont("Arial", 20)

    while esperando:
        screen.fill(BLACK)#pantalla en negro
        draw_brasas(menu_brasas)  # Fondo animado

        # Panel con transparencia
        panel_rect = pygame.Surface((600, 300), pygame.SRCALPHA) # Crea una superficie, donde su muestra el texto
        panel_rect.fill((0, 0, 0, 180)) #Rellena el panel con negro y una opacidad
        screen.blit(panel_rect, (WIDTH // 2 - 300, HEIGHT // 2 - 150)) #dibuja el panel centrado

        # Título centrado,  si es de muerte
        titulo_surf = titulo_font.render(titulo, True, PINK if "¡Has muerto!" not in titulo else RED)
        screen.blit(titulo_surf, (WIDTH // 2 - titulo_surf.get_width() // 2, HEIGHT // 2 - 130))#Dibuja el título centrado horizontalmente

        # texto descripción
        lineas = descripcion.split("\n")
        for i, linea in enumerate(lineas):#Recorre cada línea con su índice (i) para posicionarlas una debajo de otra.
            texto_surf = descripcion_font.render(linea, True, WHITE)# Convierte cada línea en una imagen de texto blanca usando la fuente descripcion_font
            screen.blit(texto_surf, (WIDTH // 2 - texto_surf.get_width() // 2, HEIGHT // 2 - 60 + i * 35))#Dibuja cada línea centrada horizontalment

        # Instrucción para continuar
        instruccion_text = "Presiona ENTER para continuar..."
        if volver_a_menu:
            instruccion_text = "Presiona ENTER para volver al menú..."# Si la variable volver_a_menu es True
        instruccion = instruccion_font.render(instruccion_text, True, CYAN)#Convierte el mensaje final en una imagen de texto cyan con la fuente instruccion_font
        screen.blit(instruccion, (WIDTH // 2 - instruccion.get_width() // 2, HEIGHT // 2 + 100))

        pygame.display.flip() #Actualiza toda la pantalla para mostrar los cambios.

        # Eventos: salir o continuar con ENTER
        for event in pygame.event.get():# Recorre todos los eventos capturados por Pygame
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:#Si el jugador presiona una tecla, se evalúa cuál fue.
                if event.key == pygame.K_RETURN:
                    esperando = False
                elif event.key == pygame.K_SPACE:
                    if player_level in [2, 3] and not escudo_activo and escudo_usos < MAX_USOS_ESCUDO:
                        escudo_activo = True
                        tiempo_escudo = pygame.time.get_ticks() #Se guarda el tiempo actual para controlar la duración del escudo.
                        escudo_usos += 1 #Se suma un uso al contador de usos del escudo

# Muestra una historia diferente dependiendo del nivel
def mostrar_historia(nivel):
    historias = { # Un diccionario que contiene el título y la descripción para cada nivel.
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
    #Si el nivel está en el diccionario historias, 
    #llama a mostrar_pantalla_info con el título y la descripción correspondientes.

def proyectil_cerca_jugador(proyectiles, player_pos, rango=50):
    px, py = player_pos#Posición del jugador.
    for proj in proyectiles:
        x, y = proj['x'], proj['y']  #Diccionario con claves 'x' y 'y'
        distancia = ((x - px)**2 + (y - py)**2)**0.5
        if distancia <= rango: #Distancia máxima para considerar que un proyectil está "cerca".
            return True
    return False



def game_loop():
    # Estas líneas declaran que se van a usar y modificar variables definidas fuera de esta función
    global proyectiles_jefe
    global run_game, show_menu
    
    escudo_activo = False #: Definen si el escudo del jugador está activo, cuánto tiempo dura, y cuántos usos le quedan
    tiempo_escudo = 0
    DURACION_ESCUDO = 3000
    escudo_usos = 0
    MAX_USOS_ESCUDO = 2


    # Partículas tipo brasas que se mueven en el fondo durante el juego
    particles = [{'x': random.randint(0, WIDTH), 'y': random.randint(0, HEIGHT), 'radius': random.randint(1, 3),
                  'speed': random.uniform(0.2, 0.6)} for _ in range(120)]

    # Posición inicial del jugador (centro de pantalla)
    player_pos = [WIDTH // 2, HEIGHT // 2]
    player_radius = 25  # Para calcular colisiones

    # Estadísticas iniciales del jugador
    base_speed = 4
    player_speed = base_speed #posición, tamaño, velocidad base, vida, experiencia actual, 
    player_health = 100  #nivel y la XP necesaria para subir de nivel.
    player_max_health = 100
    player_xp = 0
    player_level = 1
    xp_to_next = 50

    # controla Nivel y habilidades
    nivel_actual = 1
    max_nivel = 3
    habilidad_actual = 1
    habilidad_nombres = {1: "Doble Tiro", 2: "Relentizador", 3: "Velocidad"}

    # Control de habilidad de relentizar
    ralentizar_enemigos = False #indica si la habilidad de ralentizar está activa.
    ralentizador_fin = 0

    # Lista de proyectiles del jugador
    projectiles = []
    projectile_speed = 7 #velocidad
    shoot_delay = 500 #tiempo mínimo entre disparos (500 ms)
    last_shot_time = pygame.time.get_ticks() #guarda el tiempo del último disparo

    # Enemigos normales
    enemies = [] # lista vacía donde se guardarán los enemigos que aparecen
    enemy_spawn_delay = 1500 # intervalo entre apariciones de enemigo
    last_enemy_spawn = pygame.time.get_ticks()#guarda el tiempo en que apareció el último enemigo
    enemy_base_speed = 1.5 #velocidad base de los enemigos
    enemy_speed = enemy_base_speed #velocidad actual

    #atributos Jefe del nivel
    jefe_activo = False
    jefe_pos = None
    jefe_vida = 0
    jefe_max_vida = 0
    jefe_danio = 10
    jefe_speed = 2
    jefe_proyectiles = []
    jefe_disparo_delay = 1000
    ultimo_disparo_jefe = 0
    #Propiedades para el "jefe" del nivel: si está activo, 
    # su posición, vida, daño, velocidad, proyectiles y temporizador de disparo. Inicialmente está inactivo.

    # Lista de manchas de sangre que se desvanecen con el tiempo
    blood_stains = []

    # Mostrar historia nivel
    mostrar_historia(nivel_actual)

    running = True #variable de control principal del game loop. Mientras sea True, el bucle seguirá ejecutándose.o

    while running:
        dt = clock.tick(60)  # Limita el bucle a 60 FPS y guarda el tiempo transcurrido entre frames en dt
        screen.blit(fondo_juego, (0, 0)) # Fondo 

        # Dibuja brasas animadas
        for p in particles:#Recorre la lista particles
            pygame.draw.circle(screen, RED, (int(p['x']), int(p['y'])), p['radius'])
            p['y'] -= p['speed'] #suba la brasa
            if p['y'] < 0:  # Si sale de la pantalla, reaparece abajo
                p['x'] = random.randint(0, WIDTH)
                p['y'] = HEIGHT + random.randint(0, 100)
                p['speed'] = random.uniform(0.2, 0.6)

        # Dibuja las manchas de sangre con transparencia
        for stain in blood_stains[:]:# Recorre una copia de la lista de manchas
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
                sys.exit() # Si el jugador cierra la ventana, el juego se termina completamente.

        # Movimiento del jugador con teclas W, A, S, D
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: player_pos[1] -= player_speed
        if keys[pygame.K_s]: player_pos[1] += player_speed
        if keys[pygame.K_a]: player_pos[0] -= player_speed
        if keys[pygame.K_d]: player_pos[0] += player_speed

        # Activar escudo manual con barra espaciadora en niveles 2 y 3, y con usos disponibles
        if player_level in [2, 3]:
            if not escudo_activo and escudo_usos < MAX_USOS_ESCUDO:
                if keys[pygame.K_SPACE]:
                    escudo_activo = True
                    tiempo_escudo = pygame.time.get_ticks()
                    escudo_usos += 1

        # Limita que el jugador no se salga de los bordes de la pantalla
        player_pos[0] = max(player_radius, min(player_pos[0], WIDTH - player_radius))
        player_pos[1] = max(player_radius, min(player_pos[1], HEIGHT - player_radius))

        # Desactivar escudo luego de 3 segundos
        if escudo_activo:
            screen.blit(escudo_img, (player_pos[0] - escudo_img.get_width() // 2, player_pos[1] - escudo_img.get_height() // 2))
            tiempo_actual = pygame.time.get_ticks()
            if tiempo_actual - tiempo_escudo >= DURACION_ESCUDO:
                escudo_activo = False


        # Tiempo actual para controlar disparos, enemigos, etc.
        now = pygame.time.get_ticks()

        # Disparar proyectiles automáticamente, por un evento
        if now - last_shot_time >= shoot_delay:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx = mouse_x - player_pos[0]
            dy = mouse_y - player_pos[1]
            dist = math.hypot(dx, dy)  # Calcula distancia entre jugador y mouse

            if dist != 0:  # Normaliza dirección del disparo
                dx /= dist
                dy /= dist #solo movemos el mouse a direccion del zombie

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

        # Movimiento de proyectiles en pantalla, como se desplaza
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

        #Este bloque de código se encarga de crear nuevos enemigos en la pantalla de manera periódica.
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
                        
                            # Según el nivel activa el jefe
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

        # controla que jefe esta activo y su comportamiento segun el nivel
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

            #disparo del jefe
            if now - ultimo_disparo_jefe >= jefe_disparo_delay:# Control del disparo del jefe, respetando delay entre disparos
                jdx = player_pos[0] - jefe_pos[0]
                jdy = player_pos[1] - jefe_pos[1]
                dist = math.hypot(jdx, jdy)
                if dist != 0:
                    jdx /= dist
                    jdy /= dist
                jefe_proyectiles.append({'x': jefe_pos[0], 'y': jefe_pos[1], 'dx': jdx, 'dy': jdy})# Agregar un nuevo proyectil que va hacia el jugador
                ultimo_disparo_jefe = now 
               #maneja los ataques del jefe y la interacción con el jugador.
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

#maneja el daño que el jefe causa si se acerca demasiado al jugador, sin necesidad de usar un proyectil.
            if math.hypot(jefe_pos[0] - player_pos[0], jefe_pos[1] - player_pos[1]) < player_radius + 25: 
                player_health -= jefe_danio // 2

            for p in projectiles[:]: #Este último bloque se encarga de registrar el daño que el jugador le inflige al jefe.
                if math.hypot(jefe_pos[0] - p['x'], jefe_pos[1] - p['y']) < 30:
                    jefe_vida -= 1
                    projectiles.remove(p)

            #si el jefe muere, avanza nivel
            if jefe_vida <= 0:
                # Añadir mancha de sangre en la posición del jefe al morir
                blood_stains.append({'x': jefe_pos[0], 'y': jefe_pos[1], 'alpha': 255})
                jefe_activo = False # Desactivar jefe para que deje de moverse y atacar
                jefe_proyectiles.clear() # Eliminar proyectil que impactó
                nivel_actual += 1

                #si hay mas niveles muestra historia
                if nivel_actual <= max_nivel:
                    mostrar_historia(nivel_actual)

                enemy_speed += 0.7# Aumentar dificultad progresivamente modificando la velocidad y frecuencia de enemigos
                enemy_spawn_delay = max(400, enemy_spawn_delay - 250)
                
                if nivel_actual == 2:    # Ajustar habilidad y velocidad del jugador según el nivel actual
                    habilidad_actual = 2
                    player_speed = base_speed
                elif nivel_actual == 3:
                    habilidad_actual = 3
                    player_speed = base_speed * 1.8 
                else:
                    habilidad_actual = 3
                    player_speed = base_speed * 1.8
                # Activar jefe al iniciar nivel 3
                if nivel_actual == 3 and not jefe_activo:
                    jefe_activo = True
                    jefe_vida = jefe_max_vida


                ralentizar_enemigos = False # Se desactiva la habilidad de ralentizar cada vez que se avanza de nivel

        if habilidad_actual == 2 and not ralentizar_enemigos and player_level >= 2:
            if keys[pygame.K_r]:
                ralentizar_enemigos = True
                tiempo_ralentizador = pygame.time.get_ticks()
                enemy_speed = enemy_base_speed / 2.5 # Disminuye la velocidad de los enemigos temporalmente
                ralentizador_fin = now + 5000 # Duración del efecto: 5 segundos

        if habilidad_actual == 3:
            player_speed = base_speed * 1.8  # Aumenta la velocidad en habilidad 3 (fase avanzada)
        elif habilidad_actual == 1 or habilidad_actual == 2:
            player_speed = base_speed  # Velocidad normal en habilidad 1 o 2

        # Dibujar jugador primero
        screen.blit(personaje_img, (player_pos[0] - personaje_img.get_width() // 2, player_pos[1] - personaje_img.get_height() // 2))

        # Luego dibujar escudo encima
        if escudo_activo:
            screen.blit(escudo_img, (player_pos[0] - escudo_img.get_width() // 2, player_pos[1] - escudo_img.get_height() // 2))


        # Dibujar enemigos centrados
        for enemy in enemies:
            img = enemigo_imgs[enemy['tipo']]
            screen.blit(img, (enemy['x'] - img.get_width() // 2, enemy['y'] - img.get_height() // 2))


        # Dibujar proyectiles
        for p in projectiles:
            screen.blit(proyectil_img, (p['x'] - proyectil_img.get_width() // 2, p['y'] - proyectil_img.get_height() // 2))

        # Dibujar jefe
        if jefe_activo:
            jefe_img = jefe_imgs.get(nivel_actual)
            if jefe_img:
                screen.blit(jefe_img, (int(jefe_pos[0] - jefe_img.get_width() // 2), int(jefe_pos[1] - jefe_img.get_height() // 2)))
            else:
                pygame.draw.circle(screen, RED, (int(jefe_pos[0]), int(jefe_pos[1])), 30)
            for j in jefe_proyectiles:
                screen.blit(proyectil_jefe_img, (int(j['x'] - proyectil_jefe_img.get_width() // 2), int(j['y'] - proyectil_jefe_img.get_height() // 2)))
            

        # imprime estadisticas ,HUD con nivel, experiencia y nombre de habilidad
        screen.blit(info_font.render(f"Nivel: {player_level}", True, WHITE), (10, 10))
        screen.blit(info_font.render(f"XP: {player_xp}/{xp_to_next}", True, WHITE), (10, 35))
        screen.blit(info_font.render(f"Fase: {nivel_actual}", True, WHITE), (10, 60))
        screen.blit(info_font.render(f"Habilidad: {habilidad_nombres[habilidad_actual]}", True, WHITE), (10, 85))
        if habilidad_actual == 2 and ralentizar_enemigos:# Mostrar barra de habilidad si ralentizador está activo
            tiempo_restante = (ralentizador_fin - now) / 1000
            screen.blit(info_font.render(f"Ralentizador activo: {tiempo_restante:.1f}s", True, WHITE), (10, 110))
        # Barra de vida del jugador con etiqueta encima
        draw_health_bar(10, HEIGHT - 35, 200, 25, player_health, player_max_health, WHITE, GREEN, DARK_RED, "Barra de salud de Lany", "above")

        if jefe_activo:
            #barra de vida para el jefe según la fase
            jefe_labels = {
                1: "Barra de salud del Portador",
                2: "Barra de salud del Acechador",
                3: "Barra de salud del Susurrador"
            }
            jefe_label_text = jefe_labels.get(nivel_actual, f"Jefe Fase {nivel_actual}")

            # Barra de vida del jefe con etiqueta debajo, reubicada para no sobreponerse
            # Calculamos la posición x para que esté centrado con la barra de vida
            jefe_bar_x = WIDTH - 260
            jefe_bar_y = 50 
            #Dibuja la barra de salud del jefe. 
            draw_health_bar(jefe_bar_x, jefe_bar_y, 250, 25, jefe_vida, jefe_max_vida, WHITE, RED, DARK_RED, jefe_label_text, "below")

        if player_health <= 0: # Verificar si el jugador murió
            grito_perder_sound.play()
            mostrar_pantalla_info("¡Has muerto!", "Los monstruos han consumido el mundo.\nNo hay esperanza...", volver_a_menu=True)
            running = False
            break

        if nivel_actual > max_nivel:# Verificar si ganó el juego (superó la última fase)
            mostrar_pantalla_info("¡HAS GANADO!", "El brote ha sido contenido.\nLa humanidad tiene una segunda oportunidad.", volver_a_menu=True)
            running = False
            break

        pygame.display.flip() # Actualiza la pantalla

    # Final del bucle principal del juego
    run_game = False
    show_menu = True

def start_game():# Función para iniciar el juego
    global run_game, show_menu
    run_game = True
    show_menu = False

def exit_game():
    pygame.quit()
    sys.exit()

def show_instructions_screen():
    global show_menu, show_instructions
    show_instructions = True
    show_menu = False

# Bucle principal
while True:
    clock.tick(60) # Limita a 60 FPS
    screen.blit(fondo_juego, (0, 0))  # Mostrar imagen de fondo


    if show_menu:
        screen.fill(BLACK)
        draw_brasas(menu_brasas)

        # Mover y dibujar enemigos grandes en las esquinas
        #for z in menu_enemigos:
           # z['x'] += z['dx']
            #z['y'] += z['dy']

            # Rebote en bordes para limitar su movimiento en la esquina
            #if z['x'] < 20 or z['x'] > (WIDTH - 20):
               # z['dx'] *= -1
            #if z['y'] < 20 or z['y'] > (HEIGHT - 20):
               # z['dy'] *= -1

            #screen.blit(z['img'], (z['x'] - z['img'].get_width() // 2, z['y'] - z['img'].get_height() // 2))

        # Logotipo centrado arriba
        screen.blit(logotipo_img, (WIDTH // 2 - logotipo_img.get_width() // 2, 40))

        # Botones menú
        draw_button("Iniciar", WIDTH // 2 - 100, 360, 200, 50, RED, PINK, start_game)
        draw_button("Instrucciones", WIDTH // 2 - 100, 430, 200, 50, RED, PINK, show_instructions_screen)
        draw_button("Salir", WIDTH // 2 - 100, 500, 200, 50, RED, PINK, exit_game)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()  

    elif show_instructions:
        mostrar_pantalla_info(
             "INSTRUCCIONES",
            "Usa W A S D para moverte por el mapa\n"
            "Apunta con el mouse y dispara de forma automática\n"
            "Pulsa ESPACIO para activar tu poder especial (Nivel 2)\n"
            "¡Resiste los ataques y elimina a los enemigos más fuertes!",
            volver_a_menu=True
        )
        show_instructions = False
        show_menu = True

    elif run_game:
        game_loop()
