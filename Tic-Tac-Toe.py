import pygame
import sys
from math import inf as infinity
from random import choice
import time

# Inicialização do Pygame
pygame.init()

# Constantes com tema retrô aprimorado
WIDTH, HEIGHT = 600, 700
BOARD_SIZE = 3
CELL_SIZE = WIDTH // BOARD_SIZE

# Cores retrô melhoradas
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BG_COLOR = (10, 10, 30)  # Fundo azul mais escuro
LINE_COLOR = (50, 255, 50)  # Verde neon mais suave
X_COLOR = (255, 70, 70)  # Vermelho com tom mais quente
O_COLOR = (70, 170, 255)  # Azul mais vibrante
TEXT_COLOR = (255, 255, 50)  # Amarelo neon mais forte
BUTTON_COLOR = (80, 80, 180)  # Azul retrô mais escuro
BUTTON_HOVER_COLOR = (130, 130, 230)  # Azul mais claro
TITLE_COLOR = (255, 70, 70)  # Vermelho neon combinando com X
GLOW_COLOR = (100, 255, 100, 50)  # Efeito de brilho

# Configuração da janela
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jogo da Velha Retro")
font = pygame.font.SysFont('Courier New', 60, bold=True)  # Fonte maior
small_font = pygame.font.SysFont('Courier New', 36, bold=True)  # Fonte média
button_font = pygame.font.SysFont('Courier New', 30, bold=True)  # Fonte de botão

# Efeito de scanlines melhorado
def draw_scanlines():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for y in range(0, HEIGHT, 3):
        pygame.draw.line(overlay, (0, 0, 0, 30), (0, y), (WIDTH, y), 1)
    screen.blit(overlay, (0, 0))

# Efeito de brilho neon
def draw_glow(pos, radius, color):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.circle(overlay, color, pos, radius)
    screen.blit(overlay, (0, 0))

# Variáveis do jogo (mantidas da versão original)
cont = 0
total = 0
HUMAN = -1
COMP = +1
board = [
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, 0],
]

# Funções do jogo (mantidas da versão original)
def evaluate(state):
    if wins(state, COMP):
        score = +1
    elif wins(state, HUMAN):
        score = -1
    else:
        score = 0
    return score

def wins(state, player):
    win_state = [
        [state[0][0], state[0][1], state[0][2]],
        [state[1][0], state[1][1], state[1][2]],
        [state[2][0], state[2][1], state[2][2]],
        [state[0][0], state[1][0], state[2][0]],
        [state[0][1], state[1][1], state[2][1]],
        [state[0][2], state[1][2], state[2][2]],
        [state[0][0], state[1][1], state[2][2]],
        [state[2][0], state[1][1], state[0][2]],
    ]
    if [player, player, player] in win_state:
        return True
    else:
        return False

def game_over(state):
    return wins(state, HUMAN) or wins(state, COMP)

def empty_cells(state):
    cells = []
    for x, row in enumerate(state):
        for y, cell in enumerate(row):
            if cell == 0:
                cells.append([x, y])
    return cells

def valid_move(x, y):
    if [x, y] in empty_cells(board):
        return True
    else:
        return False

def set_move(x, y, player):
    if valid_move(x, y):
        board[x][y] = player
        return True
    else:
        return False

def minimax(state, depth, alpha, beta, player):
    global cont
    if player == COMP:
        best = [-1, -1, -infinity]
    else:
        best = [-1, -1, +infinity]

    if depth == 0 or game_over(state):
        score = evaluate(state)
        return [-1, -1, score]

    for cell in empty_cells(state):
        x, y = cell[0], cell[1]
        state[x][y] = player
        score = minimax(state, depth - 1, alpha, beta, -player)
        state[x][y] = 0
        score[0], score[1] = x, y

        if player == COMP:
            if score[2] > best[2]:
                best = score
            alpha = max(alpha, score[2])
            if beta <= alpha:
                break
        else:
            if score[2] < best[2]:
                best = score
            beta = min(beta, score[2])
            if beta <= alpha:
                break

    cont = cont + 1
    return best

def reset_board():
    global board
    board = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
    ]

# Funções da interface gráfica melhorada
def draw_board():
    screen.fill(BG_COLOR)
    
    # Efeito de gradiente no fundo mais suave
    for y in range(HEIGHT):
        alpha = min(30, y // 15)
        pygame.draw.line(screen, (alpha, alpha, alpha + 30), (0, y), (WIDTH, y))
    
    # Desenha as linhas do tabuleiro com efeito brilhante
    for i in range(1, BOARD_SIZE):
        # Efeito de brilho nas linhas
        pygame.draw.line(screen, (LINE_COLOR[0]//4, LINE_COLOR[1]//4, LINE_COLOR[2]//4), 
                         (0, i * CELL_SIZE + 1), (WIDTH, i * CELL_SIZE + 1), 8)
        pygame.draw.line(screen, (LINE_COLOR[0]//4, LINE_COLOR[1]//4, LINE_COLOR[2]//4), 
                         (i * CELL_SIZE + 1, 0), (i * CELL_SIZE + 1, WIDTH), 8)
        
        pygame.draw.line(screen, LINE_COLOR, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), 4)
        pygame.draw.line(screen, LINE_COLOR, (i * CELL_SIZE, 0), (i * CELL_SIZE, WIDTH), 4)
    
    # Desenha os X e O com estilo retrô melhorado
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == HUMAN:
                if h_choice == 'X':
                    draw_x(col * CELL_SIZE, row * CELL_SIZE)
                else:
                    draw_o(col * CELL_SIZE, row * CELL_SIZE)
            elif board[row][col] == COMP:
                if c_choice == 'X':
                    draw_x(col * CELL_SIZE, row * CELL_SIZE)
                else:
                    draw_o(col * CELL_SIZE, row * CELL_SIZE)
    
    # Desenha o status do jogo com efeito neon melhorado
    status_text = ""
    if game_over(board):
        if wins(board, HUMAN):
            status_text = "VITÓRIA!"
        elif wins(board, COMP):
            status_text = "DERROTA!"
        else:
            status_text = "EMPATE!"
    elif len(empty_cells(board)) == 0:
        status_text = "EMPATE!"
        global game_state
        game_state = GAME_OVER
    
    if status_text:
        # Efeito de texto neon com brilho
        for i in range(5, 0, -1):
            glow_color = (TEXT_COLOR[0]//i, TEXT_COLOR[1]//i, TEXT_COLOR[2]//i, 50)
            text_glow = font.render(status_text, True, glow_color)
            text_rect = text_glow.get_rect(center=(WIDTH//2, HEIGHT - 100))
            screen.blit(text_glow, text_rect)
        
        text = font.render(status_text, True, TEXT_COLOR)
        text_rect = text.get_rect(center=(WIDTH//2, HEIGHT - 100))
        screen.blit(text, text_rect)
        
        # Botão de reiniciar com estilo retrô melhorado
        button_color = BUTTON_HOVER_COLOR if restart_button_hover else BUTTON_COLOR
        pygame.draw.rect(screen, button_color, restart_button_rect, border_radius=8)
        pygame.draw.rect(screen, LINE_COLOR, restart_button_rect, 3, border_radius=8)
        
        restart_text = button_font.render("JOGAR NOVAMENTE", True, WHITE)
        restart_text_rect = restart_text.get_rect(center=restart_button_rect.center)
        screen.blit(restart_text, restart_text_rect)
    
    # Efeito de scanlines
    draw_scanlines()
    pygame.display.flip()

def draw_x(x, y):
    padding = CELL_SIZE // 3  # Espaçamento maior
    center_x, center_y = x + CELL_SIZE//2, y + CELL_SIZE//2
    
    # Efeito de brilho
    draw_glow((center_x, center_y), CELL_SIZE//3, (X_COLOR[0]//3, X_COLOR[1]//3, X_COLOR[2]//3, 100))
    
    # X com estilo mais retrô
    pygame.draw.line(screen, X_COLOR, 
                    (x + padding, y + padding), 
                    (x + CELL_SIZE - padding, y + CELL_SIZE - padding), 10)
    pygame.draw.line(screen, X_COLOR, 
                    (x + CELL_SIZE - padding, y + padding), 
                    (x + padding, y + CELL_SIZE - padding), 10)

def draw_o(x, y):
    padding = CELL_SIZE // 3  # Espaçamento maior
    center_x, center_y = x + CELL_SIZE//2, y + CELL_SIZE//2
    
    # Efeito de brilho
    draw_glow((center_x, center_y), CELL_SIZE//3, (O_COLOR[0]//3, O_COLOR[1]//3, O_COLOR[2]//3, 100))
    
    # O com estilo mais retrô
    pygame.draw.circle(screen, O_COLOR, (center_x, center_y), 
                       CELL_SIZE//2 - padding, 10)

def show_menu():
    global h_choice, c_choice, first, game_state
    
    screen.fill(BG_COLOR)
    
    # Efeito de gradiente no fundo mais suave
    for y in range(HEIGHT):
        alpha = min(30, y // 15)
        pygame.draw.line(screen, (alpha, alpha, alpha + 30), (0, y), (WIDTH, y))
    
    # Título com efeito neon melhorado
    title = "JOGO DA VELHA"
    for i in range(5, 0, -1):
        glow_color = (TITLE_COLOR[0]//i, TITLE_COLOR[1]//i, TITLE_COLOR[2]//i, 50)
        title_glow = font.render(title, True, glow_color)
        title_rect = title_glow.get_rect(center=(WIDTH//2, 100))
        screen.blit(title_glow, title_rect)
    
    title_text = font.render(title, True, TITLE_COLOR)
    title_rect = title_text.get_rect(center=(WIDTH//2, 100))
    screen.blit(title_text, title_rect)
    
    # Subtítulo decorativo
    subtitle = small_font.render("~ RETRO EDITION ~", True, (150, 150, 255))
    subtitle_rect = subtitle.get_rect(center=(WIDTH//2, 160))
    screen.blit(subtitle, subtitle_rect)
    
    # Seleção de símbolo
    symbol_text = small_font.render("ESCOLHA SEU SÍMBOLO:", True, TEXT_COLOR)
    symbol_text_rect = symbol_text.get_rect(center=(WIDTH//2, 230))
    screen.blit(symbol_text, symbol_text_rect)
    
    # Botões X e O com estilo retrô melhorado
    x_button_color = BUTTON_HOVER_COLOR if x_button_hover else BUTTON_COLOR
    o_button_color = BUTTON_HOVER_COLOR if o_button_hover else BUTTON_COLOR
    
    pygame.draw.rect(screen, x_button_color, x_button_rect, border_radius=8)
    pygame.draw.rect(screen, LINE_COLOR, x_button_rect, 3, border_radius=8)
    
    pygame.draw.rect(screen, o_button_color, o_button_rect, border_radius=8)
    pygame.draw.rect(screen, LINE_COLOR, o_button_rect, 3, border_radius=8)
    
    x_text = button_font.render("X", True, X_COLOR)
    o_text = button_font.render("O", True, O_COLOR)
    x_text_rect = x_text.get_rect(center=x_button_rect.center)
    o_text_rect = o_text.get_rect(center=o_button_rect.center)
    screen.blit(x_text, x_text_rect)
    screen.blit(o_text, o_text_rect)
    
    # Quem começa
    first_text = small_font.render("QUEM COMEÇA?", True, TEXT_COLOR)
    first_text_rect = first_text.get_rect(center=(WIDTH//2, 380))
    screen.blit(first_text, first_text_rect)
    
    # Botões de quem começa com estilo retrô melhorado
    human_button_color = BUTTON_HOVER_COLOR if human_first_button_hover else BUTTON_COLOR
    comp_button_color = BUTTON_HOVER_COLOR if comp_first_button_hover else BUTTON_COLOR
    
    pygame.draw.rect(screen, human_button_color, human_first_button_rect, border_radius=8)
    pygame.draw.rect(screen, LINE_COLOR, human_first_button_rect, 3, border_radius=8)
    
    pygame.draw.rect(screen, comp_button_color, comp_first_button_rect, border_radius=8)
    pygame.draw.rect(screen, LINE_COLOR, comp_first_button_rect, 3, border_radius=8)
    
    human_first_text = button_font.render("VOCÊ", True, WHITE)
    comp_first_text = button_font.render("CPU", True, WHITE)
    human_first_text_rect = human_first_text.get_rect(center=human_first_button_rect.center)
    comp_first_text_rect = comp_first_text.get_rect(center=comp_first_button_rect.center)
    screen.blit(human_first_text, human_first_text_rect)
    screen.blit(comp_first_text, comp_first_text_rect)
    
    # Botão de iniciar
    if h_choice and first:
        start_button_color = BUTTON_HOVER_COLOR if start_button_hover else BUTTON_COLOR
        pygame.draw.rect(screen, start_button_color, start_button_rect, border_radius=8)
        pygame.draw.rect(screen, LINE_COLOR, start_button_rect, 3, border_radius=8)
        
        start_text = button_font.render("INICIAR JOGO", True, WHITE)
        start_text_rect = start_text.get_rect(center=start_button_rect.center)
        screen.blit(start_text, start_text_rect)
    
    # Efeito de scanlines
    draw_scanlines()
    pygame.display.flip()

# Estados do jogo
MENU = 0
PLAYING = 1
GAME_OVER = 2
game_state = MENU

# Variáveis de seleção
h_choice = ''
c_choice = ''
first = ''

# Retângulos para os botões (melhor alinhados)
button_width, button_height = 100, 60
x_button_rect = pygame.Rect(WIDTH//2 - button_width - 20, 270, button_width, button_height)
o_button_rect = pygame.Rect(WIDTH//2 + 20, 270, button_width, button_height)
human_first_button_rect = pygame.Rect(WIDTH//2 - button_width - 20, 420, button_width, button_height)
comp_first_button_rect = pygame.Rect(WIDTH//2 + 20, 420, button_width, button_height)
start_button_rect = pygame.Rect(WIDTH//2 - 120, 520, 240, 60)
restart_button_rect = pygame.Rect(WIDTH//2 - 120, HEIGHT - 60, 240, 50)

# Variáveis de hover
x_button_hover = False
o_button_hover = False
human_first_button_hover = False
comp_first_button_hover = False
start_button_hover = False
restart_button_hover = False

# Loop principal
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == MENU:
                # Seleção de símbolo
                if x_button_rect.collidepoint(mouse_pos):
                    h_choice = 'X'
                    c_choice = 'O'
                elif o_button_rect.collidepoint(mouse_pos):
                    h_choice = 'O'
                    c_choice = 'X'
                
                # Quem começa
                elif human_first_button_rect.collidepoint(mouse_pos):
                    first = 'S'
                elif comp_first_button_rect.collidepoint(mouse_pos):
                    first = 'N'
                
                # Iniciar jogo
                elif start_button_rect.collidepoint(mouse_pos) and h_choice and first:
                    reset_board()
                    game_state = PLAYING
                    if first == 'N':
                        # Computador joga primeiro
                        depth = len(empty_cells(board))
                        if depth == 9:
                            x = choice([0, 1, 2])
                            y = choice([0, 1, 2])
                        else:
                            move = minimax(board, depth, -infinity, infinity, COMP)
                            x, y = move[0], move[1]
                        set_move(x, y, COMP)
            
            elif game_state == PLAYING:
                # Jogada do humano
                if len(empty_cells(board)) > 0 and not game_over(board):
                    x, y = mouse_pos[0] // CELL_SIZE, mouse_pos[1] // CELL_SIZE
                    if valid_move(y, x):
                        set_move(y, x, HUMAN)
                        
                        # Verifica se o jogo acabou após a jogada do humano
                        if not game_over(board) and len(empty_cells(board)) > 0:
                            # Jogada do computador
                            depth = len(empty_cells(board))
                            if depth > 0:
                                move = minimax(board, depth, -infinity, infinity, COMP)
                                x, y = move[0], move[1]
                                set_move(x, y, COMP)
            
            elif game_state == GAME_OVER:
                if restart_button_rect.collidepoint(mouse_pos):
                    game_state = MENU
                    h_choice = ''
                    c_choice = ''
                    first = ''
                    reset_board()  # Resetar o tabuleiro ao voltar ao menu
    
    # Atualiza estados de hover
    if game_state == MENU:
        x_button_hover = x_button_rect.collidepoint(mouse_pos)
        o_button_hover = o_button_rect.collidepoint(mouse_pos)
        human_first_button_hover = human_first_button_rect.collidepoint(mouse_pos)
        comp_first_button_hover = comp_first_button_rect.collidepoint(mouse_pos)
        start_button_hover = start_button_rect.collidepoint(mouse_pos) and h_choice and first
    elif game_state == GAME_OVER:
        restart_button_hover = restart_button_rect.collidepoint(mouse_pos)
    
    # Renderiza o estado atual do jogo
    if game_state == MENU:
        show_menu()
    elif game_state == PLAYING:
        if game_over(board) or len(empty_cells(board)) == 0:
            game_state = GAME_OVER
        draw_board()
    elif game_state == GAME_OVER:
        draw_board()

pygame.quit()
sys.exit()