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


