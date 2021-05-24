# server.py - a simple threaded server
#Sean Blanchard
#3/23/2021
#COMP429 - Networking

import argparse, socket, logging, threading
from TicTacToeEngine import TicTacToeEngine

# Comment out the line below to not print the INFO messages
logging.basicConfig(level=logging.INFO)


class ClientThread(threading.Thread):
    def __init__(self, address, socket, thread_cond, ttte, player):
        threading.Thread.__init__(self)
        self.csock = socket
        self.address = address
        self.thread_cond = thread_cond
        self.ttte = ttte
        self.player = player

        logging.info('New thread!')

    # Function that handles thread condition
    # and makes clients wait for other clients move to make move
    def wait_for_turn(self):
        isWaiting = True
        while isWaiting:
            # When accessing critical data lock the other thread
            # from returning data until tread condition is done executing
            self.thread_cond.acquire()
            if self.ttte.x_turn and self.player == 'X':
                isWaiting = False
            elif (not self.ttte.x_turn) and (self.player == 'O'):
                isWaiting = False
            self.thread_cond.release()

    # Data is read from the connection with recv() and transmitted with sendall().
    def run(self):
        # send a message

        # send back player information
        string = ('Your player ' + self.player + '\n')
        self.csock.sendall(string.encode('utf-8'))

        # get a message
        msg = self.recv_until(self.csock, b"\n").decode('utf-8')
        logging.info("Message: " + msg)

        # EXCHANGE MESSAGES
        # opcode	operation
        # 1	START
        # 2	CONNECT
        # 3	DISCONNECT
        # 4	ERROR
        # 5	VALID
        # 6	MOVE
        # 7	END OF GAME
        # 8  BOARDSTATE

        # Values of Fields
        # moveOfBoard: A int value 0-9 that represents play positions on the board
        # stringOfBoard: Represents a string value of the board that the client can interpret and return a view of the tictactoe board that the user can read

        # disconnect
        # self.csock.close()
        # logging.info('Disconnect client.')

        # EXCHANGE MESSAGES
        # loop until game is signaled over with '-'
        gameContinue = True
        while gameContinue:
            stringOfBoard = ''
            boardState = ''
            # All game logic/processing goes in this loop
            # Also conditional lock
            # that makes it so that only one thread runs through this section at a time
            # thread_cond.acuquire / release
            #  will only allow one thread to communicate at one time
            # Server starts the game
            # Server connects to tictactoe engine -> call TicTacToeEngine
            # Prompt for a move
            self.wait_for_turn()

            # Prompt for a new move
            # and display the board before
            # users makes a new move
            self.thread_cond.acquire()
            stringOfBoard = "".join(self.ttte.board)
            promptMove = ('6:' + stringOfBoard + '\n')
            self.csock.sendall(bytes(promptMove.encode('utf-8')))
            self.thread_cond.release()

            # Server recieves move from client
            serverRecieveMove = self.recv_until(self.csock, b"\n").decode('utf-8')
            logging.info(serverRecieveMove)

            # Grab the move on the board
            grabMoveOnBoard = serverRecieveMove[2]
            # Convert it to a int
            intVersionGrabMoveOnBoard = int(grabMoveOnBoard)
            # Make it valid from 0-8
            intVersionGrabMoveOnBoard = intVersionGrabMoveOnBoard - 1

            stringOfBoard = ''
            boardState = ''
            self.thread_cond.acquire()
            # if move is valid, make the move
            if self.ttte.is_move_valid(intVersionGrabMoveOnBoard) == True:
                self.ttte.make_move(intVersionGrabMoveOnBoard)

                # If someone wins send the other client the final board state
                # and send another message that game is over
                winner = self.ttte.is_game_over()
                if winner != '-':
                    stringOfBoard = "".join(self.ttte.board)
                    endOfGame = ('7:' + stringOfBoard + winner + '\n')
                    self.csock.sendall(bytes(endOfGame.encode('utf-8')))
                    gameContinue = False
                else:
                    # convert the state of the board as a string
                    # and send the display the board to the client
                    stringOfBoard = "".join(self.ttte.board)
                    boardState = ('8:' + stringOfBoard + '\n')
                    self.csock.sendall(bytes(boardState.encode('utf-8')))
            # Else send an error to the client
            else:
                promptError = ('4\n')
                self.csock.sendall(bytes(promptError.encode('utf-8')))

            # self.thread_cond.release()

            # self.thread_cond.acquire()
            # gameContinue = self.ttte.is_game_over() is '-'
            self.thread_cond.release()

    def recv_until(self, sock, suffix):
        """Receive bytes over socket `sock` until we receive the `suffix`."""
        message = sock.recv(1024)
        if not message:
            raise EOFError('socket closed')
        while not message.endswith(suffix):
            data = sock.recv(1024)
            if not data:
                raise IOError('received {!r} then socket closed'.format(message))
            message += data
        return message


def server():
    # start serving (listening for clients)
    # Then bind() is used to associate the socket with the server address.
    # In this case, the address is localhost, referring to the current server, and the port number is 9001.
    port = 9016
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('localhost', port))

    # https://docs.python.org/3.8/library/threading.html#threading.Condition
    thread_cond = threading.Condition()
    # Game object being created
    ttte = TicTacToeEngine()

    Counter = 0
    player = ''
    # Wait for a connection
    # Calling listen() puts the socket into server mode, and accept() waits for an incoming connection
    while True:
        # Listen for incoming connection
        sock.listen(1)
        logging.info('Server is listening on port ' + str(port))

        # counter that makes first player player X or second player player O
        # have to restart server after game
        if Counter == 0:
            player = 'X'
            Counter += 1
        elif Counter == 1:
            player = 'O'

        # client has connected
        # accept() returns an open connection between the server and client, along with the address of the client.
        sc, sockname = sock.accept()
        logging.info('Accepted connection.')
        t = ClientThread(sockname, sc, thread_cond, ttte, player)
        t.start()


server()