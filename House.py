from random import choice, shuffle, random, sample
from time import time, sleep
from itertools import combinations
import json
from math import floor, log10
import threading
import socket
from typing import List, Any


def round_sig_figs(n, sig_figs):
    """Rounds a number 'n' to a given number of significant figures (sig_figs)"""
    return round(n, sig_figs - floor(log10(n)) - 1)


def int_to_base(integer, base=256):
    """Converts integer to a number in a given base"""
    if integer < 0:
        return False

    if 0 == integer:
        return [0]

    bytes_list = []
    i = 0
    while base ** (i + 1) < integer:
        i += 1

    for k in range(i, -1, -1):
        j = 0
        while (j + 1) * base ** k <= integer:
            j += 1

        integer -= j * base ** k
        bytes_list.append(j)

    return bytes_list


class Card:
    """
    Class for the card object. Has attributes that can be called to look at a cards face value or suit
    """

    def __init__(self, face=""):
        """
        Takes the input of a card in the form of a string (eg 'JC' or 'TH' or '6D'). Random face if input left emtpy
        returns a card object.
        """
        if face and len(face) == 2:
            if face[0] in "SCDH":  # corrects the order if the user has entered the card incorrectly
                face = face[::-1]

            self.face = face.upper()

        else:
            self.face = choice("23456789TJQKA") + choice("SCDH")  # Randomly genarates a card

        self.value = self.face[0]
        self.suit = self.face[1]
        self.face_value = "23456789TJQKA".index(self.value)


class Deck:
    """
    An object to simulate a deck of cards. Has attributes and methods for shuffling the deck and
    returning a given number of cards
    """

    def __init__(self, shuffled=False):
        """
        Input suffled -> boolean
        if suffled is True then the deck will be shuffled after genarated
        """
        self.deck = []
        for suit in "SCDH":
            for value in "23456789TJQKA":
                self.deck.append(Card(value + suit))

        if shuffled:
            shuffle(self.deck)

    def take(self):
        """Takes the first card of the deck and returns it. Returns false if there are not cards in the deck"""
        try:
            return self.deck.pop(0)
        except IndexError:
            return False

    def take_n(self, number):
        """
        number -> int
        returns list: list of cards of length number.

        Takes a given number of cards off the deck and returns it in a list
        If number is larger then the amount of cards in the deck then some items in the list will be false
        """
        return [self.take() for _ in range(number)]

    def add(self, card):
        """
        card -> Card object
        Adds a Card object to the END of the deck. if input is not Card object then will not be added to deck
        returns True if the input is a Card object, returns False if input is not Card object
        """
        if type(card) is not Card:
            return False

        self.deck.append(card)
        return True

    def shuffle_deck(self):
        """Shuffles the deck"""
        shuffle(self.deck)

    def str_deck(self, mn=0, mx=-1):
        """
        Returns a nice looking string from given part of deck. in form 'JH, 5D, TC, 7S, ...'
        mn -> int: is the index of the first card to include in the string. Defaults to the start of the deck
        mx -> int: is the index of the first card to NOT include in the string. Defaults to inlude the end of the deck.
        """
        if mx < 0 or type(mx) is not int:
            mx = len(self.deck)
        if mn < 0 or type(mn) is not int:
            mx = 0

        string = ", ".join([card.face for card in self.deck[mn: mx]])

        return string

    def remove_card(self, card):
        """
        Removes a given card form the deck
        card -> Card or string in form 'QH', 'TS', '3C'
        """
        deck_str = self.str_deck()
        if type(card) is Card:  # Convets card from a Card object to string
            card = card.face

        deck_str = deck_str.split(", ")
        try:
            deck_str.remove(card)
        except ValueError:
            return False

        self.deck = list(map(Card, deck_str))  # Converts a list of strings to a list of cards
        return True


def get_value(value):
    """
    Returns int the value of the a card, unless value is not in a valid format, in which case it returns false
    value -> Card, string
    """
    if type(value) is Card:
        value = value.face

    if type(value) is str:
        value = value[0]

    if type(value) is not str:
        return False

    return "23456789TJQKA".index(value)


class Hand:
    """
    Simulates a hand of poker. Contains infomation on the hole cards (the 2 cards that only one player can see),
    and the table cards, which is up to 5 cards that every player can see.
    """

    def __init__(self, hole=None, on_table=None):
        """
        Creates a hand object. hole is a list of cards that the player has, on_table is the list of cards that all
        other players can see. If hole or on_table are not specified, then the values default to empty lists
        """
        self.hand_types = ["RoyalF", "StraightF", "4OAK", "FullH", "Flush", "Straight", "3OAK", "2Pair", "Pair", "High"]
        if hole is None:
            self.hole = []

        if on_table is None:
            on_table = []

        self.hole = hole
        self.on_table = on_table

    def clear(self):
        """Clears the hole and the table cards"""
        self.hole = []
        self.on_table = []

    def give_hole(self, hole):
        """Gives a player their hole cards"""
        self.hole = hole[:]

    def hand_values(self, h=None, sort=True):
        """
        Returns the string of values of cards in a given hand e.g if the hand had the cards KH, 6H, 7C, then it will
        return "K67". If sort is True, then it will return the string, but sorted, so "67K"
         if no hand is specified, then the hand will be the current hand.
        """
        if h is None:
            h = self.in_play()

        output = []
        for card in h:
            output.append(card.value)

        if sort:
            output.sort(key=lambda x: "23456789TJQKA".index(x))

        output_str = ""
        for item in output:
            output_str += item

        return output_str

    def hand_suits(self, h=None):
        """
        Returns the string of suits in order. If there is no hand in the input, the value h will default to the
        the current hand
        """
        if h is None:
            h = self.in_play()

        output = []
        for card in h:
            output.append(card.suit)

        output_str = ""
        for item in output:
            output_str += item

        return output_str

    def add(self, card):
        """Adds a given card into the table"""
        self.on_table.append(card)

    def in_play(self):
        """Return the list of all the cards that are in play"""
        return self.hole + self.on_table

    def str_hand(self, h=None):
        """Outputs a nicly formated string of all cards of in play. If a value for h is a list a """
        output = ""

        if h is None or type(h) is not list:
            h = self.in_play()

        for item in h:
            output += item.face + ", "

        return output.strip(", ")

    def sort_hand(self):
        """Returns the full list of cards in play, sorted by value"""
        return sorted(self.in_play(), key=lambda x: "23456789TJQKA".index(x.value))

    def is_straight(self, cards):
        """Takes an input of 5 cards and returns weather or not it's a stright"""
        values = self.hand_values(cards)
        if values in "23456789TJQKA":
            return True

        if values in ["2JQKA", "23QKA", "234KA", "2345A"]:
            return True

        return False

    def combo(self):
        """Returns all the 5 card combonates of a hand with length 5 to 7"""
        hand_combinations = []
        sorted_hand = self.sort_hand()

        if len(sorted_hand) > 7:
            print("Combo has problem")
            return []
        if len(sorted_hand) == 5:
            hand_combinations.append(sorted_hand)

        elif len(sorted_hand) == 6:
            index = 0
            while index < 6:
                copy = sorted_hand[:]
                copy.pop(index)
                hand_combinations.append(copy)
                index += 1

        elif len(sorted_hand) == 7:
            indexs = [0, 1]
            done = False
            while not done:
                copy = sorted_hand[:]
                copy.pop(indexs[0])
                copy.pop(indexs[1] - 1)
                hand_combinations.append(copy)

                if indexs == [5, 6]:
                    done = True

                elif indexs[1] == 6:
                    indexs[0] += 1
                    indexs[1] = indexs[0] + 1

                else:
                    indexs[1] += 1
        return hand_combinations

    def pair(self, full_hand=None):
        """
        Returns highest pair of cards from a list of cards; full_hand. If no full_hand is specifyed, the full_hand defaults
        to the current hand
        """
        if full_hand is None:
            full_hand = self.in_play()

        pairs = []
        for combo in combinations(full_hand, 2):
            if combo[0].value == combo[1].value:
                pairs.append(combo)

        if pairs:
            pairs = sorted(pairs, key=lambda x: x[0].face_value)
            return pairs[-1]
        else:
            return False

    def best(self):
        """
        Returns the best hand from a given hand.
        output in the form of a tuple of (type, value, cards)
        type: hand type eg. 2pair, straight, flush
        value: tells how strong a hand is. changes format depending on the type of hand
        cards: all the involved in the hand

        table of types and corresponding hand values
        Hand type | description
        ---------------------------
        RoyalF    | the suit that the royal flush is in
        StrightF  | 5 characters of the values of the cards in the suit, sorted by value
        4OAK      | the value of the card that is a 4 of a kind
        FullH     | 2 characters. Values of the card with 3, 2 values eg. KKAKA would be 'KA'
        Flush     | 5 characters of the values of the cards in the flush, sorted by value
        Straight  | 5 characters  of the values of the cards in the straight, sorted by value
        3OAK      | the value of the card that there is 3 of
        2Pair     | the values of the cards in the pairs, in order in value
        Pair      | the value of the card of the pair
        High      | the value of the highest card
        """
        for t in self.hand_types:
            # Loop though each type and check the hand for the best thing in a hand
            if t == "RoyalF":
                # 1 find all states of all TJQKA

                l: List[Any] = self.sort_hand()

                while l and "23456789TJQKA".index(l[0].value) < "23456789TJQKA".index("T"):
                    l.pop(0)

                all_present = True  # Weather or not all of T, J, Q, K, A are in the hand
                values = self.hand_values(l)
                for v in "TJQKA":
                    if v not in values:
                        all_present = False
                        break

                if len(l) >= 5 and all_present:
                    strates = []
                    if len(l) == 5:
                        strates.append(l)

                    if len(l) == 6:
                        last = ""
                        repeated = ""
                        for i in range(6):
                            if last == l[i].value:
                                repeated = last
                                break
                            last = l[i].value

                        repeated_index = values.index(repeated)
                        strates.append(l[:repeated_index] + l[repeated_index + 1:])
                        strates.append(l[:repeated_index + 1] + l[repeated_index + 2:])

                    if len(l) == 7:
                        last = []  # List of index of repeated values of cards
                        for i in range(6):
                            if l[i].value == l[i + 1].value:
                                last.append(i)

                        if last[1] - last[0] == 1:
                            x = last[0]
                            left = l[:x]
                            right = l[x + 3:]
                            mid = l[x: x + 3]
                            for i in range(3):
                                strates.append(left + [mid[i]] + right)

                        else:
                            for i in range(4):
                                l_copy = l[:]

                                if i % 2:
                                    l_copy.pop(last[0])
                                else:
                                    l_copy.pop(last[0] + 1)

                                if i // 2:
                                    l_copy.pop(last[1] - 1)
                                else:
                                    l_copy.pop(last[1])

                                strates.append(l_copy)

                    # Found all possible royal flushes
                    for s in strates:
                        i = 0
                        while i < 4 and s[i].suit == s[i + 1].suit:
                            i += 1

                        if i == 4:
                            return t, s[0].suit, s

            if t == "StraightF":
                flushes = []

                for copy in self.combo():

                    if self.is_straight(copy):  # If it is a straight
                        flush = True
                        for x in range(4):
                            if copy[x].suit != copy[x + 1].suit:
                                flush = False
                                break

                        if flush:
                            flushes.append(copy)

                if flushes:
                    highest = flushes[0]
                    for flu in flushes[1:]:
                        # is flu sorted?
                        s_ranking = ["2345A", "23456", "34567", "45678", "56789", "6789T", "789TJ", "89TJQ", "9TJQK",
                                     "234KA", "23QKA", "2JQKA"]

                        if self.hand_values(highest) in s_ranking:
                            highest_ranking = s_ranking.index(self.hand_values(highest))
                        else:
                            highest_ranking = 20

                        if self.hand_values(flu) in s_ranking:
                            flu_ranking = s_ranking.index(self.hand_values(highest))
                        else:
                            flu_ranking = 20

                        if flu_ranking > highest_ranking:
                            highest = flu

                    return t, self.hand_values(highest), highest

            if t == "4OAK":
                string = self.hand_values(sort=False)
                counts = {}
                for chrt in string:
                    counts[chrt] = string.count(chrt)

                repeated = ""
                for value, count in counts.items():
                    if count == 4:
                        repeated = value

                if repeated:
                    indexs = []
                    for i in range(len(string)):
                        if string[i] == repeated:
                            indexs.append(i)

                    if len(indexs) == 4:
                        cards = []
                        for index in indexs:
                            cards.append(self.in_play()[index])

                        return t, cards[0].value, cards

            if t == "FullH":
                houses = []
                for copy in self.combo():
                    string = self.hand_values(copy)
                    low_first = string[0] * 2 + string[2] * 3
                    high_first = string[0] * 3 + string[3] * 2
                    if string == low_first or string == high_first:
                        houses.append(copy)

                if houses:
                    highest_house = houses[0]
                    low = self.hand_values(highest_house)[0]
                    high = self.hand_values(highest_house)[-1]
                    mid = self.hand_values(highest_house)[2]  # the vaule of the card there is 3 of
                    for house in houses[1:]:
                        string = self.hand_values(house)
                        if "23456789TJQKA".index(mid) < "23456789TJQKA".index(string[2]):
                            highest_house = house
                            low = self.hand_values(highest_house)[0]
                            high = self.hand_values(highest_house)[-1]
                            mid = self.hand_values(highest_house)[2]
                        elif "23456789TJQKA".index(mid) == "23456789TJQKA".index(string[2]):
                            if mid == low:
                                two = high  # two is the vaule of the card there is 2 of
                            else:
                                two = low

                            if string[2] == string[0]:
                                two_of_check = string[-1]
                            else:
                                two_of_check = string[0]

                            if "23456789TJQKA".index(two) < "23456789TJQKA".index(two_of_check):
                                highest_house = house
                                low = self.hand_values(highest_house)[0]
                                high = self.hand_values(highest_house)[-1]
                                mid = self.hand_values(highest_house)[2]

                    if mid == low:
                        two = high  # two is the vaule of the card there is 2 of
                    else:
                        two = low
                    return t, mid + two, highest_house

            if t == "Flush":
                flushs = []
                for combo in self.combo():
                    fs = ["SSSSS", "HHHHH", "DDDDD", "CCCCC"]
                    if self.hand_suits(combo) in fs:
                        flushs.append(combo)

                if flushs:
                    highest = flushs[0]
                    for flu in flushs[1:]:
                        i = 1
                        while i < 5 and get_value(self.hand_values(highest)[-i]) == get_value(
                                self.hand_values(flu)[-i]):
                            i += 1

                        if get_value(self.hand_values(highest)[-i]) < get_value(self.hand_values(flu)[-i]):
                            highest = flu

                    return t, self.hand_values(highest), highest

            if t == "Straight":
                straights = []
                for com in self.combo():
                    if self.is_straight(com):
                        straights.append(com)

                if straights:
                    highest = straights[0]
                    for flu in straights[1:]:
                        # is flu sorted?
                        s_ranking = ["2345A", "23456", "34567", "45678", "56789", "6789T", "789TJ", "89TJQ", "9TJQK"]

                        if self.hand_values(highest) in s_ranking:
                            highest_ranking = s_ranking.index(self.hand_values(highest))
                        else:
                            highest_ranking = 20

                        if self.hand_values(flu) in s_ranking:
                            flu_ranking = s_ranking.index(self.hand_values(flu))
                        else:
                            flu_ranking = 20

                        if flu_ranking > highest_ranking:
                            highest = flu

                    return t, self.hand_values(highest), highest

            if t == "3OAK":
                string = self.hand_values(sort=False)
                counts = {}
                for chrt in string:
                    counts[chrt] = string.count(chrt)

                repeated = ""
                for value, count in counts.items():
                    if count == 3:
                        repeated = value

                if repeated:
                    indexs = []
                    for i in range(len(string)):
                        if string[i] == repeated:
                            indexs.append(i)

                    if len(indexs) == 3:
                        cards = []
                        for index in indexs:
                            cards.append(self.in_play()[index])

                        return t, cards[0].value, cards

            if t == "2Pair":
                first = self.pair()
                if first:
                    hand = self.in_play()
                    for item in first:
                        hand.remove(item)

                    second = self.pair(hand)
                    if second:
                        first_value = first[0].value
                        second_value = second[0].value

                        if "23456789TJQKA".index(first_value) > "23456789TJQKA".index(second_value):
                            string = first_value + second_value
                        else:
                            string = second_value + first_value

                        return t, string, first + second

            if t == "Pair":
                pair = self.pair()
                if pair:
                    return t, pair[0].value, list(pair)

            if t == "High":
                highest = self.in_play()[0]
                for card in self.in_play()[1:]:
                    if card.face_value > highest.face_value:
                        highest = card
                return t, highest.value, [highest]


class Player:
    """
    This is a class that contains all methods and atrublues that
    are available to any player, AI or Human
    """

    def __init__(self, name="", min_bet=None):
        """
        Creates a player object. name is the players name. min_bet is the current minimum bet requirement
        for the game. The player will be given 1000 times the minimum bet
        """
        if min_bet is None:
            min_bet = 10
        self.hand = Hand()
        self.name = name
        self.money = 10 ** 3 * min_bet

    def give_hole(self, cards):
        """Given the player their hole cards. input must be a list of 2 card objects"""
        self.hand.give_hole(cards)

    def add_flop(self, flop):
        """Gives the player the flop cards that are on the table. flop is a list of cards"""
        for item in flop:
            if type(item) is Card:
                self.hand.add(item)

    def add_turn(self, turn_card):
        """Adds one card to the table in the players hand"""
        self.hand.add(turn_card)

    def add_river(self, river_card):
        """Adds one card to the table in the players hand."""
        self.hand.add(river_card)

    def bet(self, amount_to_bet):
        """
        Decrements the players money by a given amount. Returns True if the player is able to make the bet, False
        Otherwise
        """
        if self.money >= amount_to_bet:
            self.money -= amount_to_bet
            return True
        else:
            return False

    def ask_bet(self, min_bet):
        """To be called when the player needs to make a bet. Will be overwritten by the subclasses of Player."""
        return False  # This should never trigger

    def fold(self, reason=""):
        """
        Returns a fold action, and prints what cards the player has. Also prints a reason for folding if a reason
        is given
        """
        string = self.name + " folds with a " + self.hand.str_hand()
        if reason:
            string += " due to " + reason
        print(string)
        return {"N": self.name, "Act": "F"}


class Human(Player):
    """Subclass of Player. One Human object will be created for each non-AI player in the game"""

    def __init__(self, name, player_socket: socket.socket, min_bet=None):
        """
        Creates a Human object. name is a string, player_socket is a socket object, and min_bet is a int
        player_socket is the end point for the connection on the client side
        """
        Player.__init__(self, name, min_bet=min_bet)
        self._player_socket = player_socket

    def send_summary(self, summary):
        """
        Sends an json encoded object to the player. Returns True if the object is sent successfully, returns False
        otherwise
        """
        try:
            self._player_socket.send(json.dumps(summary).encode())
            return True
        except ConnectionResetError or ConnectionAbortedError:
            return False

    def update(self, res):
        """
        Updates the player on the action (res) of another player.
        If the action is one that the player made, then it will not send the infomation
        Returns True if res was send successfully, returns False otherwise
        """
        if "N" in res and res["N"] != self.name:
            # print("Sending", res, "to", self.name)
            did_send = self.send_summary(res)
            if not did_send:
                return False
            else:
                return True
        else:
            # print("Not sending", res, "to", self.name, " Res:", res)
            return True

    def ask_bet(self, min_bet):
        """
        Asks a human player for a bet. Returns a dictionary with the betting infomation.
        Returns the bet equivlant to quit ({"N": self.name, "Act": "Q"}) if a error occurs with the connection
        """
        sleep(0.1)
        while True:
            try:
                self.send_summary({"N": self.name, "MakeBet": min_bet, "yMoney": self.money})
            except ConnectionResetError or ConnectionAbortedError:
                return {"N": self.name, "Act": "Q"}

            try:
                mes = self._player_socket.recv(512).decode()
            except ConnectionResetError or ConnectionAbortedError:
                return {"N": self.name, "Act": "Q"}
            except socket.timeout:
                print(self.name, "timed out")
                self._player_socket.close()
                return {"N": self.name, "Act": "Q"}

            # Send a reqeast to the player, and wait for a response

            try:
                mes = json.loads(mes)
            except json.JSONDecodeError:
                print("Json Decode error")
                try:
                    self._player_socket.send(json.dumps({"Error": "Json Error"}).encode())
                except ConnectionResetError or ConnectionAbortedError:
                    return {"N": self.name, "Act": "Q"}
                continue

            if "N" not in mes or "Act" not in mes:
                try:
                    self._player_socket.send(json.dumps({"Error": "Incorrect dict format"}).encode())
                except ConnectionResetError or ConnectionAbortedError:
                    return {"N": self.name, "Act": "Q"}
                continue

            if mes["N"] != self.name:
                try:
                    self._player_socket.send(json.dumps({"Error": "Wrong Name"}).encode())
                except ConnectionResetError or ConnectionAbortedError:
                    return {"N": self.name, "Act": "Q"}
                continue

            if mes["Act"] == "B" and "Am" not in mes:
                try:
                    self._player_socket.send(json.dumps({"Error": "Incorrect dict format"}).encode())
                except ConnectionResetError or ConnectionAbortedError:
                    return {"N": self.name, "Act": "Q"}
                continue

            # If the player is betting, and they haven't bet a vaild amount of money (they haven't made a bet
            # between the min_bet and the players money, and they haven't gone all in.)
            if mes["Act"] == "B" and not (min_bet <= mes["Am"] <= self.money):
                if mes["Am"] != self.money:
                    try:
                        print("Am:", mes["Am"], "  self.money:", self.money, "  min_bet:", min_bet)
                        print(min_bet <= mes["Am"] <= self.money)
                        self._player_socket.send(json.dumps({"Error": "Wrong amount of money"}).encode())
                    except ConnectionResetError or ConnectionAbortedError:
                        return {"N": self.name, "Act": "Q"}
                    continue

            try:
                self._player_socket.send(json.dumps({"Accepted": True}).encode())
            except ConnectionResetError or ConnectionAbortedError:
                return {"N": self.name, "Act": "Q"}

            # End of test connections
            if mes["Act"] == "B":
                self.bet(mes["Am"])

            return mes


class AI(Player):
    """
    This will be the AI of the poker player.
    For each action the AI makes (e.g. bet, fold, check, raise) It will be based on the "hand_confidence".
    hand_confidence is based of a simulation of a sample of possible poker hands in the current game, and how likly the
    AI is to win
    The hand_confidence value is then used to decide how the AI should bet and what to bet
    """

    def __init__(self, starting_min_bet=10, current_names=None):
        """Creates an AI. current_names is a list of all the current names in the game"""
        if current_names is None:
            current_names = []
        name_list = ["Bob", "Michel", "John", "Alex", "Booth", "Vincent", "Angela", "Michaela", "Camille", "Tamara",
                     "Emily", "Meghan", "Barb", "Ava", "Ashley", "Morgan", "Mackenzie", "Madison", "Jordan", "Dylan",
                     "Alexis", "Addison", "Haley", "Isabella", "Grace"]  # List of names

        name_choice = ""
        while not name_choice or name_choice in current_names:
            name_choice = "AI " + choice(name_list)

        Player.__init__(self, name_choice, min_bet=starting_min_bet)
        self.cockyness = (random() - .3) * 0.2
        self.conf = 0  # The confidence of the current hand
        self.player_count = 0  # The number of players in the game, including self
        self.players_starting_money = {}
        self.players_bets = {}
        self.starting_min_bet = starting_min_bet
        self.starting_money = self.money
        self.is_bluffing = {}
        self.am_i_bluffing = False

    def update_player_count(self, new_player_count):
        """Updates the player count"""
        self.player_count = new_player_count

    def sim(self, playercount=1, min_sims=100, min_time=5):
        """Simulates many rounds of poker and returns a tuple of win probability and draw probability, and sim count"""

        if playercount < 1:
            return False

        sim_deck = Deck()
        sim_table = Table(create_socket=False)

        sim_count = 0
        for card in self.hand.in_play():
            sim_deck.remove_card(card)

        sim_players = [Player() for _ in range(playercount)]
        num_cards = 2 * playercount + 5 - len(self.hand.on_table)
        total_win = 0
        total_draw = 0
        for player in sim_players:
            player.hand.clear()
            player.add_flop(self.hand.on_table[:])

        starting_table_cards = self.hand.on_table[:]
        self_starting_hole_cards = self.hand.hole[:]

        start_time = time()
        while True:
            cards = sample(sim_deck.deck, num_cards)
            for player in sim_players:
                player.hand.clear()
                player.add_flop(starting_table_cards[:])
                player.give_hole(cards[:2])
                cards = cards[2:]

            self.hand.clear()
            self.add_flop(starting_table_cards[:])
            self.give_hole(self_starting_hole_cards)

            for player in sim_players + [self]:
                player.add_flop(cards)

            b = sim_table.best_player(sim_players + [self])
            sim_count += 1
            if b == self:
                total_win += 1

            elif type(b) is list and self in b:
                total_draw += 1

            if sim_count > min_sims and time() > start_time + min_time:
                self.hand.on_table = starting_table_cards[:]
                return total_win / sim_count, total_draw / sim_count, sim_count

    def update(self, res):
        """Updates the self.player_bets dictionary based other players choices"""
        if res["N"] != self.name:
            if res["N"] in self.players_bets:
                if res["Act"].upper() in "FQ":
                    for item in [self.players_bets, self.players_starting_money]:
                        item.pop(res["N"])
                elif res["Act"] == "B":
                    self.players_bets[res["N"]] += res["Am"]

            elif res["Act"].upper() in "FQ":
                pass

            else:
                print("res is for a player we don't know about. res", res)
                print(self.players_bets)
                # If this triggers, then the res will be for a player we don't know about

    def est_player_conf(self):
        """
        Works out how confidenct each other player as in there hands
        Returns a dict in form {name: conf} of all active players
        """
        conf_dict = {player: pow(self.players_bets[player] / self.players_starting_money[player], 0.7)
                     for player in self.players_bets if self.players_starting_money[player] != 0}

        # This deals with the edje case of players that have gone all in
        for player in [p for p in self.players_starting_money if self.players_starting_money[p] == 0]:
            conf_dict[player] = 1

        # Adjusting the dict for players with little money to have less confidence
        for player in [p for p in conf_dict if self.players_starting_money[p] < 20 * self.starting_min_bet]:
            conf_dict[player] *= 0.65

        # A player with a estimated conf between 0.7 to 1.0 has a chance of the AI disiding
        # if the player is bluffing.
        # The chance depending of the confidnece, with 0.05 chance for a 0.7, and 0.15 for a 1.0

        for player in [p for p in conf_dict if conf_dict[p] >= 0.7 and not self.is_bluffing[p]]:
            # for player that I don't think are bluffing, but could be...
            bluff_prob = 0.05 * (1 + ((conf_dict[player] - 0.7) / 0.3) * 2)
            print("there is a", round(bluff_prob, 4), "chance that", player, "is bluffing")
            if random() < bluff_prob or round(bluff_prob, 4) == 0.15:
                print(self.name, "thinks that", player, "is bluffing")
                self.is_bluffing[player] = True

        for player in conf_dict:
            if self.is_bluffing[player]:
                # Adjusting confidence of bluffing players
                conf_dict[player] *= 0.5

        # Return a dictanry of a player name: player cofidence
        return conf_dict

    def start_round(self, other_players, min_bet=None):
        """
        Initialise variables that will be used in calculation. Called before any bets have been made
        other_players: list of other players as Player objects
        """
        self.player_count = len(other_players) + 1
        self.conf = 1 / self.player_count
        self.players_starting_money = {p.name: p.money for p in other_players}
        # self.players_starting_money is a map of other players names to the amount of starting money
        self.players_bets = {p.name: 0 for p in other_players}
        self.starting_money = self.money
        if min_bet is None:
            min_bet = self.starting_min_bet

        self.starting_min_bet = min_bet

    def blinds(self, blind_list, min_bet):
        """
        blind_list is a list of player objects in the form [small_blind, big_blind]
        min_bet is an int which is the starting minimum bet
        """
        if blind_list[0] != self:
            self.players_bets[blind_list[0].name] = int(min_bet / 2)
        if blind_list[1] != self:
            self.players_bets[blind_list[1].name] = min_bet

    def hand_value(self):
        """Returns the float number of money that the AI 'thinks' that the hand is worth"""
        power = 0.6 + 0.2 * self.cockyness
        if self.starting_money < 20 * self.starting_min_bet:
            return self.money * pow(self.conf, power) * 0.2
        else:
            return 0.2 * (self.starting_min_bet * 20 + self.starting_money) / 2 * pow(self.conf, power)

    def begin_round(self, player_list):
        """To be called before any betting is done"""
        self.is_bluffing = {player.name: False for player in player_list if player != self}

    def ask_bet(self, min_bet):
        """
        Makes the AI make a choice on how much to bet, or if to fold
        THE NAME OF THIS FUNCTION MUST NOT CHANGE
        """

        if len(self.players_bets) == 0 or self.money == 0:
            sleep(0.2)
            print("Betting automaticly")
            return {"N": self.name, "Act": "B", "Am": 0}

        new = self.sim(self.player_count - 1, min_time=1)[0] + (random() - 0.5) * self.cockyness
        new = max(min(new, 1), 0)
        # new is a messure of hand confience

        if self.player_count == len(self.players_bets):
            self.conf = (self.conf + new) / 2
        else:
            self.conf = new

        if random() < 0.1 and not self.am_i_bluffing:
            print("I'm going to bluff")
            self.am_i_bluffing = True

        if self.am_i_bluffing and self.conf < 0.6:
            # adjusts the self.conf if I'm bluffing
            # Liner fuction y = (1/3)x + 0.6. x is current self.conf, y is new self.conf
            self.conf = (1 / 3) * self.conf + 0.6

        if self.conf < 0.8 / self.player_count:  # If the conf falls below a curten threshold, fold
            return self.fold("conf <" + str(round(0.8 / self.player_count, 3)))

        if self.conf < max(self.est_player_conf().values()) * 0.8:
            # If the conf is less then 80% of max estimated player confidences
            return self.fold("best player is too confident")

        # hand_value = self.hand_value()  # For debugging
        amount_to_bet = self.hand_value() - self.starting_money + self.money
        amount_to_bet *= (0.75 + random() / 4)
        amount_to_bet = round(amount_to_bet)

        if amount_to_bet and (self.starting_money - self.money) / abs(amount_to_bet) > 20 and self.money >= min_bet:
            # If the amount to bet is very small, then bet the min amount
            self.bet(min_bet)
            print(self.name, "bets", min_bet)
            return {"N": self.name, "Act": "B", "Am": min_bet}

        amount_to_bet = max(amount_to_bet, 0)

        if min_bet == 0 == amount_to_bet:
            print(self.name, "bets", min_bet)
            return {"N": self.name, "Act": "B", "Am": min_bet}

        if amount_to_bet == 0:
            return self.fold("amount to bet is 0")

        if min_bet and 0.8 < amount_to_bet / min_bet < 1.2:
            self.bet(min_bet)
            print(self.name, "bets", min_bet)
            return {"N": self.name, "Act": "B", "Am": min_bet}

        players_betting_max = [p for p in self.players_bets if self.players_bets[p] == max(self.players_bets.values())]
        if [True] * len(players_betting_max) == [self.is_bluffing[p] for p in
                                                 players_betting_max] and min_bet > amount_to_bet:
            # Are all the players that have bet the largest amount bluffing and the min_bet is greater then I value
            # my hand
            print("I'm calling this bluff")

            print("MinBet", min_bet, "Money", self.money)
            if min_bet < self.money:
                print(self.name, "bets", min_bet)
                self.bet(min_bet)
                return {"N": self.name, "Act": "B", "Am": min_bet}
            print(self.name, "bets", self.money)
            x = self.money
            self.bet(x)
            return {"N": self.name, "Act": "B", "Am": x}

        if min_bet and amount_to_bet / min_bet < 0.8:
            return self.fold("min_bet was too large")

        if amount_to_bet > self.money:
            self.bet(self.money)
            print(self.name, "bets", self.money)
            return {"N": self.name, "Act": "B", "Am": self.money}

        self.bet(amount_to_bet)  # Subtracks the amount to bet from AI's money
        print(self.name, "bets", amount_to_bet)
        return {"N": self.name, "Act": "B", "Am": amount_to_bet}

    def update_win_loss(self, winning_player):
        """Adjusts the AI cockyness based on if it wins. If a AI wins, it will become more cocky"""
        if self == winning_player or (type(winning_player) is list and self in winning_player):
            self.cockyness + 0.2 * random()
        else:
            self.cockyness - 0.2 * random()

        self.cockyness = max(min(self.cockyness, 0.9), 0.1)


class Table:
    """ Will contain all of the information in a table. No GUI"""

    def __init__(self, create_socket=True):
        """Creates a Table object. If create_socket is set to False, then the table will not create a socket"""
        if create_socket:
            ip = socket.gethostbyname(socket.gethostname())
            ip = [int(x) for x in ip.split(".")]
            ip = ip[::-1]
            ip = sum([value * 256 ** power for power, value in enumerate(ip)])
            # ip is now a integer
            ip = int_to_base(ip, 36)
            ip = ["0123456789abcdefghijklmnopqrstuvwxyz"[x] for x in ip]
            code = "".join(ip)

            print("Code:", code)

            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.bind((socket.gethostname(), 54321))
            self._socket.listen(10)
            self.code = code
        else:
            self.code = ""
            self._socket = False
        self.player_list = []
        self.players_to_add = []
        self.min_bet = 10

    def add_player(self, player):
        if isinstance(player, Player):
            self.players_to_add.append(player)

    def game_summary(self):
        """Sumarises the current state of play between poker rounds in a nested list
        eg. [2, [["David", "Human", 1200], ["AI Mike", "AI", 800]]]  (The 2 is because there are 2 players)"""

        return [len(self.player_list + self.players_to_add), [[p.name, type(p).__name__, p.money]
                                                              for p in self.player_list + self.players_to_add]]

    def make_human_player(self, player_socket):
        """Takes to a player though the player_socket to set up the name and add them to the players to add"""
        new_name = ""
        player_socket.send("Send Name".encode())
        while not new_name or new_name in [p.name for p in self.players_to_add + self.player_list]:
            try:
                mes = player_socket.recv(512)
                responce = json.loads(mes.decode())
            except json.decoder.JSONDecodeError:
                responce = ""
                player_socket.send(json.dumps({"Accepted": False, "Error": "Not valid dict"}).encode())
            except socket.timeout:
                print("Connection from new player timed out")
                player_socket.close()
                return False

            if type(responce) is dict and "MyName" in responce and len(responce) == 1:
                new_name = responce["MyName"]  # I don't think that pycharm should be yelling at me

            if new_name in [p.name for p in self.players_to_add + self.player_list]:
                player_socket.send(json.dumps({"Accepted": False, "Error": "Name Taken"}).encode())

            if "MyName" not in responce or type(responce) is not dict:
                player_socket.send(json.dumps({"Accepted": False, "Error": "Not valid dict"}).encode())

        player_socket.send(json.dumps({"Accepted": True}).encode())
        print("Player from", player_socket.getpeername(), "has the name", new_name)
        new_player = Human(new_name, player_socket, min_bet=self.min_bet)
        self.players_to_add.append(new_player)
        new_player.send_summary(self.game_summary())

    def listen_for_new_players(self):
        """Handles new connections from new players"""
        t = time()
        while self._socket:
            clientsocket, address = self._socket.accept()
            clientsocket.settimeout(120)
            print("Connection from", address)
            self.make_human_player(clientsocket)
            if t + 5 < time():
                t = time()
                print("listening...")

    @staticmethod
    def best_of_2(player1, player2):
        """Returns that player with the best hand, or both in a list if they draw"""
        # https://youtu.be/S2lMEkvnfno
        # Poker hand rankings. Can only use 5 cards
        handtypes = player1.hand.hand_types
        player1_best_hand = player1.hand.best()
        player2_best_hand = player2.hand.best()
        if handtypes.index(player1_best_hand[0]) > handtypes.index(player2_best_hand[0]):
            return player2

        elif handtypes.index(player1_best_hand[0]) < handtypes.index(player2_best_hand[0]):
            return player1

        # If it reaches this point, both players have the same type of hand

        t = player1_best_hand[0]

        if t == "High":
            player1_values = player1.hand.hand_values()[::-1]
            player2_values = player2.hand.hand_values()[::-1]

            i = 0
            while i < 5 and player1_values[i] == player2_values[i]:
                i += 1

            if i < 5:
                if "23456789TJQKA".index(player1_values[i]) > "23456789TJQKA".index(player2_values[i]):
                    return player1
                elif "23456789TJQKA".index(player1_values[i]) < "23456789TJQKA".index(player2_values[i]):
                    return player2

        if t == "Pair":
            player1_pair = player1_best_hand[1]
            player2_pair = player2_best_hand[1]

            if "23456789TJQKA".index(player1_pair) > "23456789TJQKA".index(player2_pair):
                return player1
            elif "23456789TJQKA".index(player1_pair) < "23456789TJQKA".index(player2_pair):
                return player2

            # Know kickers are used

            player1_values = player1.hand.hand_values()[::-1]
            player2_values = player2.hand.hand_values()[::-1]

            player1_values = list(player1_values)
            player1_values.remove(player1_pair)
            player1_values.remove(player1_pair)
            player1_values = "".join(player1_values)

            player2_values = list(player2_values)
            player2_values.remove(player2_pair)
            player2_values.remove(player2_pair)
            player2_values = "".join(player2_values)

            i = 0
            while i < 3 and player1_values[i] == player2_values[i]:
                i += 1

            if "23456789TJQKA".index(player1_values[i]) > "23456789TJQKA".index(player2_values[i]):
                return player1
            elif "23456789TJQKA".index(player1_values[i]) < "23456789TJQKA".index(player2_values[i]):
                return player2

        if t == "2Pair":
            player1_2pair = player1_best_hand[1]
            player2_2pair = player2_best_hand[1]

            if get_value(player1_2pair[0]) > get_value(player2_2pair[0]):
                return player1
            elif get_value(player1_2pair[0]) < get_value(player2_2pair[0]):
                return player2

            if get_value(player1_2pair[1]) > get_value(player2_2pair[1]):
                return player1
            elif get_value(player1_2pair[1]) < get_value(player2_2pair[1]):
                return player2

            player1_values = player1.hand.hand_values()[::-1]
            player2_values = player2.hand.hand_values()[::-1]

            player1_values = list(player1_values)
            player1_values.remove(player1_2pair[0])
            player1_values.remove(player1_2pair[0])
            player1_values.remove(player1_2pair[1])
            player1_values.remove(player1_2pair[1])
            player1_values = "".join(player1_values)

            player2_values = list(player2_values)
            player2_values.remove(player2_2pair[0])
            player2_values.remove(player2_2pair[0])
            player2_values.remove(player2_2pair[1])
            player2_values.remove(player2_2pair[1])
            player2_values = "".join(player2_values)

            if get_value(player1_values[0]) > get_value(player2_values[0]):
                return player1
            elif get_value(player1_values[0]) < get_value(player2_values[0]):
                return player2

        if t == "3OAK":
            if get_value(player1_best_hand[1]) > get_value(player2_best_hand[1]):
                return player1
            if get_value(player1_best_hand[1]) < get_value(player2_best_hand[1]):
                return player2

            player1_values = player1.hand.hand_values()[::-1]
            player2_values = player2.hand.hand_values()[::-1]

            player1_values = list(player1_values)
            player1_values.remove(player1_best_hand[1])
            player1_values.remove(player1_best_hand[1])
            player1_values.remove(player1_best_hand[1])
            player1_values = "".join(player1_values)

            player2_values = list(player2_values)
            player2_values.remove(player2_best_hand[1])
            player2_values.remove(player2_best_hand[1])
            player2_values.remove(player2_best_hand[1])
            player2_values = "".join(player2_values)

            i = 0
            while i < len(player1_values) - 1 and player1_values[i] == player2_values[i]:
                i += 1

            if get_value(player1_values[i]) > get_value(player2_values[i]):
                return player1
            elif get_value(player1_values[i]) < get_value(player2_values[i]):
                return player2

        if t == "Straight":
            ranking = ["2345A", "23456", "34567", "45678", "56789", "6789T", "789TJ", "89TJQ", "9TJQK", "234KA",
                       "23QKA", "2JQKA", "TJQKA"]

            if ranking.index(player1_best_hand[1]) > ranking.index(player2_best_hand[1]):
                return player1
            if ranking.index(player1_best_hand[1]) < ranking.index(player2_best_hand[1]):
                return player2

            player1_values = list(player1.hand.hand_values()[::-1])
            player2_values = list(player2.hand.hand_values()[::-1])

        if t == "Flush":
            player1_flush = player1_best_hand[1]
            player2_flush = player2_best_hand[1]

            i = 0
            while i < 5 and player1_flush[i] == player2_flush[i]:
                i += 1

            if i < 5:
                if get_value(player1_flush[i]) > get_value(player2_flush[i]):
                    return player1
                if get_value(player1_flush[i]) < get_value(player2_flush[i]):
                    return player2

            """
            # This code make it so that flushes have much stricter bar for drawing
            
            # Eg.  say you have a flush on the table of AH, 6H, 5H, 9H, JH  with no other players having any other
            # Hearts. If this code isn't used, then you don't split the pot, UNLESS all players have idetical 
            # values of cards.
            # I think that this is wrong, which is why it's commented
            
            
            
            player1_values = list(player1.hand.hand_values()[::-1])
            player2_values = list(player2.hand.hand_values()[::-1])

            for item in player1_best_hand[1]:
                player1_values.remove(item)
                player2_values.remove(item)

            i = 0
            while i < len(player1_values) - 1 and player1_values[i] == player2_values[i]:
                i += 1

            if get_value(player1_values[i]) > get_value(player2_values[i]):
                return player1
            elif get_value(player1_values[i]) < get_value(player2_values[i]):
                return player2
            """

        if t == "FullH":
            if get_value(player1_best_hand[1][0]) > get_value(player2_best_hand[1][0]):
                return player1
            if get_value(player1_best_hand[1][0]) < get_value(player2_best_hand[1][0]):
                return player2

            if get_value(player1_best_hand[1][1]) > get_value(player2_best_hand[1][1]):
                return player1
            if get_value(player1_best_hand[1][1]) < get_value(player2_best_hand[1][1]):
                return player2

        if t == "4OAK":
            if get_value(player1_best_hand[1]) > get_value(player2_best_hand[1]):
                return player1
            if get_value(player1_best_hand[1]) < get_value(player2_best_hand[1]):
                return player2

            player1_values = list(player1.hand.hand_values())
            player2_values = list(player2.hand.hand_values())

            for i in range(4):
                player1_values.remove(player1_best_hand[1])
                player2_values.remove(player2_best_hand[1])

            if get_value(player1_values[0]) > get_value(player2_values[0]):
                return player1
            if get_value(player1_values[0]) < get_value(player2_values[0]):
                return player2

        if t == "StraightF":
            s_ranking = ["2345A", "23456", "34567", "45678", "56789", "6789T", "789TJ", "89TJQ", "9TJQK"]

            if player1_best_hand[1] in s_ranking:
                player1_ranking = s_ranking.index(player1_best_hand[1])
            else:
                player1_ranking = 20

            if player2_best_hand[1] in s_ranking:
                player2_ranking = s_ranking.index(player2_best_hand[1])
            else:
                player2_ranking = 20

            if player1_ranking > player2_ranking:
                return player1

            if player1_ranking < player2_ranking:
                return player2

        return [player1, player2]

    def best_player(self, player_list):
        """Returns the player with the best hand from the player_list or a list of player if they have drawn"""
        if len(player_list) == 0:
            return False
        if len(player_list) == 1:
            return player_list[0]

        winners = [player_list[0]]
        for player in player_list[1:]:
            b = self.best_of_2(player, winners[0])
            if type(b) is list:
                winners.append(player)
            elif b != winners[0]:
                winners = [b]

        if len(winners) == 1:
            return winners[0]

        return winners

    def send_cards(self, players):
        """Sends the card information to the human players"""
        if not players:
            print("The players list doesn't seem to exist. Check input")
            raise Exception("Error in Table.send_cards")

        cards = [[card.face for card in p.hand.on_table] for p in players]
        # cards should look something like [["JC", "KD", "3C"], ["JC", "KD", "3C"], ["JC", "KD, "3C"]]
        # All items in cards should be idenitcal, this section checks it
        if min(cards) != max(cards):
            print("The cards don't seem to match")
            print("Cards:", cards)
            raise Exception("Cards don't seem to match, check before error")

        cards_to_send = cards[0]
        cards_str = "".join(cards_to_send)
        bytes_to_send = {"cards": cards_str}
        # bytes_to_send is a bytes object to send to all the human players

        players_left = []
        for player in [p for p in players if isinstance(p, Human)]:
            # Send bytes to players
            try:
                player.send_summary(bytes_to_send)
            except ConnectionResetError:
                players_left.append(player)

        return players_left

    def create_ai(self):
        a = AI(self.min_bet, [p.name for p in self.player_list + self.players_to_add])
        print(f"{a.name} joined")
        self.add_player(a)

    @staticmethod
    def non_round(active_players):
        """Returns True if the next round will finish instantly"""
        if len(active_players) <= 1:
            return True

        return [0] * (len(active_players) - 1) == sorted([p.money for p in active_players])[:-1]
        # Translates to: If all but one player has any money?

    def betting_round(self, active=None, min_bet=10, start=False):
        """
        Completes a betting round
        returns tuple: (players still in the game, total of bets in the game)
        """
        if active is None:
            active = self.player_list[:]

        if len(active) == 1:
            return active, 0, False

        players_money_set = set([p.money for p in active])
        if len(players_money_set) == 2 and 0 in players_money_set:
            return active, 0, False

        if [0] * len(active) == [p.money for p in active]:
            return active, 0, False

        for ai in [player for player in active if isinstance(player, AI)]:
            active_copy = active[:]
            active_copy.remove(ai)
            if start:
                ai.start_round(active_copy, min_bet=min_bet)
            else:
                ai.start_round(active_copy)

        starting_players = set(active)
        player_bets = {player: 0 for player in active}

        asked_players = set([])  # Thi is a set of all players that have been asked for a bet

        if start:  # Is this the first betting round i.e do we need to distribute the blinds
            blinds = [int(min_bet / 2), min_bet]
            for hum_player in [h for h in self.player_list if isinstance(h, Human)]:
                cards = hum_player.hand.in_play()
                cards = [c.face for c in cards]
                cards = cards[0] + cards[1]  # Four digit string of a players cards eg. 3DJS, which, in this case, is
                # the three of diamonds and the jack of spades

                try:
                    hum_player.send_summary([cards, [a.name for a in active[:2]], min_bet])
                except ConnectionResetError:
                    starting_players.remove(hum_player)
                    del player_bets[hum_player]
            sleep(1)

            for player, blind_amount in zip(active[:2], blinds):
                if player.money < blind_amount:
                    player_bets[player] += player.money
                    player.bet(player.money)
                else:
                    player_bets[player] += blind_amount
                    player.bet(blind_amount)

            print("Blinds: ", [p.name for p in active[:2]])

            for ai in [player for player in active if isinstance(player, AI)]:
                ai.blinds(active[:2], min_bet)
                ai.update_player_count(len(active))

            active = active[2:] + active[:2]

        count = 0
        while True:
            count += 1
            print("Round:", count, "Order", [p.name for p in active])
            if count > 20:
                # debug = True  # This is for testing reasons
                pass
            if active[0].money > 0:
                print("Asking", active[0].name)
                res = active[0].ask_bet(max(player_bets.values()) - player_bets[active[0]])

                for player in active:
                    if isinstance(player, Human):
                        did_send = player.update(res)
                        if not did_send:
                            res = {"N": res["N"], "Act": "Q"}
                    else:
                        player.update(res)

                sleep(1)

                if active[0] not in asked_players:
                    asked_players.add(active[0])

                if res["Act"] == "B":
                    player_bets[active[0]] += res["Am"]

                if res["Act"] in "FQ":  # Need to change this sometime, to add the quit feature.
                    active = active[1:]
                    if res["Act"] == "Q":
                        quitting_player = [p for p in self.player_list if res["N"] == p.name][0]
                        self.player_list.remove(quitting_player)
                else:
                    active = active[1:] + [active[0]]

            else:
                if active[0] not in asked_players:
                    asked_players.add(active[0])
                active = active[1:] + [active[0]]

            # Cheaking if it's time to stop this round of betting

            # Have all players bet?
            # Have all active players, i.e not folded, bet the same amount of money, or run out of money

            if len(active) == 1:
                return active, sum(player_bets.values()), True

            if asked_players != starting_players:
                continue

            players_with_money = [player_bets[player] for player in active
                                  if player.money > 0 or max(player_bets.values()) == player_bets[player]]
            # This is a list of players bets that players with money have made this round
            if min(players_with_money) != max(players_with_money):
                continue

            return active, sum(player_bets.values()), True

    def round(self, count):
        """ Plays a round of poker """
        print("\nCode:", self.code)
        sleep(3)  # Stops message overlap on slow connections.
        pot = 0
        d = Deck(True)

        for ai in [a for a in self.player_list if isinstance(a, AI)]:
            ai.begin_round(self.player_list)

        for hum in [h for h in self.player_list if isinstance(h, Human)]:
            hum.send_summary({"Start Round": self.game_summary()})

        sleep(1)  # This is so that there is a delay in sending the "Start Round" and the next round at the same time

        for player in self.player_list:
            player.hand.give_hole(d.take_n(2))

        table_cards = d.take_n(5)

        # input("First Betting round...")
        print("First Betting round...")

        results = self.betting_round(start=True, min_bet=self.min_bet)
        active_players = results[0]
        pot += results[1]
        for player in self.player_list:
            player.add_flop(table_cards[:3])

        if not self.non_round(active_players):
            left = self.send_cards(active_players)
            for p in left:
                self.player_list.remove(p)
                active_players.remove(p)

        # input("Second Betting round...")
        print("Second Betting round...")
        results = self.betting_round(active=active_players, min_bet=0)
        active_players = results[0]
        pot += results[1]
        for player in self.player_list:
            player.add_turn(table_cards[3])

        if not self.non_round(active_players):
            left = self.send_cards(active_players)
            for p in left:
                self.player_list.remove(p)
                active_players.remove(p)

        # input("Third Betting round...")
        print("Third Betting round...")
        results = self.betting_round(active=active_players, min_bet=0)
        active_players = results[0]
        pot += results[1]
        for player in self.player_list:
            player.add_river(table_cards[4])

        if not self.non_round(active_players):
            left = self.send_cards(active_players)
            for p in left:
                self.player_list.remove(p)
                active_players.remove(p)

        # input("Final Round...")
        print("Final Round...")
        results = self.betting_round(active=active_players, min_bet=0)
        active_players = results[0]
        pot += results[1]

        b = self.best_player(active_players)
        if isinstance(b, Player):
            best_hand_type = b.hand.best()[0]
        else:
            best_hand_type = b[0].hand.best()[0]

        for ai in [a for a in self.player_list if isinstance(a, AI)]:
            ai.update_win_loss(b)

        print("\n\n\n")
        if type(b) is not list:
            print("Table: " + self.player_list[0].hand.str_hand(table_cards))
            for player in active_players:
                print(player.name + ": " + player.hand.str_hand(player.hand.hole))
            print("Best:", b.name, "with a", best_hand_type)
            pass

        if type(b) is list:
            print("Table: " + self.player_list[0].hand.str_hand(table_cards))
            for player in self.player_list:
                print(player.name + ": " + player.hand.str_hand(player.hand.hole))

            string = ""
            for item in b:
                string += item.name + ", "
            string = string.strip(", ")

            print("Draw between", string)
            pass

        active_players_cards = {p.name: "".join([c.face for c in p.hand.hole]) for p in active_players}
        table_cards = "".join([card.face for card in active_players[0].hand.on_table])

        for player in self.player_list:
            player.hand.clear()

        self.player_list = self.player_list[1:] + [self.player_list[0]]

        # Divid up the pot

        if isinstance(b, Player):
            b.money += pot

        elif type(b) is list:
            remander = pot % len(b)  # Adjusts the players in b so that they have the correct amounts of money
            for i in range(len(b)):
                if i < remander:
                    b[i].money += int(pot / len(b)) + 1
                else:
                    b[i].money += int(pot / len(b))

        if isinstance(b, Player):
            b = [b]

        # Sends infomation to the human players about the state of the game
        for player in [p for p in self.player_list if isinstance(p, Human)]:
            ending_info = (  # Info about the end of a round of poker.
                active_players_cards,
                # Names of active players in the end and cards they have

                pot,
                # The size of the pot

                [winner.name for winner in b],
                # Names of the winner(s) of the round

                best_hand_type,
                # The type of hand that is the best

                table_cards
                # Final cards for the end of the game
            )

            did_send = player.send_summary({"EndRound": ending_info})
            if not did_send:
                self.player_list.remove(player)

        sleep(1)

        if count % 5 == 0:
            print("Updating min_bet to", self.min_bet * 2)
            self.min_bet *= 2
            self.min_bet = round_sig_figs(self.min_bet, 2)

        for player in self.player_list:
            if player.money < self.min_bet:
                if isinstance(player, Human):
                    try:
                        player.send_summary({"NoMoney": ""})
                    except ConnectionResetError:
                        pass
                self.player_list.remove(player)
        sleep(1)

        print("")
        print("-" * 40)
        print("Players remaining")
        for item in self.player_list:
            print("{}: ${}".format(item.name, item.money))

        sleep(1)  # Allows players to look at the result of the game

        print("Starting next round")

    def play(self):
        """Main fuction that plays poker on a table"""

        threading.Thread(target=self.listen_for_new_players).start()

        count = 1
        while True:
            while len([p for p in self.player_list + self.players_to_add if isinstance(p, AI)]) < 3:
                self.create_ai()

            if self.players_to_add:
                self.player_list.extend(self.players_to_add)
                self.players_to_add = []

            if True in [isinstance(player, Human) for player in self.player_list]:
                self.round(count)
                count += 1


def stringToCards(string):
    output = []
    while string:
        output.append(Card(string[:2]))
        string = string[2:]

    return output


class Cheater:
    def __init__(self):
        self.ai = AI()
        self.other_player_num = 0

    def add_input(self):
        self.other_player_num = int(input("Other Player Num: "))
        self.ai.give_hole(stringToCards(input("Hole: ")))
        self.ai.add_flop(stringToCards(input("Table: ")))

    def cheat(self):
        self.add_input()
        print(self.ai.sim(self.other_player_num, min_sims=1, min_time=2))
        self.ai.hand.clear()
        print()


if __name__ == "__main__":
    c = Cheater()
    while True:
        c.cheat()