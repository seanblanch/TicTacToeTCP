# client.py
#Sean Blanchard
#3/23/2021
#COMP429 - Networking

import argparse, socket, logging
from TicTacToeEngine import TicTacToeEngine

# Comment out the line below to not print the INFO messages
logging.basicConfig(level=logging.INFO)


def recv_until(sock, suffix):
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


# The client program sets up its socket differently from the way a server does.
# Instead of binding to a port and listening, it uses connect() to attach the socket directly to the remote address.
def client(host, port):
    # connect
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect the socket to the port where the server is listening
    sock.connect((host, port))
    sock.setblocking(True)
    logging.info('Connect to server: ' + host + ' on port: ' + str(port))

    msg = recv_until(sock, b"\n").decode('utf-8')
    logging.info('Message: ' + msg)

    sendmsg = ('Test\n')
    sock.sendall(sendmsg.encode())

    # sock.send(b"Hi server!\n")

    ##START MESSAGES
    # quit
    # sock.close()
    moveOnBoard = ''
    gameOver = False
    while not gameOver:
        # print('We still here')
        # sock.sendall(b'Hello\n')
        # logging.info('Sent: Hello\n')
        # message = recv_until(sock, b"\n").decode('utf-8')
        # logging.info('received: ' + message + '\n')
        # sendmsg = ('Test\n')
        # sock.sendall(sendmsg.encode())

        # Recieve message from server requesting to move
        recieveMove = recv_until(sock, b"\n").decode('utf-8')
        logging.info(recieveMove)
        if recieveMove[0] == '6':

            # Recieve the board state from server
            boardState = recieveMove[2:11]
            boardState = [char for char in boardState]

            # Use the TicTacToeEngine to display the boardstate
            engine = TicTacToeEngine()
            engine.board = boardState
            engine.display_board()

            # Client checks if game is over,
            # if it is not over print Tie if recieve a T
            # or print if X or O won the game
            winner = engine.is_game_over()
            if winner != '-':
                gameOver = True
                if winner == 'T':
                    print(winner + "ie game")
                else:
                    print(winner + ' Won')
                continue

            moveOnBoard = input("Please enter your move on the board: ")
            sendMove = ('6:' + moveOnBoard + '\n')
            sock.sendall(bytes(sendMove.encode('utf-8')))

            if recieveMove[0] == '4':
                recieveError = recv_until(sock, b"\n").decode('utf-8')
                logging.info(recieveError)
                print('ERROR: Invalid move')
            else:
                logging.info(recieveMove)
                boardState = recieveMove[2:11]
                boardState = [char for char in boardState]

                # Use the TicTacToeEngine to display the boardstate
                engine = TicTacToeEngine()
                engine.board = boardState
                engine.display_board()

        elif recieveMove[0] == '7':
            gameOver = True
            # Recieve the board state from server
            boardState = recieveMove[2:11]
            boardState = [char for char in boardState]

            # Use the TicTacToeEngine to display the boardstate
            engine = TicTacToeEngine()
            engine.board = boardState
            engine.display_board()

            # Client checks if game is over by checking the last 11 characters,
            # which would either return a T for tie
            # or a X or 0 for who won
            # print Tie if recieve a T
            # or print if X or O won the game
            returnResult = (recieveMove[11])
            if returnResult == 'T':
                print(returnResult + "ie game")
            else:
                print(returnResult + ' Won')

        # Recieve the board state from server
        # recieveBoardState = recv_until(sock, b"\n").decode('utf-8')
        # logging.info(recieveBoardState)
        # boardState = recieveBoardState[2:11]
        # boardState = [char for char in boardState]

        # Use the TicTacToeEngine to display the boardstate
        # engine = TicTacToeEngine()
        # engine.board = boardState
        # engine.display_board()

        # if recieveMove[0] == '4':
        #    recieveError = recv_until(sock, b"\n").decode('utf-8')
        #    logging.info(recieveError)
        #    print('ERROR: Invalid move')


if __name__ == '__main__':
    port = 9016

    parser = argparse.ArgumentParser(description='Client')
    parser.add_argument('host', help='IP address of the server.')
    args = parser.parse_args()

    client(args.host, port)