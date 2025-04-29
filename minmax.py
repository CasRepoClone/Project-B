import networkx as nx
import copy
import time 
import random



#/usr/bin/env python3
# -*- coding: utf-8 -*-
# Ai project game 'clobber' - 2025
# Using minmax algorithm to play the game
# Alpha Beta pruning


class Game():
    def __init__(self):
        self.turn = 'B'
        self.currentGameState = None

    def createBoard(self, width, height) -> None: 
        """Create a board of size width n height m and assign into gameState"""
        self.currentGameState = self.Board(width, height, self.turn)
    
    def newState(self, state=None):
        """Create a deep copy of a given state, or current game state"""
        if state is None:
            state = self.currentGameState
        return copy.deepcopy(state)

        
    def evaluateBoard(self, state, mode): # heuristic function -> moves available for each piece mode 1,2,3
        """HEURISTICS - Evaluate the board and return a score"""
        score = 0
        board = state.getBoard() # get the board from the state
        whiteScore = 0
        blackScore = 0
        if mode == 1: # heuristic 1 - russian politics / High priority target (kill the enemies piece with the most moves)
            for row in range(len(board)):
                for col in range(len(board[row])):
                    if board[row][col] == 'B': # black is maximising 
                        blackScore += len(state.getMoves(row, col)) # get all moves for the piece
                    elif board[row][col] == 'W': # white is minimising 
                        whiteScore += len(state.getMoves(row, col)) # get all moves for the piece as length and subtract from score
                    #print("row " + str(row) + " col " + str(col) + " score " + str(blackScore - whiteScore)) 
            score = blackScore - whiteScore 
           
            return score, blackScore, whiteScore # return the score and the scores for each player'
        
        if mode == 2: # heuristic 2 - pieces on the board
            for row in range(len(board)):
                for col in range(len(board[row])):
                    if board[row][col] == 'B':
                        blackScore += 1
                    elif board[row][col] == 'W':
                        whiteScore += 1
            score = blackScore - whiteScore
            return score, blackScore, whiteScore # return the score and the scores for each player'
        
        if mode == 3: # heuristic 3 - schrodingers cat (the score is either there or not there we dont know )
            for row in range(len(board)):
                for col in range(len(board[row])):
                    if board[row][col] == 'B':
                        # yes this will randomly just cut off branches - dont even ask why i did this 
                        if random.randint(0,1) == 1:
                            blackScore += len(state.getMoves(row, col)) 
                        else:
                            blackScore += 0
                    elif board[row][col] == 'W':
                        if random.randint(0,1) == 1:
                            whiteScore += len(state.getMoves(row, col)) 
                        else:
                            whiteScore += 0
            score = blackScore - whiteScore
        else:
            raise ValueError("Invalid mode")

    
    def minmax(self, state, depth, maximisingPlayer, mode, alpha=float('-inf'), beta=float('inf')):
        """Minimax algorithm with alpha-beta pruning"""
        # check endstate
        if depth == 0:
            score, blackMoves, whiteMoves = self.evaluateBoard(state, mode)
            if blackMoves == 0 or whiteMoves == 0:
                if blackMoves == 0:
                    return -1000, None  # Black loses
                elif whiteMoves == 0:
                    return 1000, None  # White loses
            return score, None
        
        #region Maximising
        if maximisingPlayer:
            # highest evaluation score set to inf
            maxEval = float('-inf')
            bestMove = None
            # get the current board state (recursive for each depth)
            board = state.getBoard()
            # for every piece 
            for row in range(len(board)):
                for col in range(len(board[row])):
                    # if its B (our maximising player)
                    if board[row][col] == 'B':
                        # get all the moves possible for this piece 
                        possibleMoves = state.getMoves(row, col)
                        # for every move it can do 
                        for move in possibleMoves:
                            # create a new state of that move being carried out 
                            newState = self.newState()
                            newState.movePiece(row, col, move[0], move[1])
                            # get the score at that depth 
                            eval, _ = self.minmax(newState, depth-1, False, mode, alpha, beta)
                            # if that depth is better than our highest seen depth (ab pruning)
                            if eval > maxEval: 
                                maxEval = eval # set it as our highest seen
                                bestMove = (row, col, move[0], move[1]) # save it as the best move
                            alpha = max(alpha, eval)  # update our alpha value 
                            if beta <= alpha:         # cut branch if less than or draw state to beta branch
                                break
                if beta <= alpha:  # cut outer branches
                    break
            return maxEval, bestMove
        #endregion
        #region Minimising
        else:
            minEval = float('inf')
            bestMove = None
            board = state.getBoard()
            for row in range(len(board)):
                for col in range(len(board[row])):
                    if board[row][col] == 'W':
                        possibleMoves = state.getMoves(row, col)
                        for move in possibleMoves:
                            newState = self.newState()
                            newState.movePiece(row, col, move[0], move[1])
                            eval, _ = self.minmax(newState, depth-1, True, mode, alpha, beta)
                            if eval < minEval:
                                minEval = eval
                                bestMove = (row, col, move[0], move[1])
                            beta = min(beta, eval)  # update beta
                            if beta <= alpha:       # cut branches 
                                break
                if beta <= alpha:  # cut outer branches 
                    break
            return minEval, bestMove
        #endregion

            


    class Board(): # Board class allows us to create multiple boards to check game state 
        def __init__(self, width, height, turn):
            self.dimensions = (width, height)
            self.board = []
            self._create() # Create the board
            self.turn = turn

        #region Board methods
        def _create(self) -> list:
            """On create function, create the board"""
            for row in range(self.dimensions[0]):
                current_row = []
                for col in range(self.dimensions[1]):
                    if (row + col) % 2 == 0:
                        current_row.append('W')  # White square
                    else:
                        current_row.append('B')  # Black square
                self.board.append(current_row)
            return self.board
        
        def getDimensions(self) -> tuple:
            return self.dimensions
        
        def getBoard(self) -> list:
            return self.board
        
        def printBoard(self) -> None:
            counter = 0 # for each row 
            for item in self.board:
                print(counter, end=" ")
                print(item)
                counter +=1
            print("\n")
            return None
        
    
        
        def getTeam(self, row, col) -> str:
            """Get the team of a piece at position (row, collumn)"""
            # we do not need to create a piece object for this
            # we can just return the team of the piece at that position
            ## this is used in getmove too if its not valid return false
            try:
                return self.board[row][collumn]
            except:
                return None # out of bounds

        def getMoves(self, row, collumn) -> list:
            # confirmed working 28/04/25
            """Get the possible moves for a piece at position (row, collumn)"""
            moves = []
            dimensions = (row, collumn)

            friendly = self.getTeam(row, collumn) # get the team of the piece at that position
            possibleMoves = [(row-1, collumn), (row+1, collumn), (row, collumn-1), (row, collumn+1)]
            for move in possibleMoves:
                if self.isValidMove(move[0], move[1], friendly) == True:
                    moves.append(move)
            return moves
            #  gen scores here and add to queue / heap
        def isValidMove(self, row, collumn, friendly) -> bool:
            """Check if a move is valid"""
            # Check bounds
            if row < 0 or row >= self.dimensions[0] or collumn < 0 or collumn >= self.dimensions[1]:
                return False
            piece = self.getBoard()[row][collumn]
            # Check if square contains an enemy piece (not empty and not friendly)
            if piece != ' ' and piece != friendly:
                return True
            else:
                return False
            
        
        def movePiece(self, row, collumn, newRow, newCollumn) -> None:
            posMoves = self.getMoves(row, collumn)
            if (newRow, newCollumn) in posMoves:
                self.board[newRow][newCollumn] = self.board[row][collumn] # move to new position 
                self.board[row][collumn] = " "  # Empty square from where we moved the piece
            else:
                raise ValueError("Invalid move")

       

        #endregion Board methods
       



class AI_Character():
    def __init__(self, name, depth, heuristic, maximising):
        self.name = name # white/black 
        self.maximising = maximising
        self.depth = depth # 2 standard
        self.heuristic = heuristic # 1 standard 

    def move(self):
        print(f"\nAI ({self.name}) is thinking...\n")
        time.sleep(3)
        
        # get the best move using minmax 
        score, bestMove = game.minmax(game.newState(), depth=self.depth, maximisingPlayer=self.maximising, mode=self.heuristic)

        if bestMove is None:
            return False

        fromRow, fromCol, toRow, toCol = bestMove
        # check win state and return win state
        return self.moveAndDisplay(fromRow, fromCol, toRow, toCol)

    def moveAndDisplay(self, fromRow, fromCol, toRow, toCol):
        print(f"({self.name})) moves from ({fromRow}, {fromCol}) to ({toRow}, {toCol})")
        game.currentGameState.movePiece(fromRow, fromCol, toRow, toCol)
        game.currentGameState.printBoard()
        return self.checkWinState()

    def checkWinState(self):
        _, blackMoves, whiteMoves = game.evaluateBoard(game.newState(), 1)
        if whiteMoves == 0:
            print("Black wins - White has no moves left.")
            exit()
            return False
        if blackMoves == 0:
            print("White wins - Black has no moves left.")
            exit()
            return False
        else:
            return True


humanVAI = False # set to true if you want to play against AI not AI v Ai

# if you cant move you lose 
if __name__ == "__main__":
    game = Game()
    width = 3
    height = 3
    game.createBoard(width, height)  # Create a 3x3 board
    game.currentGameState.printBoard()  # Show initial board

    if humanVAI:
        # Main LOOOP
        while True:
            # human moves 
            print("Your turn (you are Black 'B'):")
            try:
                # get inputs 

                # from
                fromRow = int(input("Enter row of piece to move: "))
                fromCol = int(input("Enter column of piece to move: "))

                # to
                toRow = int(input("Enter row to move to: "))
                toCol = int(input("Enter column to move to: "))

                possibleMoves = game.currentGameState.getMoves(fromRow, fromCol)
                if (toRow, toCol) not in possibleMoves:
                    print("Invalid move... Try again.\n")
                    game.currentGameState.printBoard()  # Show initial board
                    continue

                game.currentGameState.movePiece(fromRow, fromCol, toRow, toCol)
                game.currentGameState.printBoard()

            except Exception as e:
                print(f"Error: {e}")
                continue

            # Check if human wins
            _, blackMoves, whiteMoves = game.evaluateBoard(game.newState(), 1)
            if whiteMoves == 0:
                print("You win! White has no moves left.")
                break
            if blackMoves == 0:
                print("You lose! Black has no moves left.")
                break

            # AI move
            print("\nAI (White) is thinking...\n")
            
            score, bestMove = game.minmax(game.newState(), depth=2, maximisingPlayer=False)

            if bestMove is None:
                print("You win! AI has no moves left.")
                break

            fromRow, fromCol, toRow, toCol = bestMove
            print(f"AI moves from ({fromRow}, {fromCol}) to ({toRow}, {toCol})")
            time.sleep(2) # simulate thinking and help me see the issues 
            game.currentGameState.movePiece(fromRow, fromCol, toRow, toCol)
            game.currentGameState.printBoard()

            # Check if AI wins
            _, blackMoves, whiteMoves = game.evaluateBoard(game.newState(), 1)
            if blackMoves == 0:
                print("You lose! Black has no moves left.")
                break
            if whiteMoves == 0:
                print("You win!White has no moves left.")
                break
    else:

        W_heuristic = 2
        B_heuristic = 1
        black_ai = AI_Character("Black", 3, B_heuristic, True) # name depth heuristic 
        white_ai = AI_Character("white", 3, W_heuristic, False) # name depth heuristic 
        # 0 = no heuristic, 1 = moves available for each piece, 
        #2 = pieces on the board, 
        #3 = high priority target (kill the enemies piece with the most moves)
        
        while True:
        # Black moves 
            print("Ai turn - Black 'B'):")
            black_ai.move()
            print("Ai turn - White 'W'):")
            white_ai.move()
            
            

                

