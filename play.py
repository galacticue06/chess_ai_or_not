import chess
import chess.svg
import chess.polyglot
import time
import traceback
import chess.pgn
import chess.engine
from ctypes import *
import collections
from random import randint

counter = None

def refresh_counter():
    global counter
    counter = time.perf_counter()

nnue = cdll.LoadLibrary("./nnueprobe.dll")

nnue.nnue_init(b"nn-62ef826d1a6d.nnue")

piece_table_variety = 0
adaptive_deepining = 0.1

def flatten(arr):
    ret = []
    for i in arr:
        ret += i
    return ret

def agressiveness(board, toMove):
    sum_ = 0
    for i in range(64):
        sum_ += len(list(board.attackers(toMove, i)))-len(list(board.attackers(not toMove, i)))
    return sum_

def p_count(board):
    pcs = [board.piece_at(chess.parse_square(i)) for i in chess.SQUARE_NAMES]
    for i in range(pcs.count(None)):
        pcs.remove(None)
    return len(pcs)

def material(board):
    wp = len(board.pieces(chess.PAWN, chess.WHITE))
    bp = len(board.pieces(chess.PAWN, chess.BLACK))
    wn = len(board.pieces(chess.KNIGHT, chess.WHITE))
    bn = len(board.pieces(chess.KNIGHT, chess.BLACK))
    wb = len(board.pieces(chess.BISHOP, chess.WHITE))
    bb = len(board.pieces(chess.BISHOP, chess.BLACK))
    wr = len(board.pieces(chess.ROOK, chess.WHITE))
    br = len(board.pieces(chess.ROOK, chess.BLACK))
    wq = len(board.pieces(chess.QUEEN, chess.WHITE))
    bq = len(board.pieces(chess.QUEEN, chess.BLACK))

    return (100 * (wp - bp) + 320 * (wn - bn) + 330 * (wb - bb) + 500 * (wr - br) + 900 * (wq - bq))



def evaluate_board(board):
    if board.is_checkmate():
        if board.turn:
            return 99999999
        else:
            return -99999999
    if board.is_stalemate(): return 0
    elif board.can_claim_draw(): return 0
    elif board.is_insufficient_material(): return 0

    nneval = nnue.nnue_evaluate_fen(bytes(board.fen(), encoding='utf-8'))
    if not board.turn:
        nneval = -nneval

    pc = p_count(board)
    mb = material(board)
    nneval = (nneval*(pc+2)+mb*(30-pc))/2

    if board.is_check():
        nneval += 50

    if board.turn:
        return nneval
    else:
        return -nneval


def alphabeta(alpha, beta, depthleft):
    bestscore = -9999
    if (depthleft <= 0):
        return quiesce(alpha, beta)
    for move in board.legal_moves:
    #for move in sort_moves(list(board.legal_moves), board):
        cap = board.is_capture(move)
        che = board.is_check()
        board.push(move)
        score = -alphabeta(-beta, -alpha, depthleft - (0.25 if cap or che else 1))
        board.pop()
        if (score >= beta):
            return score
        if (score > bestscore):
            bestscore = score
        if (score > alpha):
            alpha = score
    return bestscore


def quiesce(alpha, beta):
    stand_pat = evaluate_board(board)
    if (stand_pat >= beta):
        return beta
    if (alpha < stand_pat):
        alpha = stand_pat

    for move in board.legal_moves:
        if board.is_capture(move):
            board.push(move)
            score = -quiesce(-beta, -alpha)
            board.pop()

            if (score >= beta):
                return beta
            if (score > alpha):
                alpha = score
    return alpha

def sort_moves(mvs, board):
    mvs.sort(key = lambda a: -1 if "x" in str(board.san(a)) else 0)
    return mvs

def sort_moves_with_mpv(mvs, board, mpv):
    mvs.sort(key = lambda a: -1 if "x" in str(board.san(a)) else 0)
    return mvs[0:mpv]

def root_moves(mvs, bo, co):
    best_moves = {}
    for i in mvs:
        bo.push(i)
        best_moves[agressiveness(board, bo.turn)] = i
        bo.pop()
    dc = {best_moves[i]:i for i in best_moves}
    best_moves = sorted(best_moves.values(), key = lambda a: dc[a])
    return best_moves[0:co]

def board_to_game(board):
    game = chess.pgn.Game()
    switchyard = collections.deque()
    while board.move_stack:
        switchyard.append(board.pop())

    game.setup(board)
    node = game

    while switchyard:
        move = switchyard.pop()
        node = node.add_variation(move)
        board.push(move)

    game.headers["Result"] = board.result()
    return game

def selectmove(board, depth, time_limit):
    refresh_counter()
    try:
        move = chess.polyglot.MemoryMappedReader("C:/Users/your_path/books/human.bin").weighted_choice(board).move
        return move
    except:
        bestMove = chess.Move.null()
        bestValue = -99999
        alpha = -100000
        beta = 100000
        legals = list(board.legal_moves)
        for move in legals:
            if time_limit < (time.perf_counter() - counter):
                break
            board.push(move)
            boardValue = -alphabeta(-beta, -alpha, depth - 1)
            if boardValue > bestValue:
                bestValue = boardValue
                bestMove = move
            if (boardValue > alpha):
                alpha = boardValue
            board.pop()
        return bestMove, bestValue

board = chess.Board()
print(board,"\n----------------")

try:
    while True:
        if board.is_checkmate() or board.is_stalemate() or board.is_insufficient_material():
            break
        move = selectmove(board, 2, time_limit=2)
        board.push(move[0])
        print(board,"\n----------------")
except:
    pass
print(board_to_game(board))
