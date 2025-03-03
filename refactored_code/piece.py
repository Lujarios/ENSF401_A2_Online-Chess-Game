import pygame
import os

PIECE_SIZE = (55, 55)
BOARD_SIZE = 8
COLOR_RED = (255, 0, 0)
BOARD_X = 113
BOARD_Y = 113
BOARD_WIDTH = 525
BOARD_HEIGHT = 525
HIGHLIGHT_SIZE = 62
BORDER_THICKNESS = 4

black_bishop_img = pygame.image.load(os.path.join("img", "black_bishop.png"))
black_king_img = pygame.image.load(os.path.join("img", "black_king.png"))
black_knight_img = pygame.image.load(os.path.join("img", "black_knight.png"))
black_pawn_img = pygame.image.load(os.path.join("img", "black_pawn.png"))
black_queen_img = pygame.image.load(os.path.join("img", "black_queen.png"))
black_rook_img = pygame.image.load(os.path.join("img", "black_rook.png"))

white_bishop_img = pygame.image.load(os.path.join("img", "white_bishop.png"))
white_king_img = pygame.image.load(os.path.join("img", "white_king.png"))
white_knight_img = pygame.image.load(os.path.join("img", "white_knight.png"))
white_pawn_img = pygame.image.load(os.path.join("img", "white_pawn.png"))
white_queen_img = pygame.image.load(os.path.join("img", "white_queen.png"))
white_rook_img = pygame.image.load(os.path.join("img", "white_rook.png"))

black_pieces = [black_bishop_img, black_king_img, black_knight_img, black_pawn_img, black_queen_img, black_rook_img]
white_pieces = [white_bishop_img, white_king_img, white_knight_img, white_pawn_img, white_queen_img, white_rook_img]

black_piece_images = []
white_piece_images = []

IMG_BISHOP = 0
IMG_KING = 1
IMG_KNIGHT = 2
IMG_PAWN = 3
IMG_QUEEN = 4
IMG_ROOK = 5

for img in black_pieces:
    black_piece_images.append(pygame.transform.scale(img, PIECE_SIZE))

for img in white_pieces:
    white_piece_images.append(pygame.transform.scale(img, PIECE_SIZE))


class Piece:
    img = -1
    board_rect = (BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT)
    start_x = board_rect[0]
    start_y = board_rect[1]

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.selected = False
        self.move_list = []
        self.king = False
        self.pawn = False

    def isSelected(self):
        return self.selected

    def update_valid_moves(self, board):
        self.move_list = self.valid_moves(board)

    def get_linear_moves(self, board, directions, max_distance=float('inf')):
        moves = []
        for dr, dc in directions:
            r, c = self.row + dr, self.col + dc
            steps = 0
            while 0 <= r < 8 and 0 <= c < 8 and steps < max_distance:
                piece = board[r][c]
                if piece == 0:
                    moves.append((c, r))
                elif piece.color != self.color:
                    moves.append((c, r))
                    break
                else:
                    break
                r += dr
                c += dc
                steps += 1
        return moves
    
    def get_single_moves(self, board, moves):
        valid_moves = []
        for dr, dc in moves:
            r, c = self.row + dr, self.col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                piece = board[r][c]
                if piece == 0 or piece.color != self.color:
                    valid_moves.append((c, r))
        return valid_moves

    def draw(self, win, color):
        if self.color == "w":
            drawThis = white_piece_images[self.img]
        else:
            drawThis = black_piece_images[self.img]

        x = (4 - self.col) + round(self.start_x + (self.col * self.board_rect[2] / BOARD_SIZE))
        y = 3 + round(self.start_y + (self.row * self.board_rect[3] / BOARD_SIZE))

        if self.selected and self.color == color:
            pygame.draw.board_rect(win, COLOR_RED, (x, y, HIGHLIGHT_SIZE, HIGHLIGHT_SIZE), BORDER_THICKNESS)

        win.blit(drawThis, (x, y))

        '''if self.selected and self.color == color:  # Remove false to draw dots
            moves = self.move_list

            for move in moves:
                x = 33 + round(self.start_x + (move[0] * self.board_rect[2] / BOARD_SIZE))
                y = 33 + round(self.start_y + (move[1] * self.board_rect[3] / BOARD_SIZE))
                pygame.draw.circle(win, (255, 0, 0), (x, y), 10)'''

    def change_pos(self, pos):
        self.row = pos[0]
        self.col = pos[1]

    def __str__(self):
        return str(self.col) + " " + str(self.row)


class Bishop(Piece):
    img = IMG_BISHOP

    def valid_moves(self, board):
        return self.get_linear_moves(board, [(1, 1), (-1, -1), (1, -1), (-1, 1)])


class King(Piece):
    img = IMG_KING

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.king = True

    def valid_moves(self, board):
        return self.get_single_moves(board, [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ])


class Knight(Piece):
    img = IMG_KNIGHT

    def valid_moves(self, board):
        return self.get_single_moves(board, [
            (-2, -1), (-2, 1), (2, -1), (2, 1),
            (-1, -2), (-1, 2), (1, -2), (1, 2)
        ])


class Pawn(Piece):
    img = IMG_PAWN

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.first = True
        self.pawn = True

    def valid_moves(self, board):
        moves = []
        direction = -1 if self.color == "w" else 1
        start_row = 6 if self.color == "w" else 1

        # Forward movement
        if 0 <= self.row + direction < 8 and board[self.row + direction][self.col] == 0:
            moves.append((self.col, self.row + direction))
            if self.row == start_row and board[self.row + 2 * direction][self.col] == 0:
                moves.append((self.col, self.row + 2 * direction))

        # Diagonal attack
        for dc in [-1, 1]:
            r, c = self.row + direction, self.col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] != 0 and board[r][c].color != self.color:
                    moves.append((c, r))

        return moves


class Queen(Piece):
    img = IMG_QUEEN

    def valid_moves(self, board):
        return self.get_linear_moves(board, [
            (1, 0), (-1, 0), (0, 1), (0, -1),  # Rook directions
            (1, 1), (-1, -1), (1, -1), (-1, 1) # Bishop directions
        ])


class Rook(Piece):
    img = IMG_ROOK

    def valid_moves(self, board):
        return self.get_linear_moves(board, [(1, 0), (-1, 0), (0, 1), (0, -1)])
