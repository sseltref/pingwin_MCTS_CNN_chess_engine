import berserk
from main import pingwin_game
import chess
class Game():
    def __init__(self, client, game_id, increment, limit, colour, **kwargs):
        super().__init__(**kwargs)
        self.game_id = game_id
        self.client = client
        self.stream = client.bots.stream_game_state(game_id)
        self.current_state = next(self.stream)
        self.increment = increment
        self.limit = limit
        self.colour = colour
        self.first_move=True
        self.on_move = True


    def invoke_engine(self,board=chess.Board()):
        settings_file = 'settings.txt'
        settings = {}
        with open(settings_file) as f:
            for line in f:
                (key, val) = line.strip().split(' = ')
                settings[key] = val

        self.pingwin = pingwin_game(exploration_constant=float(settings['exploration_constant']),bias_constant=float(settings['bias_constant']),n_init=int(settings['init_node_visits']),initboard=board,killer_rate=float(settings['killer_rate']), simulation_depth=int(settings['simulation_depth']))
    def run(self):
        if self.colour == 'white':
            self.handle_state_change()
        for event in self.stream:
            if event['type'] == 'gameState':
                self.handle_state_change(event)
            elif event['type'] == 'chatLine':
                self.handle_chat_line(event)
    def read_move_made_by_opponent(self,game_state):
        move_made_by_opponent = game_state['moves'][-5:]
        if move_made_by_opponent[-1] == "q":
            move_made_by_opponent = move_made_by_opponent[-5:]
        else:
            move_made_by_opponent = move_made_by_opponent[-4:]
        return move_made_by_opponent
    def handle_state_change(self, game_state=None):
        if self.on_move==True:
            if self.first_move==True:
                if self.colour=='white':
                    self.invoke_engine()
                    move=self.pingwin.make_move(self.limit/100)
                    client.bots.make_move(self.game_id, move)
                    self.on_move=False
                else:
                    move_made_by_opponent = self.read_move_made_by_opponent(game_state)
                    board = chess.Board()
                    move = chess.Move.from_uci(move_made_by_opponent)
                    board.push(move)
                    self.invoke_engine(board)
                    move=self.pingwin.make_move(self.limit/50)
                    client.bots.make_move(self.game_id, move)
                    self.on_move = False
                self.first_move=False

            else:
                self.make_move(game_state)
        else:
            self.on_move = True
        pass

    def handle_chat_line(self, chat_line):
        pass
    def make_move(self, game_state):
        move_made_by_opponent = self.read_move_made_by_opponent(game_state)
        self.pingwin.read_opponent_move(move_made_by_opponent)
        if self.colour == 'white':
            time_left = game_state["wtime"]
        else:
            time_left = game_state["btime"]
        minutes_left = time_left.minute
        seconds_left = time_left.second
        time_left = int(minutes_left) * 60 + int(seconds_left)
        if self.pingwin.moves_made<16:
            move_time = (self.limit*0.5)/16 + self.increment *0.5
        elif self.pingwin.moves_made<31:
            move_time = (self.limit*0.3)/15 + self.increment
        else:
            move_time = time_left*0.1

        move = self.pingwin.make_move(move_time)
        client.bots.make_move(self.game_id, move)
        self.on_move = False

with open('token.txt') as f:
    token = f.read()
session = berserk.TokenSession(token)
client = berserk.Client(session=session)
challenge_accepted = False
for event in client.bots.stream_incoming_events():
    if event['type'] == 'challenge':
        client.bots.accept_challenge(event['challenge']['id'])
        increment=event['challenge']['timeControl']['increment']
        limit = event['challenge']['timeControl']['limit']
        challenge_accepted = True
    if event['type'] == 'gameStart' and challenge_accepted:
        game = Game(game_id=event['game']['gameId'], client=client,increment=increment,limit=limit,colour=event['game']['color'])
        game.run()