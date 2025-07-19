import pygame
import copy
import sys
import time
import math

# Constantes
WIDTH, HEIGHT = 500, 500
ROWS, COLS = 6, 6
SQUARE_SIZE = WIDTH // COLS

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
HIGHLIGHT = (255, 255, 0)
CROWN_COLOR = (255, 215, 0)
GOLD = (212, 175, 55)

pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Damas com IA - Minimax + AlfaBeta")
FONT = pygame.font.SysFont('Arial', 32)
SMALL_FONT = pygame.font.SysFont('Arial', 24)

class Piece:
    PADDING = 10
    OUTLINE = 5
    ANIMATION_SPEED = 9  # Velocidade da animação

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.animating = False
        self.calc_pos()

    def calc_pos(self):
        self.x = self.col * SQUARE_SIZE + SQUARE_SIZE // 2
        self.y = self.row * SQUARE_SIZE + SQUARE_SIZE // 2
        self.target_x = self.x
        self.target_y = self.y

    def make_king(self):
        self.king = True

    def draw(self, win):
        # Atualizar posição durante animação
        if self.animating:
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < 1:  # Chegou perto o suficiente
                self.x = self.target_x
                self.y = self.target_y
                self.animating = False
            else:
                # Movimento suave
                self.x += dx / self.ANIMATION_SPEED
                self.y += dy / self.ANIMATION_SPEED

        radius = SQUARE_SIZE // 2 - self.PADDING
        border_color = CROWN_COLOR if self.king else GRAY
        pygame.draw.circle(win, border_color, (int(self.x), int(self.y)), radius + self.OUTLINE)
        pygame.draw.circle(win, self.color, (int(self.x), int(self.y)), radius)
        
        # Desenhar coroa se for dama
        if self.king:
            crown_img = pygame.Surface((radius, radius), pygame.SRCALPHA)
            pygame.draw.polygon(crown_img, CROWN_COLOR, [
                (radius//2, 0),
                (radius//4, radius//2),
                (radius//2, radius//3),
                (3*radius//4, radius//2)
            ])
            win.blit(crown_img, (int(self.x - radius//2), int(self.y - radius//2)))

    def move(self, row, col):
        self.row = row
        self.col = col
        self.target_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
        self.target_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
        self.animating = True

    def is_animating(self):
        return self.animating

class Board:
    def __init__(self):
        self.board = []
        self.white_left = self.black_left = 6
        self.white_kings = self.black_kings = 0
        self.create_board()

    def draw_squares(self, win):
        win.fill(BLACK)
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(win, WHITE, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def evaluate(self):
        white_score = 0
        black_score = 0

        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    value = 1.5 if piece.king else 1

                    center_bonus = 0.3 if 2 <= row <= 5 and 2 <= col <= 5 else 0

                    progress_bonus = (row / 7) * 0.2 if piece.color == WHITE else ((7 - row) / 7) * 0.2

                    total = value + center_bonus + progress_bonus

                    if piece.color == WHITE:
                        white_score += total
                    else:
                        black_score += total

        
        white_moves = len(self.get_all_valid_moves(WHITE))
        black_moves = len(self.get_all_valid_moves(BLACK))
        mobility_score = (white_moves - black_moves) * 0.1

        return white_score - black_score + mobility_score

    def get_all_pieces(self, color):
        pieces = []
        for row in self.board:
            for piece in row:
                if piece and piece.color == color:
                    pieces.append(piece)
        return pieces

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if row % 2 == (col + 1) % 2:
                    if row < 2:
                        self.board[row].append(Piece(row, col, BLACK))
                    elif row > 3:
                        self.board[row].append(Piece(row, col, WHITE))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)

    def draw(self, win):
        self.draw_squares(win)
        for row in self.board:
            for piece in row:
                if piece:
                    piece.draw(win)

    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = 0, piece
        piece.move(row, col)
        if (piece.color == WHITE and row == 0) or (piece.color == BLACK and row == ROWS - 1):
            if not piece.king:  # Só faz dama se ainda não for
                piece.make_king()
                if piece.color == WHITE:
                    self.white_kings += 1
                else:
                    self.black_kings += 1

    def get_piece(self, row, col):
        return self.board[row][col]

    def remove(self, pieces):
        for piece in pieces:
            self.board[piece.row][piece.col] = 0
            if piece != 0:
                if piece.color == BLACK:
                    self.black_left -= 1
                    if piece.king:
                        self.black_kings -= 1
                else:
                    self.white_left -= 1
                    if piece.king:
                        self.white_kings -= 1

    def winner(self):
        if self.black_left <= 0:
            return WHITE
        elif self.white_left <= 0:
            return BLACK
        
        white_moves = len(self.get_all_valid_moves(WHITE))
        black_moves = len(self.get_all_valid_moves(BLACK))
        
        if white_moves == 0:
            return BLACK
        if black_moves == 0:
            return WHITE
        
        return None

    def get_valid_moves(self, piece):
        moves = {}
        
        if piece.king:
            # Movimento para damas - pode se mover em qualquer diagonal
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # Todas as direções diagonais
            for dr, dc in directions:
                for i in range(1, ROWS):
                    r, c = piece.row + dr * i, piece.col + dc * i
                    if 0 <= r < ROWS and 0 <= c < COLS:
                        if self.board[r][c] == 0:
                            moves[(r, c)] = []
                        else:
                            if self.board[r][c].color != piece.color:
                                r2, c2 = r + dr, c + dc
                                if 0 <= r2 < ROWS and 0 <= c2 < COLS and self.board[r2][c2] == 0:
                                    moves[(r2, c2)] = [self.board[r][c]]
                            break
                    else:
                        break
        else:
            # Movimento para peças normais
            left = piece.col - 1
            right = piece.col + 1
            row = piece.row

            if piece.color == WHITE:
                moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
                moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))
            else:
                moves.update(self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left))
                moves.update(self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right))

        # Verifica se há capturas obrigatórias
        must_capture = any(skipped for skipped in moves.values() if skipped)
        
        if must_capture:
            # Filtra apenas os movimentos de captura
            moves = {move: skipped for move, skipped in moves.items() if skipped}
            
            # Agora vamos verificar se há capturas múltiplas
            final_moves = {}
            for move, skipped in moves.items():
                # Simula o movimento para ver se há mais capturas disponíveis
                temp_board = copy.deepcopy(self)
                temp_piece = temp_board.get_piece(piece.row, piece.col)
                temp_board.move(temp_piece, move[0], move[1])
                temp_board.remove(skipped)
                
                # Verifica se há mais capturas disponíveis após este movimento
                new_moves = temp_board.get_valid_moves(temp_board.get_piece(move[0], move[1]))
                has_more_captures = any(skipped for skipped in new_moves.values() if skipped)
                
                if not has_more_captures:
                    final_moves[move] = skipped
                else:
                    # Se houver mais capturas, não adiciona este movimento
                    # Em vez disso, adiciona apenas os movimentos finais da cadeia
                    for new_move, new_skipped in new_moves.items():
                        if new_skipped:  # É uma captura
                            final_moves[new_move] = skipped + new_skipped
            
            return final_moves if final_moves else moves
        
        return moves

    def get_all_valid_moves(self, color):
        all_moves = {}
        for piece in self.get_all_pieces(color):
            valid_moves = self.get_valid_moves(piece)
            if valid_moves:
                all_moves[piece] = valid_moves
        return all_moves

    def has_capture_moves(self, color):
        for piece in self.get_all_pieces(color):
            moves = self.get_valid_moves(piece)
            if any(skipped for skipped in moves.values()):
                return True
        return False

    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break

            current = self.board[r][left]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, left)] = last + skipped
                else:
                    moves[(r, left)] = last

                if last:
                    row = max(r - 3, -1) if step == -1 else min(r + 3, ROWS)
                    moves.update(self._traverse_left(r + step, row, step, color, left - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, left + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]
            left -= 1

        return moves

    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= COLS:
                break

            current = self.board[r][right]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, right)] = last + skipped
                else:
                    moves[(r, right)] = last

                if last:
                    row = max(r - 3, -1) if step == -1 else min(r + 3, ROWS)
                    moves.update(self._traverse_left(r + step, row, step, color, right - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, right + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]
            right += 1

        return moves

def minimax(position, depth, alpha, beta, max_player, game):
    if depth == 0 or position.winner() is not None:
        return position.evaluate(), position

    if max_player:
        max_eval = float('-inf')
        best_move = None
        all_moves = get_all_moves(position, WHITE, game)
        
        # Prioriza movimentos de captura
        capture_moves = []
        for move in all_moves:
            piece, new_board = move
            original_valid_moves = position.get_valid_moves(piece)
            if any(skipped for skipped in original_valid_moves.values()):
                capture_moves.append(move)
        
        if capture_moves:
            all_moves = capture_moves
            
        for move in all_moves:
            piece, new_board = move
            evaluation = minimax(new_board, depth - 1, alpha, beta, False, game)[0]
            if evaluation > max_eval:
                max_eval = evaluation
                best_move = new_board
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        best_move = None
        all_moves = get_all_moves(position, BLACK, game)
        
        # Prioriza movimentos de captura
        capture_moves = []
        for move in all_moves:
            piece, new_board = move
            original_valid_moves = position.get_valid_moves(piece)
            if any(skipped for skipped in original_valid_moves.values()):
                capture_moves.append(move)
        
        if capture_moves:
            all_moves = capture_moves
            
        for move in all_moves:
            piece, new_board = move
            evaluation = minimax(new_board, depth - 1, alpha, beta, True, game)[0]
            if evaluation < min_eval:
                min_eval = evaluation
                best_move = new_board
            beta = min(beta, evaluation)
            if beta <= alpha:
                break
        return min_eval, best_move

def simulate_move(piece, move, board, game, skip):
    board.move(piece, move[0], move[1])
    if skip:
        board.remove(skip)
    return board

def get_all_moves(board, color, game):
    moves = []
    for piece in board.get_all_pieces(color):
        valid_moves = board.get_valid_moves(piece)
        for move, skip in valid_moves.items():
            temp_board = copy.deepcopy(board)
            temp_piece = temp_board.get_piece(piece.row, piece.col)
            new_board = simulate_move(temp_piece, move, temp_board, game, skip)
            moves.append((piece, new_board))
    return moves

def draw_winner(win, text):
    pygame.draw.rect(win, BLACK, (WIDTH//4, HEIGHT//3, WIDTH//2, HEIGHT//3))
    label = FONT.render(text, 1, WHITE)
    win.blit(label, (WIDTH//2 - label.get_width()//2, HEIGHT//2 - label.get_height()//2))
    pygame.display.update()
    time.sleep(3)

class Game:
    def __init__(self, win):
        self._init()
        self.win = win

    def update(self):
        self.board.draw(self.win)
        self.draw_valid_moves(self.valid_moves)
        self.draw_selected()
        pygame.display.update()

    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = WHITE
        self.valid_moves = {}
        self.waiting_for_animation = False

    def reset(self):
        self._init()

    def draw_selected(self):
        if self.selected:
            row, col = self.selected.row, self.selected.col
            pygame.draw.rect(self.win, HIGHLIGHT, 
                           (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            pygame.draw.circle(self.win, GREEN, 
                             (col * SQUARE_SIZE + SQUARE_SIZE//2, row * SQUARE_SIZE + SQUARE_SIZE//2), 10)

    def select(self, row, col):
        if self.waiting_for_animation:
            return False
            
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select(row, col)

        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            
            # Se houver capturas obrigatórias, mostra apenas elas
            if self.board.has_capture_moves(self.turn):
                self.valid_moves = {move: skipped for move, skipped in self.valid_moves.items() if skipped}
                
            return True
        return False

    def _move(self, row, col):
        piece = self.board.get_piece(row, col)
        if self.selected and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col)
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove(skipped)
                
                # Verificar se há mais capturas disponíveis
                self.valid_moves = self.board.get_valid_moves(self.board.get_piece(row, col))
                if any(skipped for skipped in self.valid_moves.values()):
                    # Ainda pode capturar mais peças
                    self.selected = self.board.get_piece(row, col)
                    self.waiting_for_animation = True
                    return True
                    
            self.change_turn()
        else:
            return False
        return True

    def change_turn(self):
        self.valid_moves = {}
        self.selected = None
        self.turn = BLACK if self.turn == WHITE else WHITE
        self.waiting_for_animation = False
        
        if len(self.board.get_all_valid_moves(self.turn)) == 0:
            winner = BLACK if self.turn == WHITE else WHITE
            player = "BRANCAS" if winner == WHITE else "PRETAS"
            draw_game_over(self.win, f"VITÓRIA DAS {player}!")
            self.reset()

    def ai_move(self, board):
        self.board = board
        self.change_turn()
        
    def is_animating(self):
        for row in self.board.board:
            for piece in row:
                if piece and piece.is_animating():
                    return True
        return False

def get_row_col_from_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

def check_draw_condition(board):
    # Contar peças brancas e pretas
    white_pieces = []
    black_pieces = []
    
    for row in board.board:
        for piece in row:
            if piece != 0:
                if piece.color == WHITE:
                    white_pieces.append(piece)
                else:
                    black_pieces.append(piece)
    
    # Verificar condições de empate
    if (len(white_pieces) == 1 and len(black_pieces) == 1 and
        white_pieces[0].king and black_pieces[0].king):
        return True
    return False

def draw_game_over(win, message):
    # Cria uma superfície semi-transparente
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Preto com transparência
    
    # Desenha o overlay
    win.blit(overlay, (0, 0))
    
    # Cria um retângulo central para a mensagem
    rect_width, rect_height = WIDTH - 100, HEIGHT // 3
    rect_x, rect_y = 50, (HEIGHT - rect_height) // 2
    pygame.draw.rect(win, (50, 50, 50), (rect_x, rect_y, rect_width, rect_height))
    pygame.draw.rect(win, GOLD, (rect_x, rect_y, rect_width, rect_height), 4)  # Borda dourada
    
    # Renderiza o texto principal
    font_large = pygame.font.SysFont('Arial', 21, bold=True)
    text_main = font_large.render(message, True, WHITE)
    text_rect = text_main.get_rect(center=(WIDTH//2, HEIGHT//2 - 20))
    win.blit(text_main, text_rect)
    
    # Texto secundário
    font_small = pygame.font.SysFont('Arial', 24)
    text_secondary = font_small.render("Clique para continuar", True, WHITE)
    text_sec_rect = text_secondary.get_rect(center=(WIDTH//2, HEIGHT//2 + 40))
    win.blit(text_secondary, text_sec_rect)
    
    pygame.display.update()
    
    # Espera pelo clique do mouse ou tecla
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                waiting = False
        
def main():
    run = True
    clock = pygame.time.Clock()
    game = Game(WIN)

    while run:
        clock.tick(60)
        
        # Esperar animações terminarem
        if game.is_animating():
            game.update()
            continue
        
        if game.turn == BLACK and not game.waiting_for_animation:
            _, new_board = minimax(game.board, 7, float('-inf'), float('inf'), False, game)
            game.ai_move(new_board)

        winner = game.board.winner()
        if winner is not None:
            text = "Vencedor: " + ("Branco" if winner == WHITE else "Preto")
            draw_winner(WIN, text)
            game.reset()
        

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN and not game.is_animating():
                pos = pygame.mouse.get_pos()
                row, col = get_row_col_from_mouse(pos)
                game.select(row, col)

        game.update()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()