import House
import socket
import json
import random
from time import sleep


class MyPlayer:
    def __init__(self, testing=False, home_ip=False):
        self._my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if home_ip:  # Is the game hosted on the machine of the player?
            self._my_socket.connect((socket.gethostname(), 54321))
        else:
            self.enter_ip()

        self.game_summary = [0, []]  # List of players
        self.name = ""
        self.set_up_name(testing)
        self.hand = House.Hand()

    def enter_ip(self):
        while True:
            coded_ip = input("IP code: ")

            try:
                ip_int = int(coded_ip, 36)
            except ValueError:
                print("code not in correct format")
                continue

            if not (0 <= ip_int < 2 ** 32):
                print("code not in correct format")
                continue

            ip = ".".join([str(x) for x in House.int_to_base(ip_int, 256)])
            if len(ip.split(".")) != 4:
                print("Not correct ip code")
                continue
            try:
                self._my_socket.connect((ip, 54321))
                break
            except ConnectionRefusedError:
                print(coded_ip, "not correct! try again")
                continue

    def set_up_name(self, test=False):
        """To be called when a MyPlayer object is created, sets up the name with the sever,
        and gives the first summary. test to set the a defult name"""
        name_choice = ""
        mes = self._my_socket.recv(512).decode()
        if mes == "Send Name":
            mes = {"Accepted": False}
            while not mes["Accepted"]:
                if test:
                    NUMBER_LENGTH = 9
                    rand = str(int(random.random() * (10 ** NUMBER_LENGTH)))
                    while len(rand) < NUMBER_LENGTH:
                        rand = "0" + rand

                    name_choice = "Test" + rand
                else:
                    name_choice = input("Name > ")

                self._my_socket.send(json.dumps({"MyName": name_choice}).encode())
                mes = self._my_socket.recv(512).decode()
                try:
                    mes = json.loads(mes)
                except json.decoder.JSONDecodeError:
                    mes = {"Accepted": False}

                if not mes["Accepted"]:
                    print("Name not accepted because", mes["Error"])

        mes = self._my_socket.recv(2048).decode()
        try:
            mes = json.loads(mes)
        except json.decoder.JSONDecodeError:
            print("Decode error in sending summary\nmes:", mes)
            mes = [0, []]
            print("Decode error in sending summary")

        self.game_summary = mes
        self.name = name_choice
        print("My name:", self.name)

        print("Name Accepted :)")

    def quit_poker(self):
        self.send_to({"N": self.name, "Act": "Q"})
        self._my_socket.close()
        quit()

    def send_to(self, x):
        """Send a dictioary to the sever"""
        self._my_socket.send(json.dumps(x).encode())

    def make_bet(self, command):
        """To be called when the command to make a bet is resivened"""

        # Making sure that the command is what it's supposed
        if type(command) is not dict or "N" not in command or "yMoney" not in command or "MakeBet" not in command:
            print("Error in command")
            print(f"Command: {command}\nType: {type(command)}")
            return None

        if command["N"] != self.name:
            print("Incorrect name")
            print(f"Command: {command}")
            return None

        # command is in the correct format
        if command["MakeBet"] < command["yMoney"]:
            # will ask the player to make a bet between the min and max values
            made_error = False
            while True:
                print("----- Make Bet -----")
                print(f"Hand: {self.hand.str_hand(self.hand.hole)}  Table: {self.hand.str_hand(self.hand.on_table)}")
                inp = input(f"Make a bet (${command['MakeBet']} - ${command['yMoney']}) or fold (type: 'f') > ")

                if inp and inp[0].lower() == "f":
                    # Sends the fold command to the server
                    try:
                        self.send_to({"N": self.name, "Act": "F"})
                        break
                    except ConnectionAbortedError:
                        print("Connection timed out. Close the program")

                if inp and inp[0].lower() == "q":
                    self.quit_poker()

                try:
                    inp = int(inp)
                except ValueError:
                    print(f"INVALID: {inp} is not an valid input")
                    made_error = True
                    continue

                if not command['yMoney'] >= inp >= command["MakeBet"]:
                    print(f"INVALID: {inp} is not in between {command['MakeBet']} and {command['yMoney']}")
                    made_error = True
                    continue

                my_bet = {"N": self.name, "Act": "B", "Am": inp}
                self.send_to(my_bet)
                mes = self._my_socket.recv(512).decode()

                try:
                    mes = json.loads(mes)
                except json.JSONDecodeError:
                    print("mes makes a json decoding error", mes)
                    mes = ""
                    made_error = True

                if type(mes) is not dict:
                    print("mes not dict", mes)
                    print("I don't know now")
                    made_error = True

                if "Error" in mes:
                    print("Not accepted because", mes["Error"])
                    made_error = True

                if "Accepted" in mes and mes["Accepted"]:
                    if made_error:
                        print("Accepted!")
                    # Bet has been made and accepted
                    break

        else:
            # Will trigger if the only option the player has is to go all in
            while True:
                res = input(f"Go all in? (${command['yMoney']}) (y or n)> ")
                if not res:
                    continue

                if res[0].lower() == "y":
                    self.send_to({"N": self.name, "Act": "B", "Am": command["yMoney"]})
                elif res[0].lower() == "q":
                    self.quit_poker()
                else:
                    self.send_to({"N": self.name, "Act": "F"})

                mes = self._my_socket.recv(512)

                try:
                    mes = json.loads(mes)
                except json.JSONDecodeError:
                    print("Resoponce was not a json object:", mes)
                    raise Exception("Not json object")

                if type(mes) is not dict:
                    print("mes not dict. Mes:", mes)
                    raise Exception("Mes not dict")

                if "Error" in mes:
                    print("Not accepted because", mes["Error"])

                if "Accepted" in mes and mes["Accepted"]:
                    break

    @staticmethod
    def end_game(ending_info: tuple):
        """Displays and handles infomation form the end of the game"""
        print()
        print("Table: ", ", ".join(ending_info[4][i:i+2] for i in range(0, 10, 2)))
        longest = max([len(x) for x in ending_info[0]])

        for player_name, cards in ending_info[0].items():
            print(f"{player_name}{' ' * (longest + 1 - len(player_name))}: {cards[:2]}, {cards[2:]}")

        print(", ".join(ending_info[2]), f"won in total ${ending_info[1]} with a {ending_info[3]}")

    def play_poker_round(self):
        """Function to be run after the begin round command is heard"""
        print("Round Starting")
        # print("Game summary:", self.game_summary)

        blind_info = self._my_socket.recv(512).decode()
        blind_info = json.loads(blind_info)

        print("Players:")

        list_of_names = []
        for item in self.game_summary[1]:
            list_of_names.append(item[0] + f" ({item[1]}) ")

        max_length = max([len(x) for x in list_of_names])
        for i in range(len(list_of_names)):
            while len(list_of_names[i]) < max_length:
                list_of_names[i] += " "

        print("-" * 40)
        for i in range(len(list_of_names)):
            print(list_of_names[i] + f"${self.game_summary[1][i][2]}")
        print("-" * 40)

        print("")
        print(f"Small blind: {blind_info[1][0]} (${int(blind_info[2] / 2)})")
        print(f"Big blind: {blind_info[1][1]} (${blind_info[2]})")
        print()

        cards = blind_info[0]
        if len(cards) != 4:
            print(f"Cards not of length 4, but {len(cards)}: {cards}")

        cards = [cards[:2], cards[2:]]
        cards = [House.Card(c) for c in cards]
        self.hand.give_hole(cards)
        print(f"Cards: {self.hand.str_hand()}")

        # Loop to listen to responces
        # print("Start listening")
        while True:
            mes = self._my_socket.recv(2048).decode()
            # print("Mes", len(mes), mes)  # Used for debugging

            try:
                mes = json.loads(mes)
            except json.JSONDecodeError:
                print("resived command not a json object\nmes:", mes)
                raise Exception("Resived command is not a json object")

            if "N" in mes and mes["N"] != self.name and "Act" not in mes:
                print("I don't think that this should happen")
                print("mes:", mes, "Length:", len(mes))
                print("My name:", self.name)

            if "N" in mes and mes["N"] != self.name:
                print("***** ", end="")
                if mes["Act"] == "B":
                    print(f"{mes['N']} bets ${mes['Am']}", "*****")
                if mes["Act"] == "F":
                    print(mes["N"], "folds", "*****")
                if mes["Act"] == "Q":
                    print(mes["N"], "quits", "*****")

            if "MakeBet" in mes:
                self.make_bet(mes)

            if "cards" in mes:
                cards_str = mes["cards"]
                cards = [cards_str[i: i+2] for i in range(0, len(cards_str), 2)]
                cards = [House.Card(c) for c in cards]
                self.hand.on_table = cards
                
                print("\nTable:", self.hand.str_hand(self.hand.on_table), "\n")

            if "EndRound" in mes:
                self.end_game(mes["EndRound"])
                self.hand.clear()
                break

    def play_poker(self):
        """Main function to run"""
        while True:
            mes = self._my_socket.recv(512).decode()
            try:
                mes = json.loads(mes)
            except json.JSONDecodeError:
                mes = ""

            if "Start Round" in mes:
                self.game_summary = mes["Start Round"]
                self.play_poker_round()
            if "NoMoney" in mes:
                print("Run out of money")
                print("Quitting")
                sleep(1)
                for i in range(5):
                    print(f"{5-i}...")
                    sleep(1)
                break
                

if __name__ == '__main__':
    me = MyPlayer(testing=False, home_ip=True)
    me.play_poker()
