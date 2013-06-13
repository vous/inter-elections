from __future__ import division
from pymongo import MongoClient
import random
import os
from math import sqrt

client = MongoClient()
db = client['election-sim']
voters = db.voter_collection

from election_classes import *

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

def generate_list_of_candidates(number):
	for num in range(number):
		cname = str(raw_input("Name:\n>> "))
		cef = float(raw_input("Econ?:\n>> "))
		ccf = float(raw_input("Civil?:\n>> "))
		c = Candidate.create(name = cname, ef = cef, cf = ccf)
		print "\n"

def point_distance(p0, p1):
    return sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

def get_distance_from_candidate(voter, candidate_info):
	# Essentially just distance formula
	vef = float(voter.econ_freedom)
	vcf = float(voter.civil_freedom)
	cef, ccf = candidate_info
	dist = point_distance((cef, ccf), (vef, vcf))
	return dist

def choose_candidate(voter):
	distances = {}
	for candidate in Candidate.select():
		candidate_info = [candidate.ef, candidate.cf]
		distance = get_distance_from_candidate(voter, candidate_info)
		candidate.dist = distance
		candidate.save()
	# Now find the smallest distance, and select that candidate
	min_dist = 1000.0
	winner = 0
	for candidate in Candidate.select():
		if candidate.dist < min_dist:
			min_dist = candidate.dist
			winner = candidate.id
		else:
			continue
	# We have a winner...
	return winner

def add_votes(candidate_id, votes):
	candidate = Candidate.get(Candidate.id == candidate_id)
	candidate.votes = candidate.votes + votes
	candidate.save()

def vote_all_voters():
	start = 1
	for voter in voters.find():
		vg = create_voter_group(voter["population"], voter["econ_freedom"], voter["civil_freedom"])
		candidate_id = choose_candidate(vg)
		add_votes(candidate_id, vg.population)
		print start
		start = start + 1
	print "Done Voting!"

def main():
	# Remove the candidates db
	os.system("rm 'candidates.db'")
	print "Removed Old Candidate Database"
	os.system("python election_classes.py")
	print "Setup Database"
	num_candidates = int(raw_input("How many candidates?\n>> "))
	generate_list_of_candidates(num_candidates)
	vote_all_voters()

	# now print out the results
	for candidate in Candidate.select():
		print "%s -- %s votes" % (candidate.name, "{:,}".format(candidate.votes)) 

if __name__ == '__main__':
	main()