# Contains class definitions for all datastone entries used by HotStreak.
# Also contains updating/displaying methods.

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    total_dollars = ndb.IntegerProperty(default=0)
    total_scores = ndb.IntegerProperty(default=0)
    total_games = ndb.IntegerProperty(default=0)

    @property
    def get_dollars(self):
        if self.total_games > 0:
            return float(self.total_dollars - 100)
        else:
            return 0

    def to_form(self):
        return UserForm(name=self.name,
                        email=self.email,
                        total_scores=self.total_scores,
                        total_dollars=self.total_dollars,
                        total_games=self.total_games,
                        get_dollars=self.get_dollars)

    def update_user(self, dollars, score):
        """Update user scoring."""
        self.total_dollars += dollars
        self.total_scores += score
        self.total_games += 1
        self.put()


class Game(ndb.Model):
    """Game object"""
    dollars = ndb.IntegerProperty(required=True)
    getcard = ndb.IntegerProperty()
    dealercard = ndb.IntegerProperty()
    myscore = ndb.IntegerProperty()
    dealerscore = ndb.IntegerProperty()
    game_over = ndb.BooleanProperty(required=True, default=False)
    user = ndb.KeyProperty(required=True, kind='User')
    history = ndb.PickleProperty(required=True)

    @classmethod
    def new_game(cls, user):
        """Creates and returns a new game"""
          
        num1 = random.choice(range(1, 13))
        num2 = random.choice(range(1, 13))
        game = Game(user=user,
                    getcard = num1,
                    dealercard = num2,
                    myscore = helper(num1),
                    dealerscore = helper(num2), 
                    dollars=10,
                    game_over=False)
        game.history = []
        game.put()
        return game

      

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.getcard = self.getcard
        form.dealercard = self.dealercard
        form.dealerscore = self.dealerscore
        form.myscore = self.myscore
        form.dollars = self.dollars
        form.game_over = self.game_over
        form.message = message
        return form

    def put_Scores(self, user):
        self.game_over = True
        self.put()
        # Add the game to the score 'board'
        scores = Score(user=self.user, date=date.today(),
                      scores=self.myscore)
        scores.put()
        user.get().update_user(self.dollars, self.myscore)


class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    scores = ndb.IntegerProperty(required=True)

    def to_form(self):
        return ScoreForm(user_name=self.user.get().name, date=str(self.date),
                         scores=self.scores)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    dollars = messages.IntegerField(2)
    getcard = messages.IntegerField(3)
    dealercard = messages.IntegerField(4)
    game_over = messages.BooleanField(5, required=True)
    message = messages.StringField(6, required=True)
    user_name = messages.StringField(7, required=True)
    myscore = messages.IntegerField(8)
    dealerscore = messages.IntegerField(9)


class GameForms(messages.Message):
    """Return multiple GameForms"""
    items = messages.MessageField(GameForm, 1, repeated=True)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    dicision = messages.StringField(1, required=True)


class ScoreRequestForm(messages.Message):
    """Used to limit the number of returned Scores"""
    num_results = messages.IntegerField(1, required=False, default=5)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    scores = messages.IntegerField(3)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class UserForm(messages.Message):
    """User Form"""
    name = messages.StringField(1, required=True)
    email = messages.StringField(2)
    total_scores = messages.IntegerField(3, required=True)
    total_dollars = messages.IntegerField(4, required=True)
    total_games = messages.IntegerField(5, required=True)
    get_dollars = messages.FloatField(6, required=True)


class UserForms(messages.Message):
    """Container for multiple User Forms"""
    items = messages.MessageField(UserForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)

# if card's value is below 10, return the value; otherwise return 10
def helper(card):
        if (card > 10):
            return 10
        else:
            return card  