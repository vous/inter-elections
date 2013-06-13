from __future__ import division
from pymongo import MongoClient
import md5
import random
from math import hypot
from voter_creator import VoterDefinitions, VoterGroup, create_voter_group

client = MongoClient()
db = client['election-sim']
voters = db.voter_collection

all_candidates = {}

class Candidate:
	def __init__(self, name = "NoName", econ_freedom = 0, civil_freedom = 0, votes = 0):
		self.name = name
		self.hash = self.name
		self.econ_freedom = econ_freedom
		self.civil_freedom = civil_freedom
		self.votes = votes
	def add_votes(self, votes):
		self.votes = self.votes + votes 
	def __repr__(self):
		return "<Candidate name:%s>" % self.name
	def __str__(self):
		return "%s" % self.name

def prompt(phrase):
	return "%s\n>> " % phrase

def get_distance_from_candidate(voter, candidate):
	# Essentially just distance formula
	vef = voter.econ_freedom
	vcf = voter.civil_freedom
	cef = candidate.econ_freedom
	ccf = candidate.civil_freedom

	distance = float(hypot(ccf - vcf, cef - vef))
	return distance

def choose_candidate(voter, list_of_candidates):
	distances = {}
	for c in list_of_candidates.keys():
		candidate = all_candidates[c]
		distance = get_distance_from_candidate(voter, candidate)
		distances[candidate.hash] = distance
	# Now find the smallest distance, and select that candidate
	min_dist = 1000.0
	voted = ""
	for item in distances.keys():
		if distances[item] < min_dist:
			min_dist = distances[item]
			voted = item
		else:
			continue
	# We have a winner...
	can =  [candidate for candidate in list_of_candidates if candidate.hash == voted][0]
	return can

def vote_all_voters():
	all_voters = voters.find()
	for voter in all_voters:
		vg = create_voter_group(voter["population"], voter["econ_freedom"], voter["civil_freedom"])
		chosen_candidate = choose_candidate(vg, all_candidates)
		cc = Candidate(chosen_candidate.name, chosen_candidate.econ_freedom, chosen_candidate.civil_freedom, chosen_candidate.votes)
		cc.add_votes(vg.population)
		all_candidates[cc.hash] = cc
		print "Voter Group has voted, and selected %s, with %s votes" % (chosen_candidate.name, "{:,}".format(vg.population)) 
	print "Done Voting!"

def main():
	number_of_candidates = int(raw_input(prompt("Number of Candidates?")))
	for num in range(number_of_candidates):
		cname = str(raw_input(prompt("Name:")))
		cef = float(raw_input(prompt("Econ?:")))
		ccf = float(raw_input(prompt("Civil?:")))
		c = Candidate(cname, cef, ccf, 0)
		all_candidates[c.hash] = c
		print "\n"
	vote_all_voters()

	print "=-=" * 3
	# Now print out the results
	for c in all_candidates.keys():
		candidate = all_candidates[c]
		print "%s -- %d votes" % (candidate.name, candidate.votes)
	print "Done!"

if __name__ == '__main__':
	main()

