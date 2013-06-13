import pymongo
from pymongo import MongoClient
import random

client = MongoClient()
db = client['election-sim']
voters = db.voter_collection

class VoterDefinitions:
	def __init__(self):
		self.populist = {"econ": [0, 50], "civil": [0, 50]} # Min/Max X, Min/Max Y
		self.liberal = {"econ": [0, 50], "civil": [50, 100]}
		self.conservative = {"econ": [50, 100], "civil": [0, 50]}
		self.libertarian = {"econ": [50, 100], "civil": [50, 100]}
	def get_classification(self, econ_freedom, civil_freedom):
		ef = econ_freedom
		cf = civil_freedom
		is_match = 0
		groups = [self.populist, self.liberal, self.conservative, self.libertarian]
		names = ["populist", "liberal", "conservative", "libertarian"]
		cur_count = 0
		for group in groups:
			gefr = group["econ"] # Group Econ Freed. Range
			gcfr = group["civil"] # Group Civil Freed. Range

			# Check the econ scores
			is_match  = is_match + 1 if gefr[0] <= ef <= gefr[1] else is_match

			# Check the civil scores
			is_match  = is_match + 1 if gcfr[0] <= cf <= gcfr[1] else is_match

			if is_match == 2:
				# Is a perfect match
				return names[cur_count]

			# Otherwise, is not a match
			cur_count = cur_count + 1
			is_match = 0
		# No match
		return "error" # Error
class VoterGroup:
	def __init__(self, population=0, civil_freedom=0, econ_freedom=0):
		self.population = population
		self.civil_freedom = civil_freedom
		self.econ_freedom = econ_freedom # Initializing values
	def translate_to_dictionary(self):
		# Values should already be set
		dictionary = {
			"population": self.population,
			"econ_freedom": self.econ_freedom,
			"civil_freedom": self.civil_freedom
		}
		return dictionary

def create_voter_group(population, econ_freedom, civil_freedom):
	ef = econ_freedom
	cf = civil_freedom
	pop = population

	vg = VoterGroup(population = pop, econ_freedom = ef, civil_freedom = cf)
	return vg

def get_voter_group_dict(voter_group):
	return voter_group.translate_to_dictionary()

def save_voter_group(voter_group):
	vgd = get_voter_group_dict(voter_group) # Voter Group Dict
	vg_id = voters.insert(vgd)
	return vg_id

def store_many_voter_groups(number_to_create):
	num = number_to_create
	for n in range(num):
		vg_pop = random.randint(175, 315) # average of 250
		vg_ef = random.randint(0, 100)
		vg_cf = random.randint(0, 100)

		vg = create_voter_group(vg_pop, vg_ef, vg_cf)
		vg_id = save_voter_group(vg)
		print "Created Voter Group"
	print "Finished Adding %d Voter Groups" % num

def get_population_all_voter_groups():
	population = 0
	for voter in voters.find():
		population = population + voter["population"]
	return population

def main():
	number_to_create = int(raw_input("How many to create?\n>> "))
	store_many_voter_groups(number_to_create)
	print "=" * 8
	total_population = get_population_all_voter_groups()
	print "Total Population is: %s voters" % ("{:,}".format(total_population))
	print "\nDone!"

if __name__ == '__main__':
	main()