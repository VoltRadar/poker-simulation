# poker-simulation
Simulation of the game Texas Hold'em Poker using Python. Contains the ability to play over the internet and with AI

WARNING: This project has very limited testing related to security of its use of web sockets.
This was written as a school project, and may be vulnerable to seveal methods of attack.
I wouldn't use this program with a network or players you do not trust.


This project contains two parts: House.py, and Player.py

Running House.py creates a server for poker games on your machine. It is a single table,
which will always contain 3 AI players. Players can join anytime by typing in a server code,
displayed after every game. The server does all the processing of who has won, calculates
moves for the AI players, and deals with web traffic for the players. No game is played when
no player is connected.

Running player.py allows you to enter a server code, and connect to a poker server and start
playing. Iteraction is only via python termial.


Every 5 games, the minium bet is doubled. If an AI goes bankrupt, another AI takes there place

Python 3 is required to run the program
