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

class Game:
	def __init__(self, num_players, cards, names):
		self.num_players = num_players
		self.turn_index = 0
		self.round_index = 0
		self.player_index = 0
		self.cards = cards

		self.suspect = random.choice(list(filter(lambda card: card.type_ == Card.SUSPECT, self.cards)))
		self.weapon = random.choice(list(filter(lambda card: card.type_ == Card.WEAPON, self.cards)))
		self.room = random.choice(list(filter(lambda card: card.type_ == Card.ROOM, self.cards)))

		self.cards_subset = cards.copy()
		self.cards_subset.remove(self.suspect)
		self.cards_subset.remove(self.weapon)
		self.cards_subset.remove(self.room)

		self.player_hands = []
		for i in range(num_players):
			self.player_hands.append([])

		count = len(self.cards_subset)
		for i in range(count):
			j = random.randint(0, count - i - 1) # cards_subset: card index
			k = i % num_players # player_hands: player index
			self.player_hands[k].append(self.cards_subset.pop(j))

		self.players = []
		uids = list(range(num_players))
		for i, hand in enumerate(self.player_hands):
			self.players.append(AIPlayer(random.choice(names), hand, i, uids, cards))

		for i, hand in enumerate(self.player_hands):
			print(i, list(map(lambda card: card.name, hand)))

	def play(self):
		while True:
			if not(self.turn()):
				return

			print("Round index =", self.round_index)
			self.round_index += 1

			# cont = input("Type y to continue playing: ").lower()
			# if cont != "y":
			# 	return

	def turn(self):
		current_player = self.players[self.player_index]

		roll = random.randint(1, 6)
		# print("Rolled a", roll)

		room = current_player.move(roll)

		if type(room) is list:
			if self.suspect in room and self.weapon in room and self.room in room:
				print("You're right!")
				for player in self.players:
					player.print_info()
			else:
				assert False, "Wrong answer!"
			return False

		suspect, weapon = current_player.propose_crime(room)
		for player in self.players:
			if player != current_player:
				player.crime_proposed(current_player.uid, suspect, weapon, room, self.turn_index)

		for i in range(1, self.num_players):
			self.turn_index += 1
			respond_player = self.players[(self.player_index + i) % self.num_players]

			choices = list(filter(lambda card: card == room or card == suspect or card == weapon, respond_player.hand))
			if len(choices) == 0:
				for player in self.players:
					if player != respond_player:
						player.crime_undenied(respond_player.uid, suspect, weapon, room, self.turn_index)
			else:
				show_card = choices[0]
				if len(choices) > 1:
					show_card = respond_player.expose_card(choices)
				current_player.card_shown(respond_player.uid, show_card, self.turn_index)
				for player in self.players:
					if player != respond_player and player != current_player:
						player.crime_denied(respond_player.uid, suspect, weapon, room, self.turn_index)
				break

		self.turn_index += 1
		self.player_index = (self.player_index + 1) % self.num_players
		return True

class Player:
	def __init__(self, name, hand, uid, uids, cards):
		self.name = name
		self.hand = hand
		self.uid = uid
		self.uids = uids.copy() # uids of other players
		self.uids.remove(uid)
		self.cards = cards

	def expose_card(self, choices):
		print("\nChoose card index:")
		for i, choice in enumerate(choices):
			print("\t", (i+1), choice.name)
		index = int(input("Index: "))
		print("Will reveal", choices[index-1].name)

		return choices[index-1]

	def crime_proposed(self, uid, suspect, weapon, room, turn_index):
		print(uid, "proposed:", suspect.name, "with the", weapon.name, "in the", room.name)

	def crime_undenied(self, uid, suspect, weapon, room, turn_index): # `uid` of player who could not deny crime
		print(uid, "could not deny:", suspect.name, "with the", weapon.name, "in the", room.name)

	def crime_denied(self, uid, suspect, weapon, room, turn_index): # `uid` of player who could deny crime
		print(uid, "denied:", suspect.name, "with the", weapon.name, "in the", room.name)

	def card_shown(self, uid, card, turn_index):
		print("You,", self.uid, ", were shown", card.name)

	def move(self, steps):
		rooms = list(filter(lambda card: card.type_ == Card.ROOM, self.cards))

		print("\nChoose room index:")
		for i, room in enumerate(rooms):
			print("\t", (i+1), room.name)
		index = int(input("Index: "))
		print("Going to", rooms[index-1].name)

		return rooms[index-1]

	def propose_crime(self, room):
		suspects = list(filter(lambda card: card.type_ == Card.SUSPECT, self.cards))
		weapons = list(filter(lambda card: card.type_ == Card.WEAPON, self.cards))

		print("\nChoose suspect index:")
		for i, sus in enumerate(suspects):
			print("\t", (i+1), sus.name)
		index = int(input("Index: "))
		suspect = suspects[index-1]

		print("\nChoose weapon index:")
		for i, wep in enumerate(weapons):
			print("\t", (i+1), wep.name)
		index = int(input("Index: "))
		weapon = weapons[index-1]

		print(suspect.name, "with the", weapon.name, "in the", room.name)
		return (suspect, weapon)

class AIPlayer(Player):
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
		# print(uid, "could not deny:", suspect.name, "with the", weapon.name, "in the", room.name)

		self.not_owned[uid][suspect] = AIPlayer.NOT_OWNED
		self.not_owned[uid][weapon] = AIPlayer.NOT_OWNED
		self.not_owned[uid][room] = AIPlayer.NOT_OWNED

		self.handle_card_not_owned(uid, suspect)
		self.handle_card_not_owned(uid, weapon)
		self.handle_card_not_owned(uid, room)

		self.check_won()

	def crime_denied(self, uid, suspect, weapon, room, turn_index): # `uid` of player who could deny crime
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
		self.handle_card_owned(uid, card, turn_index, smart=False)

	def expose_card(self, choices):
		return random.choice(choices)

	def move(self, steps):
		if self.won:
			print(self.uid, self.name, "won! Winning cards:", list(map(lambda card: card.name, self.winning_cards)))
			return self.winning_cards

		rooms = list(filter(lambda card: card.type_ == Card.ROOM, self.cards))
		return random.choice(rooms)

	def propose_crime(self, room):
		suspects = list(filter(lambda card: card.type_ == Card.SUSPECT, self.cards))
		weapons = list(filter(lambda card: card.type_ == Card.WEAPON, self.cards))
		return (random.choice(suspects), random.choice(weapons))
		# best_score = 0
		# best_suspect = None
		# for suspect in suspects:
		# 	score = 0
		# 	if self.known[suspects] == UNKNOWN:


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

game = Game(4, cards_list, names_list)
game.play()