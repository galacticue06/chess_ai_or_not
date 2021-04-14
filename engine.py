import chess
from random import uniform, randint
from copy import deepcopy
import time
import sys

bo = chess.Board()
ps =  {chess.PAWN:100,chess.BISHOP:330,chess.KNIGHT:320,chess.ROOK:500,chess.QUEEN:975}


zobrists = []

def flat(arr):
    fl = []
    for i in arr:
        for j in i:
            fl.append(j)
    return fl

pawntable_w = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 1.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 1.0, 0.5, 0.5, 1.0, 2.5, 2.5, 1.0, 0.5, 0.5, 0.0, 0.0, 0.0, 2.0, 2.0, 0.0, 0.0, 0.0, 0.5, -0.5, -1.0, 0.0, 0.0, -1.0, -0.5, 0.5, 0.5, 1.0, 1.0, -2.0, -2.0, 1.0, 1.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
#pawntable_b = pawntable_w[::-1]
pawntable_b = pawntable_w
knighttable_w = [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0, -4.0, -2.0, 0.0, 0.0, 0.0, 0.0, -2.0, -4.0, -3.0, 0.0, 1.0, 1.5, 1.5, 1.0, 0.0, -3.0, -3.0, 0.5, 1.5, 2.0, 2.0, 1.5, 0.5, -3.0, -3.0, 0.0, 1.5, 2.0, 2.0, 1.5, 0.0, -3.0, -3.0, 0.5, 1.0, 1.5, 1.5, 1.0, 0.5, -3.0, -4.0, -2.0, 0.0, 0.5, 0.5, 0.0, -2.0, -4.0, -5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0]
#knighttable_b = knighttable_w[::-1]
knighttable_b = knighttable_w
bishoptable_w = [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0, -1.0, 0.0, 0.5, 1.0, 1.0, 0.5, 0.0, -1.0, -1.0, 0.5, 0.5, 1.0, 1.0, 0.5, 0.5, -1.0, -1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, -1.0, -1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.5, -1.0, -2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0]
#bishoptable_b = bishoptable_w[::-1]
bishoptable_b = bishoptable_w
rooktable_w = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5, -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5, -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5, -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5, -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5, -0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5, 0.0, 0.0, 0.0, 0.5, 0.5, 0.0, 0.0, 0.0]
#rooktable_b = rooktable_w[::-1]
rooktable_b = rooktable_w

def score(board):
    ret = sum([ps[i]*len(board.pieces(i,True)) for i in ps])-sum([ps[i]*len(board.pieces(i,False)) for i in ps])+uniform(-0.01,0.01)
    for j in board.pieces(chess.PAWN,True):
        ret += pawntable_w[j]
    for j in board.pieces(chess.PAWN,False):
        ret -= pawntable_b[j]
    for j in board.pieces(chess.KNIGHT,True):
        ret += knighttable_w[j]
    for j in board.pieces(chess.KNIGHT,False):
        ret -= knighttable_b[j]
    for j in board.pieces(chess.BISHOP,True):
        ret += bishoptable_w[j]
    for j in board.pieces(chess.BISHOP,False):
        ret -= bishoptable_b[j]
    for j in board.pieces(chess.ROOK,True):
        ret += rooktable_w[j]
    for j in board.pieces(chess.ROOK,False):
        ret -= rooktable_b[j] 
    return ret

def ev(b,maxim):
    if b.is_checkmate():
        if maxim:
            return 10000
        else:
            return -10000
    elif b.is_stalemate() or b.is_insufficient_material():
        return 0
    else:
        ret = score(b)
    return ret
    

def minimax_ab_zobrist(board,depth,maximizing=True,toMove=True,a=-10001,b=10001):
    if depth < 1:
        return ev(board,toMove),None
    legal = list(board.legal_moves)
    if maximizing:
        bests = -10000
        bestm = legal[0]
        for i in legal:
            nboard = deepcopy(board)
            nboard.push(i)
            zb = chess.polyglot.zobrist_hash(nboard)
            if zb not in zobrists:
                zobrists.append(zb)
                sc = minimax_ab_zobrist(nboard,depth-1,not maximizing,not toMove,a,b)[0]
                if sc > bests:
                    bests = sc
                    bestm = i
                    if sc > a:
                        a = sc
                        if a >= b:
                            break
            del nboard
    else:
        bests = 10000
        bestm = legal[0]
        for i in legal:
            nboard = deepcopy(board)
            nboard.push(i)
            zb = chess.polyglot.zobrist_hash(nboard)
            if zb not in zobrists:
                zobrists.append(zb)
                sc = minimax_ab_zobrist(nboard,depth-1,not maximizing,not toMove,a,b)[0]
                if sc < bests:
                    bests = sc
                    bestm = i
                    if sc < b:
                        b = sc
                        if b <= a:
                            break
            del nboard
    return bests, bestm
        
        

def minimax_ab(board,depth,maximizing=True,toMove=True,a=-10001,b=10001):
    if depth < 1:
        return ev(board,toMove),None
    legal = list(board.legal_moves)
    ll = len(legal)
    if maximizing:
        bests = -10000
        bestm = legal[0]
        for i in legal:
            board.push(i)
            sc = minimax_ab(board,depth-1,not maximizing,not toMove,a,b)[0]
            board.pop()
##            nboard = deepcopy(board)
##            nboard.push(i)
##            sc = minimax_ab(nboard,depth-1,not maximizing,not toMove,a,b)[0]
##            del nboard
            if sc > bests:
                bests = sc
                bestm = i
                if sc > a:
                    a = sc
                    if a > b:
                        break
            
    else:
        bests = 10000
        bestm = legal[0]
        for i in legal:
            board.push(i)
            sc = minimax_ab(board,depth-1,not maximizing,not toMove,a,b)[0]
            board.pop()
##            nboard = deepcopy(board)
##            nboard.push(i)
##            sc = minimax_ab(nboard,depth-1,not maximizing,not toMove,a,b)[0]
##            del nboard
            if sc < bests:
                bests = sc
                bestm = i
                if sc < b:
                    b = sc
                    if b < a:
                        break
            
    return bests, bestm, ll


def pts(board):
    for i in board.pieces(chess.QUEEN,True):
        print(((64-i)//8,i%8))
        

move = 0
time_limit = 0.6
dp = int(sys.argv[1])
while 1:
    run = time.time()
    move += 1
    try:
        if move % 2 == 1:
            mm = minimax_ab(bo,dp+1,True,True)
        else:
            mm = minimax_ab(bo,dp,False,True)
    except:
        if bo.is_checkmate():
            print('Checkmate:',bo.fen())
        else:
            print('An error occured.')
        input()
        exit()
    bo.push(mm[1])
    zobrists = []
    print(bo,'\nEval:',mm[0]/100,not (move % 2 == 1),'\n'*3)
    total = time.time()-run


