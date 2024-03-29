import time
import random
import subprocess
import gc
import math
from node import treeNode
from functions import *
class mcts():
    def __init__(self, initialState, timeLimit=None, explorationConstant=math.sqrt(2),
                 rolloutPolicy=MCMC, biasConstant=1, n_init=1, killer_rate=0.5, simulation_depth=0, print_limit=5, show_variation=False):
        if timeLimit != None:

            self.originalExplorationConstant = explorationConstant
            self.timeLimit = timeLimit
            self.limitType = 'time'
        else:
                raise ValueError("Iteration limit must be greater than one")
        self.explorationConstant = explorationConstant
        self.n_init=n_init
        self.simulation_depth=simulation_depth
        self.rollout = rolloutPolicy
        self.biasConstant = biasConstant
        self.one_move_available = False
        self.killer_rate=killer_rate
        self.root = treeNode(initialState, None, 0, 0)
        self.print_limit=print_limit
        self.panic = False
        self.is_winning = False
        self.is_losing = False
        if show_variation == "True":
            self.show_variation = True
        else:
            self.show_variation=False

    def progressbar(self, time_left, prefix="", size=30):  # Python3.3+
        def show( time_left):
            time_spent = self.timeLimit/1000-time_left
            x = int(size * ((self.timeLimit/1000)-time_left)/(self.timeLimit/1000))
            print("{}[{}{}] {}".format(prefix, "#" * x, "." * (size - x),str("%.0f" % time_spent) + "s"))

        show( time_left)
    def print_analysis(self, board,time_left):
        childs = []
        for child in self.root.children.values():
            if child.numVisits != 0:
                v = child.totalReward / child.numVisits
                m = child.minmaxReward
                killer_and_average = (1 - self.killer_rate) * v + self.killer_rate * m
                childs.append((self.getAction(self.root, child).uci(),
                               "score:" + '%.2f' % (((((1-self.killer_rate)*child.totalReward / child.numVisits)+self.killer_rate*child.minmaxReward)) * 100) + "%", "iterations: " + str(child.numVisits)))

        childs = sorted(childs, key=lambda x: float(x[2][12:]), reverse=True)
        num_of_childs = len(childs)
        subprocess.run('cls', shell = True)
        print(board)
        print('')
        print('Analyzing position...')
        self.progressbar(time_left)
        print("Best moves:")
        for p in range (0,self.print_limit):
            if num_of_childs > p:
                print("{}: ".format(p+1) + childs[p][0] , childs[p][1] , childs[p][2])
            else:
                break

        print("Total iterations: " + str(self.root.numVisits-1))
        print("")
        if self.show_variation == True:
            variation = []
            node = self.root
            while node.num_children != 0:
                variation.append((self.getAction(node, self.getBestChildVisit(node))))
                node = self.getBestChildVisit(node)
            print('Best line:')
            for l in range(len(variation)):
                print("{}. {}, ".format(l+1,variation[l]), end="")
            print("")
            print("")
    def search(self):
        subprocess.run('cls', shell=True)
        time_start = float(time.time())
        timeLimit = time.time() + self.timeLimit / 1000
        total_time = float(timeLimit) - float(time_start)
        i = 0
        t = 0
        self.one_move_available = False
        if len(list(self.root.board.legal_moves)) == 1:
            self.one_move_available = True
        while time.time() < timeLimit:
            time_left = (timeLimit-time.time())
            time_spent = self.timeLimit/1000 - time_left
            self.executeRound()
            if i == 100 and self.one_move_available:
                return list(self.root.board.legal_moves)[0]

            if t < time_spent:
                self.bestChildVisit = self.getBestChildVisit(self.root)
                self.bestChildLCB = self.getBestChildLCB(self.root)
                self.print_analysis(self.root.board,timeLimit-time.time())
                t+=1
            i += 1

        return self.getAction(self.root, self.bestChildVisit)


    def executeRound(self):
        node = self.selectNode(self.root)
        reward = node.totalReward/node.numVisits
        self.backpropogate(node, reward)
        self.backpropagate_minmax(node, reward)

    def selectNode(self, node):
        #possible_draw = False
        if self.root.numVisits > 0:
            '''if self.root.totalReward / self.root.numVisits < 0.01:
                possible_draw = True'''
        while not node.isTerminal:
            '''if possible_draw == True:
                if node.parent is not None:
                    if node.parent.parent == self.root:
                        if node.board.can_claim_threefold_repetition():
                            node.isTerminal = True
                            node.minmaxReward = 0.5
                            node.minmaxReward = 1
                            node.numVisits = 10
                            return node
                if  node.parent == self.root:
                    if node.board.can_claim_threefold_repetition():
                        node.isTerminal = True
                        node.minmaxReward = 0.5
                        self.backpropagate_minmax(node, 0.5)
                        node = self.getBestChild(self.root, self.explorationConstant, self.biasConstant)'''
            if node.isFullyExpanded:
                node = self.getBestChild(node, self.explorationConstant, self.biasConstant)
            else:
                if node.add_node_picked or self.one_move_available is True or node == self.root:
                    newNode = self.expand(node)
                    node.iterations_sice_expanded = 0
                    node = self.getBestChild(node, self.explorationConstant, self.biasConstant)
                    if newNode == node:
                        node.parent.add_node_picked = True
                        return node
                    else:
                        node.parent.add_node_picked = False
                        node.parent.last_added_node = newNode
                else:
                    node.iterations_sice_expanded += 1
                    node = self.getBestChild(node, self.explorationConstant, self.biasConstant)
                    if node == node.parent.last_added_node or node.parent.iterations_sice_expanded > 0:
                        node.parent.add_node_picked = True
                        return node
        return node


    def expand(self,node):
        #pick the from square (piece) we are going to expand by selecting the highest value from the list of values of available moves dictionary in node position
        max_prob_from_val, max_prob_from_square = max((node.from_move_prob_dist_dict[key][0], key) for key in node.from_move_prob_dist_dict)
        #if it is the first time this piece has been picked in the node, generate a dictionary of available squares keys for this piece along with values generated by neural network
        if node.from_move_prob_dist_dict[max_prob_from_square][1] == None:
            node.from_move_prob_dist_dict[max_prob_from_square][1] = get_move_board(node.board, max_prob_from_square, node.splitted_dims_board, node.legal_moves)[0]
        #pick the to square for the piece by selecting the highest value
        to_move_prob_dist_dict = node.from_move_prob_dist_dict[max_prob_from_square][1]
        max_prob_to_val, max_prob_to_square = max((to_move_prob_dist_dict[key], key) for key in to_move_prob_dist_dict)
        #this it the move that is going to be expanded in node
        move_str = str(max_prob_from_square) + str(max_prob_to_square)
        #convert move string to move object
        move = chess.Move.from_uci(move_str)
        #add 'q' so it can be read as promotion in UCI when you move a piece from 7 to 8 or 2 to 1 rank and it is not a legal move (it was a pawn move)
        #this in fact is one of the engies slight flaws --- it can only 'see' queen promotions, which anyway is 99,9% of all promotions
        if str(max_prob_from_square)[1] == '7' and str(max_prob_to_square)[1] == '8' or str(max_prob_from_square)[1] == '2' and str(max_prob_to_square)[1] == '1':
            if move not in node.board.legal_moves:
                move=chess.Move.from_uci(move_str+'q')
        #set bias of the by multiplying the probability of piece being the best to move and square being the best to move the named piece to
        move_bias = max_prob_from_val*max_prob_to_val
        #subtract the value of square probability times piece probability from piece probability
        #this is important --- if we picked square that had big probability of being the best, there is also a big chance that the rest of moves are bad, therefore the overal probability of the piece is always the sum of remaining squares times initial piece probability
        a = max_prob_to_val*node.from_move_prob_dist_dict[max_prob_from_square][2]
        node.from_move_prob_dist_dict[max_prob_from_square][0] -= a
        #delete the square value so the same move cannot be expanded twice
        del to_move_prob_dist_dict[max_prob_to_square]
        #delete the piece value if all the available moves by the piece have already been expanded
        if not bool(node.from_move_prob_dist_dict[max_prob_from_square][1]):
            del node.from_move_prob_dist_dict[max_prob_from_square]
        #initialize new node object with position of new node being position of old node that had the selected move taken. Also set a bias for the new node.
        newNode = treeNode(node.takeAction(move), node, move_bias, self.n_init)
        #add new node as a children of the old node
        node.children[move] = newNode
        #set a value for the new node by simulating it
        val = self.rollout(newNode, self.simulation_depth)
        newNode.totalReward = val*self.n_init
        newNode.minmaxReward = val
        node.num_children += 1
        #if old node doesn't have any pieces to select, make it fully expanded so it can't be expanded anymore
        if not bool(node.from_move_prob_dist_dict):
            node.isFullyExpanded = True
        return newNode


    def backpropogate(self, node, reward):
        if not node.isTerminal:
            node=node.parent
            reward=1-reward
        while node is not None:
            node.totalReward += reward
            reward=1-reward
            node.numVisits += 1
            node = node.parent

    def backpropagate_minmax(self, node, reward):
        if node == self.root:
            node.minmaxReward = reward
            return
        if node.minmaxReward == -1:
            node.minmaxReward = reward
        node_reward = node.minmaxReward
        if 1-reward < node.parent.minmaxReward or node.parent.num_children == 1:
            node.minmaxReward = reward
            return self.backpropagate_minmax(node.parent, 1-reward)
        else:
            siblings_rewards = []
            for child in node.parent.children.values():
                child_reward = child.minmaxReward
                siblings_rewards.append(child_reward)
            max_reward = max(siblings_rewards)
            if node_reward == max_reward:
                siblings_rewards.remove(max_reward)
                siblings_rewards.append(reward)
                max_reward = max(siblings_rewards)
                node.minmaxReward = reward
                return self.backpropagate_minmax(node.parent, 1-max_reward)






    def getBestChild(self, node, explorationValue, biasValue):
        bestValue = float("-inf")
        bestNodes = []
        nodes = []
        values = []
        for child in node.children.values():
            if child.numVisits == 0:
                num_visits = 1
            else:
                num_visits = child.numVisits
            if node.numVisits ==0:
                node_num_visits = 1
            else:
                node_num_visits = node.numVisits

            v = child.totalReward / num_visits
            m = child.minmaxReward
            r = math.sqrt(2 * math.log(node_num_visits) / num_visits)
            H = child.move_bias
            nodeValue = v + H*(math.sqrt(node_num_visits)/num_visits)
            if nodeValue > bestValue:
                bestValue = nodeValue
                bestNodes = [child]
            elif nodeValue == bestValue:
                bestNodes.append(child)
        return random.choice(bestNodes)

    def getBestChildLCB(self, node):
        bestValue = float("-inf")
        bestNodes = []
        for child in node.children.values():
            #if (child.totalReward / child.numVisits) > 0.99:
                #v = child.minmaxReward
            #else:
            #v = child.numVisits
            visits = child.numVisits
            if visits == 0:
                visits =1
            #v = (child.totalReward / visits)-math.sqrt(2 * math.log(node.numVisits) / visits)
            r = (1-self.killer_rate) * (child.totalReward / child.numVisits) + self.killer_rate * child.minmaxReward
            v = r - self.explorationConstant * math.sqrt(2 * math.log(node.numVisits) / visits)
            #if r>0.99:
                #v = child.minmaxReward
            nodeValue = v
            #nodeValue = visits

            if nodeValue > bestValue:
                bestValue = nodeValue
                bestNodes = [child]
            elif nodeValue == bestValue:
                bestNodes.append(child)
        return random.choice(bestNodes)


    def getBestChildVisit(self,node):
        bestValue = float("-inf")
        bestNodes = []
        for child in node.children.values():
            #v = child.numVisits
            visits = child.numVisits
            if visits == 0:
                visits =1
            v=visits
            nodeValue = v

            if nodeValue > bestValue:
                bestValue = nodeValue
                bestNodes = [child]
            elif nodeValue == bestValue:
                bestNodes.append(child)
        return random.choice(bestNodes)
    def getBestChildKiller(self,node):
        bestValue = float("-inf")
        bestNodes = []
        for child in node.children.values():
            #nodeValue = child.minmaxReward - self.explorationConstant * math.sqrt(2 * math.log(node.numVisits) / child.numVisits)
            nodeValue = child.minmaxReward
            if nodeValue > bestValue:
                bestValue = nodeValue
                bestNodes = [child]
            elif nodeValue == bestValue:
                bestNodes.append(child)
        return random.choice(bestNodes)
    def getBestChildAverage(self,node):
        bestValue = float("-inf")
        bestNodes = []
        for child in node.children.values():
            nodeValue = child.totalReward/child.numVisits -  self.explorationConstant * math.sqrt(2 * math.log(node.numVisits) / child.numVisits)
            if nodeValue > bestValue:
                bestValue = nodeValue
                bestNodes = [child]
            elif nodeValue == bestValue:
                bestNodes.append(child)
        return random.choice(bestNodes)
    def getAction(self, root, bestChild):
        for action, node in root.children.items():
            if node is bestChild:
                return action


