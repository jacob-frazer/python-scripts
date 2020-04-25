# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 18:46:33 2019

@author: Jake Frazer
"""

import numpy as np

class hexapawn_agent:
    
    def __init__(self, player_id):
        ''' do I need to define some things in here?
        '''
        self.player_id = player_id
        self.moves = {}
        self.decision_matrix = {} #something in here
        self.seen_boards = []
        self.pawn_list = []
        
    
    def assign_pawns(self, pawns):
        for pawn in pawns:
            self.pawn_list.append(pawn)
        return
        
    
    def unassign_pawns(self):
        for pawn in self.pawn_list:
            del pawn
            
        self.pawn_list = []
        return
    
    def make_move(self, board):
        ''' randomly pick move based on decision matrix - updated as win lose. Causes good decisions to rise up and bad to fall down.
        '''
        random_pool = []
        seen, board_num = self.seen_board_state(board)
        
        if not seen:
            self.decision_matrix[board_num] = {}
        
            # creating decision_matrix for first seeing - dict that has board num, pawnnum, then a list of lists with moves and decision score SAME INDEX!
            for pawn_num, poss_move in self.potential_moves(board).items():
                self.decision_matrix[board_num][pawn_num] = [poss_move, [10 for x in poss_move]]        
            
        
        for pawn_num, moves_decision_list in self.decision_matrix[board_num].items():
            for index, move in enumerate(moves_decision_list[0]):
                random_pool += [(move, pawn_num)]*moves_decision_list[1][index]
        
        # no valid moves pass up the chain that agent lost
        if not random_pool:
            return 'no valid moves', 'no moves board'
        
        return random_pool[np.random.choice(len(random_pool))], board_num
        

    
    def update_decision_matrix(self, winner:bool, moves_made):
        ''' updates the decision matrix based on whether they won or lost. # list - (board num, (move type, pawn number) ) 
        '''
        
        for board_num, move in moves_made:
            
            # find appropriate move in decision matrix
            if winner:
                move_index = self.decision_matrix[board_num][move[1]][0].index(move[0])
                self.decision_matrix[board_num][move[1]][1][move_index] += 2
                
            else:
                move_index = self.decision_matrix[board_num][move[1]][0].index(move[0])
                # stop decision going below 1
                if self.decision_matrix[board_num][move[1]][1][move_index] > 2:
                    self.decision_matrix[board_num][move[1]][1][move_index] -= 2
                
        return
    
    
    
    def seen_board_state(self, board):
        ''' checking for if we know this board - checks all every time not efficient Also manipulates the array not efficient.
        '''
        i_to_change = []
        board = board.flatten()
        # making a repr without the object since diff memory addresses on subsequent games will break it.
        # some vals will be 0's some will be pawn objects
        for index, val in enumerate(board):
            if type(val) is pawn:
                i_to_change.append(index)
                
        for i in i_to_change:
            board[i] = board[i].owner
        
        board = np.reshape(board,(3,3))
            
        for i, seen_board in enumerate(self.seen_boards):
            if (board == seen_board).all():
                return True, i
        
        self.seen_boards.append(board)
        return False, len(self.seen_boards)-1
    
    
    
    def potential_moves(self, board):
        ''' state of the board and which player is moving. returns potential moves in a predictable fashion.
        if board state has been calculated before this won't need to run.
        
        pawn move guide -- 0 indicates diagonal take left -- 1 is move forward -- 2 is diagonal take right
        '''
        potential_moves_dict = {}
     
        for pawn in self.pawn_list:
#            print(pawn.taken)
            if pawn.taken:
                continue
            
            y, x = pawn.position

            # clear ahead
            if board[y+1][x] == 0:
                potential_moves_dict[pawn.pawn_id] = [1]
            # take left
            if x-1>-1:
                if board[y+1][x-1] != 0 and pawn.owner != board[y+1][x-1].owner:
                    potential_moves_dict[pawn.pawn_id] = potential_moves_dict.get(pawn.pawn_id,[]) + [0]
             # take right  
            if x+1<3:
                if board[y+1][x+1] != 0 and pawn.owner != board[y+1][x+1].owner:
                    potential_moves_dict[pawn.pawn_id] = potential_moves_dict.get(pawn.pawn_id,[]) + [2]
    
#        print(potential_moves_dict)
        return potential_moves_dict
        
    
    
class game:
    
    def __init__(self, agent1, agent2):
        ''' build board - 1 signifies.
        '''
        self.a1id = agent1.player_id
        self.a2id = agent2.player_id
        if self.a2id == self.a1id:
            raise ValueError('The ID of the two players is the same - this breaks the game.')
            
        # building and assigning pawn objects position is done unconventionally defined [0,0] y then x
        p0,p1,p2,p3,p4,p5 = pawn(self.a1id,[0,0],0),pawn(self.a1id,[0,1],1),pawn(self.a1id,[0,2],2),pawn(self.a2id,[2,0],3),pawn(self.a2id,[2,1],4),pawn(self.a2id,[2,2],5)
        agent1.assign_pawns([p0,p1,p2])
        agent2.assign_pawns([p3,p4,p5])
        self.board = np.array([[p0,p1,p2], [0,0,0], [p3,p4,p5]])
        self.moves_made = {}
        return
        
      
    def flip_board(self):
        self.board = np.flip(self.board,0)
        translation_dict = {0:2,1:1,2:0}
        
        # translating all pawn y positions too.
        for pawn in agent1.pawn_list:
            pawn.position[0] = translation_dict[pawn.position[0]]
            
        for pawn in agent2.pawn_list:
            pawn.position[0] = translation_dict[pawn.position[0]]
            
        return 
    
    
    def has_agent_won(self, player_id):
        ''' checks the win conditions - pawn to otherside, all opp pawns taken, no possible moves for opponent.
        checks whole board is there more efficient way to do this
        '''
        num_oppo_pawns = 0
        for y, row in enumerate(self.board):
            for x, position in enumerate(row):
                
                # pawn reached other side
                if y==2 and type(position) is pawn and position.owner==player_id:
                    return True
                
                if position != 0 and position.owner!=player_id:
                    num_oppo_pawns += 1
                    
        # killed all opponents pawns (0 left)
        if not num_oppo_pawns:
            return True
            
        return False
    
    
    def return_moves_made(self, player_id):
        # list - (board num, (move type, pawn number) ) )
        return self.moves_made[player_id]
    
    
    def log_move(self, agent, move, board_num):
        ''' logs move in dict w/ player id as key - actually carries out move
        '''
        
        if move == 'no valid moves':
            return
        
        if not self.moves_made.get(agent.player_id, False):
            self.moves_made[agent.player_id] = [(board_num,move)]
        else:
            self.moves_made[agent.player_id] += [(board_num,move)]
            
        for pawn in agent.pawn_list:
            
            if pawn.pawn_id == move[1]:
                # update pawn location and board
                y, x = pawn.position
                
                # move down
                if move[0] == 1:
                    pawn.position[0] = pawn.position[0]+1     
                #taking right
                if move[0] == 2:
                    pawn.position[0],pawn.position[1] = pawn.position[0]+1, pawn.position[1]+1        
                #taking left
                if move[0] == 0:
                    pawn.position[0],pawn.position[1] = pawn.position[0]+1, pawn.position[1]-1        
                
                # Add some taken flag to old pawn and update movd pawn and board
                new_y, new_x = pawn.position
                
                
                if self.board[new_y][new_x] != 0 and self.board[new_y][new_x] != agent.player_id:    # less elegant work around to the beneath block that doesnt work
                    self.board[new_y][new_x].toggle_taken()
                    
#                if type(self.board[new_y][new_x]) is pawn:                         # dont know why this doesn't work
#                    print('is this just never running?')
#                    self.board[new_y][new_x].toggle_taken()
                
                self.board[new_y][new_x] = pawn
                self.board[y][x] = 0
    
        return
    
    
    def display_board(self):
        for i in self.board:
            display = []
            for x in i:
                if type(x) is pawn:
                    display.append(x.owner)
                else:
                    display.append(x)
                    
            print(display)
        print(' ')
        return

    

class pawn:
    
    def __init__(self, player_id, position, pawn_id):
        ''' id is just who pawn belongs to. position is tuple that is position on board.
        '''
        self.owner = player_id
        self.position = position
        self.pawn_id = pawn_id
        self.taken = False
        
    def move(move_choice):
        ''' move choice will be a number that corresponds to a potential move in that board state.
        '''
        return
    
    def toggle_taken(self):
        ''' call this to toggle if the pawn has been taken - wont be looked at for potential moves.
        this isn't working right - delete object as it's taken?
        '''
        self.taken = True
        return
    
    
    
# actual script here
    
# build agents
agent1 = hexapawn_agent(1)
agent2 = hexapawn_agent(2)
winners = []

for i in range(1):     # looping the game over and over to teach the agents
    hx_game = game(agent1, agent2)
    
    while True:
        
        # code for player 1 playing
        p1move, board_num = agent1.make_move(hx_game.board)
        hx_game.log_move(agent1, p1move, board_num)
        
        if p1move == 'no valid moves':
            agent2.update_decision_matrix(True, hx_game.return_moves_made(agent2.player_id))
            agent1.update_decision_matrix(False, hx_game.return_moves_made(agent1.player_id))
            winner = agent2.player_id
            break
        
        if hx_game.has_agent_won(agent1.player_id):
            agent1.update_decision_matrix(True, hx_game.return_moves_made(agent1.player_id))
            agent2.update_decision_matrix(False, hx_game.return_moves_made(agent2.player_id))
            winner = agent1.player_id
            break
        
        hx_game.display_board()
        
        # flipping board for pov of other player
        hx_game.flip_board()
        
        
        p2move, board_num = agent2.make_move(hx_game.board)
        hx_game.log_move(agent2, p2move, board_num)
        
        
        
        if p2move == 'no valid moves':
            agent1.update_decision_matrix(True, hx_game.return_moves_made(agent1.player_id))
            agent2.update_decision_matrix(False, hx_game.return_moves_made(agent2.player_id))
            winner = agent1.player_id
            break
            
        if hx_game.has_agent_won(agent2.player_id):
            agent2.update_decision_matrix(True, hx_game.return_moves_made(agent2.player_id))
            agent1.update_decision_matrix(False, hx_game.return_moves_made(agent1.player_id))
            winner = agent2.player_id
            break
    
        # flipping board for pov of other player
        hx_game.flip_board()
        hx_game.display_board()
        
        
        
    
    # remove all pawn objects
    agent1.unassign_pawns()
    agent2.unassign_pawns()
    

    print('The winning agent was:',winner)
    print('final board state:')
    hx_game.display_board()
    winners.append(winner)
    
    
    