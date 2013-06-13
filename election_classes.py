from peewee import *
peewee_db = SqliteDatabase('candidates.db')

class Candidate(Model):
	name = CharField()
	ef = FloatField()
	cf = FloatField()
	dist = FloatField(default = 0.0)
	votes = IntegerField(default = 0)
	class Meta:
		database = peewee_db
	def __str__(self):
		return self.name
	def __repr(self):
		return "<Candidate name:%s" % self.name

def setup_db():
	Candidate.create_table()

if __name__ == '__main__':
	setup_db()