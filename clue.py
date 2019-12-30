import random
from functools import reduce

class Card:
	SUSPECT = 0
	WEAPON = 1
	ROOM = 2

	def __init__(self, name, type_):
		assert type_ == Card.SUSPECT or type_ == Card.WEAPON or type_ == Card.ROOM
		self.name = name
		self.type_ = type_

		if type_ == Card.SUSPECT:
			self.typeName = "Suspect"
		elif type_ == Card.WEAPON:
			self.typeName = "Weapon"
		elif type_ == Card.ROOM:
			self.typeName = "Room"

cards_list = [
	Card("Col. Mustard", Card.SUSPECT), 
	Card("Prof. Plum", Card.SUSPECT), 
	Card("Mr. Green", Card.SUSPECT), 
	Card("Mrs. Peacock", Card.SUSPECT), 
	Card("Miss Scarlett", Card.SUSPECT), 
	Card("Mrs. White", Card.SUSPECT), 
	Card("Knife", Card.WEAPON), 
	Card("Candlestick", Card.WEAPON), 
	Card("Revolver", Card.WEAPON), 
	Card("Rope", Card.WEAPON), 
	Card("Lead Pipe", Card.WEAPON), 
	Card("Wrench", Card.WEAPON), 
	Card("Hall", Card.ROOM), 
	Card("Lounge", Card.ROOM), 
	Card("Dining Room", Card.ROOM), 
	Card("Kitchen", Card.ROOM), 
	Card("Ball Room", Card.ROOM), 
	Card("Conservatory", Card.ROOM), 
	Card("Billiard Room", Card.ROOM), 
	Card("Library", Card.ROOM), 
	Card("Study", Card.ROOM),
]

names_list = ["Liam", "Emma", "Noah", "Olivia", "William", "Ava", "James", "Isabella", "Oliver", "Sophia", "Benjamin", "Charlotte", "Elijah", "Mia", "Lucas", "Amelia", "Mason", "Harper", "Logan", "Evely"]

class AIPlayer:
	UNKNOWN = -1
	NOT_OWNED = 1

	def __init__(self, name, hand, uid, uids, cards):
		self.name = name
		self.hand = hand
		self.uid = uid
		self.cards = cards

		i = uids.index(uid)
		self.looped_uids = uids[i+1:] + uids[:i]
		self.uids = uids.copy() # uids of other players
		self.uids.remove(uid)

		self.known = {} # key is card, value is UNKNOWN or UID of player who owns it
		self.possibly_owned = {} # key is UID of player, value is {key is card, value is [UNKNOWN], or list of turn_index #s when denied}
		self.not_owned = {} # key is UID of player, value is {key is card, value is UNKNOWN or NOT_OWNED}

		self.won = False
		self.winning_cards = []

		for uid in self.uids:
			self.possibly_owned[uid] = {}
			self.not_owned[uid] = {}
			for card in self.cards:
				self.possibly_owned[uid][card] = [AIPlayer.UNKNOWN]
				self.not_owned[uid][card] = AIPlayer.UNKNOWN

		for card in self.cards:
			self.known[card] = AIPlayer.UNKNOWN

		for card in self.hand:
			self.known[card] = self.uid

	def check_possibilites(self, uid, turn_index): # returns a card if it's owned by `uid`, None otherwise
		if turn_index <= -1:
			return None # if this turn isn't even REAL return None

		of_round = list(filter(lambda e: turn_index in e[1], self.possibly_owned[uid].items())) # get the other cards `uid` could have owned during `turn_index`
		if len(of_round) == 1: # if only one card remains as possible it must be the owned one
			return of_round[0][0] # return the card
		else:
			return None # return None if no deduction is possible

	def handle_card_not_owned(self, uid, card_not_owned):
		turn_indecies = self.possibly_owned[uid][card_not_owned] # get the rounds that `uid` possibly had this card (could get an ENUM instead of round)
		self.possibly_owned[uid][card_not_owned] = [AIPlayer.UNKNOWN] # `uid` does not own this card
		if turn_indecies[0] != AIPlayer.UNKNOWN: # if `uid` might own a card from `turn_indecies`
			for turn_index in turn_indecies:
				card = self.check_possibilites(uid, turn_index)
				if not(card is None): # `uid` owns `card`
					self.handle_card_owned(uid, card, turn_index)

	def handle_card_owned(self, owner_uid, owned_card, turn_index=-1, smart=True):
		if self.known[owned_card] == owner_uid: # if we already know that `owner_uid` owns this
			return # just exit
		elif self.known[owned_card] != AIPlayer.UNKNOWN: # if someone owns `owned_card`, but not `owner_uid`, it's a mistake!
			print("Major logical error occured: Both", owner_uid, "and", self.known[owned_card], "own", owned_card.name)
			assert self.uid != 0
			return
		
		for card, indecies in filter(lambda e: turn_index in e[1], self.possibly_owned[owner_uid].items()):
			if len(indecies) <= 1:
				self.possibly_owned[owner_uid][card] = [AIPlayer.UNKNOWN]
			else:
				indecies.remove(turn_index)
		
		self.known[owned_card] = owner_uid

		for uid in self.uids:
			turn_indecies = self.possibly_owned[uid][owned_card]
			if uid == owner_uid or turn_indecies[0] == AIPlayer.UNKNOWN:
				continue # skip `owner_uid` or if no turn_indecies for `uid` and `owned_card`

			self.possibly_owned[uid][owned_card] = [AIPlayer.UNKNOWN]
			for turn_index_ in turn_indecies:
				card = self.check_possibilites(uid, turn_index_)
				if not(card is None):
					self.handle_card_owned(uid, card, turn_index_)

		if smart:
			print("~~~~", self.uid, "determined that", owner_uid, "owns", owned_card.name)
			assert owned_card in game.players[owner_uid].hand
		else:
			print("----", self.uid, "determined that", owner_uid, "owns", owned_card.name)

	def check_won(self):
		unowned_suspects = reduce(lambda count, e: count + 1 if (e[0].type_ == Card.SUSPECT and e[1] == AIPlayer.UNKNOWN) else count, self.known.items(), 0) # count unknown suspects
		unowned_weapons = reduce(lambda count, e: count + 1 if (e[0].type_ == Card.WEAPON and e[1] == AIPlayer.UNKNOWN) else count, self.known.items(), 0) # count unknown weapons
		unowned_rooms = reduce(lambda count, e: count + 1 if (e[0].type_ == Card.ROOM and e[1] == AIPlayer.UNKNOWN) else count, self.known.items(), 0) # count unknown rooms

		if (unowned_suspects == 0 or unowned_weapons == 0 or unowned_rooms == 0): # if any of these are zero, something has gone seriously wrong
			print("Major logical error occured:", unowned_suspects, unowned_weapons, unowned_rooms)
			assert self.uid != 0
		elif (unowned_suspects == 1 and unowned_weapons == 1 and unowned_rooms == 1): # if all of these are one, then we know what the crime was
			self.winning_cards = list(map(lambda e: e[0], filter(lambda e: e[1] == AIPlayer.UNKNOWN, self.known.items())))
			self.won = True
			print("\t", self.name, "will win! The cards are: ", list(map(lambda card: card.name, self.winning_cards)))

	def deny_card(self, uid, card, turn_index):
		if self.not_owned[uid][card] == AIPlayer.UNKNOWN and self.known[card] == AIPlayer.UNKNOWN: # if this card could be owned by `uid`
			options = self.possibly_owned[uid][card]
			if options[0] == AIPlayer.UNKNOWN: # if the list has no turn_indecies yet
				options[0] = turn_index # replace it with the round index
			else:
				options.append(turn_index) # otherwise just add it to the list
			return True
		else:
			return False

	def crime_proposed(self, uid, suspect, weapon, room, turn_index):
		# print(uid, "proposed:", suspect.name, "with the", weapon.name, "in the", room.name)
		pass

	def crime_undenied(self, uid, suspect, weapon, room, turn_index): # `uid` of player who could not deny crime
		if uid == self.uid:
				return
		# print(uid, "could not deny:", suspect.name, "with the", weapon.name, "in the", room.name)

		self.not_owned[uid][suspect] = AIPlayer.NOT_OWNED
		self.not_owned[uid][weapon] = AIPlayer.NOT_OWNED
		self.not_owned[uid][room] = AIPlayer.NOT_OWNED

		self.handle_card_not_owned(uid, suspect)
		self.handle_card_not_owned(uid, weapon)
		self.handle_card_not_owned(uid, room)

		self.check_won()

	def crime_denied(self, uid, suspect, weapon, room, turn_index): # `uid` of player who could deny crime
		if uid == self.uid:
			return
		# print(uid, "denied:", suspect.name, "with the", weapon.name, "in the", room.name)
		possiblities = []

		if self.known[suspect] == uid or self.known[weapon] == uid or self.known[room] == uid:
			return # if one of the cards is known to be owned by uid, we can't gather any info

		if self.deny_card(uid, suspect, turn_index):
			possiblities.append(suspect)

		if self.deny_card(uid, weapon, turn_index):
			possiblities.append(weapon)

		if self.deny_card(uid, room, turn_index):
			possiblities.append(room)

		if len(possiblities) == 0:
			print("Major logical error occured: crime [", suspect.name, weapon.name, room.name, "] cannot be denied by", uid)
			assert self.uid != 0
		elif len(possiblities) == 1:
			self.handle_card_owned(uid, possiblities[0], turn_index)
			self.check_won()


	def card_shown(self, uid, card, turn_index):
		# print("You,", self.uid, ", were shown", card.name)
		if uid == self.uid:
			return
		self.handle_card_owned(uid, card, turn_index, smart=False)

	def print_info(self):
		print("\n----------------Info of " + str(self.uid) + "----------------")
		print("Known\t\tPossible" + "\t"*len(self.uids) + "Not Owned")

		ln = "\t\t"
		for uid in self.uids:
			ln += str(uid) + "\t"
		ln += "\t"
		for uid in self.uids:
			ln += str(uid) + "\t"
		print(ln)

		for card in self.cards:
			ln = "  " + str(self.known[card]) + "\t\t"
			for uid in self.uids:
				ln += str(self.possibly_owned[uid][card]) + "\t"
			ln += "\t"
			for uid in self.uids:
				ln += str(self.not_owned[uid][card]) + "\t"
			ln += "\t" + card.name
			
			print(ln)

rooms_list = list(filter(lambda card: card.type_ == Card.ROOM, cards_list))
suspects_list = list(filter(lambda card: card.type_ == Card.SUSPECT, cards_list))
weapons_list = list(filter(lambda card: card.type_ == Card.WEAPON, cards_list))

n_players = int(input("Enter number of players: "))
player_names = {0: "Me"}
for i in range(1, n_players):
	player_names[i] = input("Player " + str(i + 1) + " name: ")

print("\nChoose card indecies:")
for i, card in enumerate(cards_list):
	print("\t", (i+1), card.name)

hand = []
while True:
	index = input("\tIndex: ")
	if index == "":
		break
	else:
		hand.append(cards_list[int(index) - 1])

print("Hand:", list(map(lambda card: card.name, hand)))

player = AIPlayer(player_names[0], hand, 0, list(range(n_players)), cards_list)
turn_index = 0
need_crime = True
suspect = None
weapon = None
room = None
proposer_uid = -1
while True:
	turn_index += 1
	print("Ids:\n\t", player_names.items())

	if need_crime:
		print("Suspects:")
		for i, card in enumerate(suspects_list):
			print("\t", (i+1), card.name)
		print("Weapons:")
		for i, card in enumerate(weapons_list):
			print("\t", (i+1), card.name)
		print("Rooms:")
		for i, card in enumerate(rooms_list):
			print("\t", (i+1), card.name)

		print("Crime proposal:")
		proposer_uid = int(input("\tPlayer id: "))
		suspect = suspects_list[int(input("\tSuspect id: ")) - 1]
		weapon = weapons_list[int(input("\tWeapon id: ")) - 1]
		room = rooms_list[int(input("\tRoom id: ")) - 1]

		print("Crime proposed by", player_names[proposer_uid], "=", suspect.name, "with the", weapon.name, "in the", room.name)
		if proposer_uid != 0:
			player.crime_proposed(proposer_uid, suspect, weapon, room, turn_index)
		need_crime = False
	else:
		print("Crime response:")
		uid = int(input("\tPlayer id: "))
		response_type = int(input("\tDo not deny = 0, Deny = 1: "))
		if response_type == 1:
			need_crime = True
			if proposer_uid == 0:
				print("Cards:")
				for i, card in enumerate(cards_list):
					print("\t", (i+1), card.name)
				card = cards_list[int(input("\tShown card id: ")) - 1]
				print("Showed", player_names[proposer_uid], card.name)
				player.card_shown(uid, card, turn_index)
			else:
				player.crime_denied(uid, suspect, weapon, room, turn_index)
		else:
			player.crime_undenied(uid, suspect, weapon, room, turn_index)

	player.print_info()