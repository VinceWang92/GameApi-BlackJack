# Contains api endpoints for game functionality. make_move() contains
# game logic for a stand or hit betting.

import logging
import endpoints
import random
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from models import User, Game, Score
from models import StringMessage, NewGameForm, GameForm, MakeMoveForm,\
    ScoreForms, GameForms, ScoreRequestForm, UserForm, UserForms
from utils import get_by_urlsafe

SCORE_REQUEST = endpoints.ResourceContainer(ScoreRequestForm)
NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1,
                                           required=True),
                                           email=messages.StringField(2))

MEMCACHE_AVERAGE_SCORE = 'AVERAGE_SCORE'

cardValues = ("Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight",
              "Nine", "Ten", "Jack", "Queen", "King")
dealer_score = 0

@endpoints.api(name='blackJack', version='v1')
class blackJackApi(remote.Service):
    """Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        print "#"    
        user = User(name=request.user_name, email=request.email, total_dollars=100)
        user.put()

        # Send Welcome email.
        taskqueue.add(url='/tasks/send_user_email',
                      params={'user_key': user.key})

        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(response_message=UserForms,
                      path='user/ranking',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Return all Users ranked by their dollars won"""
        users = User.query(User.total_games > 0).fetch()
        users = sorted(users, key=lambda x: x.get_dollars, reverse=True)
        return UserForms(items=[user.to_form() for user in users])

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new BlackJack game. For a new user, he has 100 initial dollars."""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException('User does not exist!')
        game = Game.new_game(user.key)
        return game.to_form('Time To Play BlackJack! You have %d dollars' %(user.total_dollars))

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            if game.game_over:
              return game.to_form('The game is already over!')
            msg = "The dealer score is %d. Your score is %d" %(game.dealerscore, game.myscore)
            return game.to_form(msg + '. Hit or Stand?')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}',
                      name='stop_game',
                      http_method='DELETE')
    def stop_game(self, request):
        """Ends and Deletes a game that is currently in-progress"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game and not game.game_over:
            game.key.delete()
            return StringMessage(message='Game with key: {} deleted.'.
                                 format(request.urlsafe_game_key))
        elif game and game.game_over:
            raise endpoints.BadRequestException(
                            'Cannot delete a completed game!')
        else:
            raise endpoints.NotFoundException('That game does not exist!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Make a dicision of Stand or Hit"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        
        my_dicision = request.dicision

        if game.game_over:
            return game.to_form('Game already over!')

        if my_dicision == "stand":
          msg = ""
          while (game.dealerscore < 16):
            dealercard = random.choice(range(1, 13))
            game.dealerscore += helper(dealercard)
            msg = msg + "Dealer got a %s. " %(cardValues[dealercard - 1])
          if (game.dealerscore > 21):
            msg1 =  "Dealer's score is 0, and you win the game"
            game.history.append(msg1)
            game.game_over = True
            game.put()
            game.put_Scores(game.user)
            return game.to_form(msg + msg1)
          else:
            if (game.dealerscore> game.myscore):
              msg1 = "Dealer's score is %d, and your score is %d. You lose!" %(game.dealerscore, game.myscore)
              game.history.append(msg1)
              game.dollars = -game.dollars
              game.game_over = True
              game.put()
              game.put_Scores(game.user)
              return game.to_form(msg + msg1)
            if (game.dealerscore < game.myscore):
              msg1 =  "Dealer's score is %d, and your score is %d. You win!" %(game.dealerscore, game.myscore)
              game.history.append(msg1)
              game.game_over = True
              game.put()
              game.put_Scores(game.user)
              return game.to_form(msg + msg1) 
            else:
              msg1 = "Dealer's score is %d, and your score is %d. Tie!" %(game.dealerscore, game.myscore)
              game.history.append(msg1)
              game.dollars = 0
              game.game_over = True
              game.put()
              game.put_Scores(game.user)
              return game.to_form(msg + msg1)  

        if my_dicision == "hit":
          dealer_stand = False;
          if (game.dealerscore < 16):
            dealercard = random.choice(range(1, 13))
            game.dealercard = dealercard
            game.dealerscore = helper(dealercard) + game.dealerscore 
          else:
            dealer_stand = True;
          mycard = random.choice(range(1, 13))
          game.getcard = mycard
          game.myscore = helper(mycard) + game.myscore
          if (game.myscore > 21):
            game.myscore = 0
            msg1 = "Dealer's score is %d, and your score is %d. You lose!" %(game.dealerscore, game.myscore)
            game.history.append(msg1)
            game.dollars = -game.dollars
            game.game_over = True
            game.put()
            game.put_Scores(game.user)
            return game.to_form(msg1)
          if (game.dealerscore > 21):
            game.dealerscore = 0
            msg1 = "Dealer's score is %d, and your score is %d. You win!" %(game.dealerscore, game.myscore)
            game.history.append(msg1)
            game.game_over = True
            game.put()
            game.put_Scores(game.user)
            return game.to_form(msg1)
          if dealer_stand:
            msg = "Dealer had to stand since the score is over 16, and your card is %s. " %(cardValues[mycard - 1])  
          else:
            msg = "Dealer's card is %s, and your card is %s. " %(cardValues[dealercard - 1], cardValues[mycard - 1])                         
          msg = msg + "Dealer's score is %d, and your score is %d. Stand or Hit?" %(game.dealerscore, game.myscore)
          game.put()
          return game.to_form(msg) 

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='user/games',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Returns the active and finished games of a specific user"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.BadRequestException('User not found!')
        games = Game.query(Game.user == user.key)
        #.filter(Game.game_over == False)
        return GameForms(items=[game.to_form("") for game in games])

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}/history',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Returns final scores of dealer and player of a game."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found')
        return StringMessage(message=str(game.history))

    @endpoints.method(request_message=SCORE_REQUEST,
                      response_message=ScoreForms,
                      path='scores',
                      name='get_high_scores',
                      http_method='PUT')
    def get_high_scores(self, request):
        """Return top scores ordered by all users' scores"""
        rlen = request.num_results
        scores = Score.query().order(-Score.scores)
        f_scores = scores.fetch(rlen)
        return ScoreForms(items=[score.to_form() for score in f_scores])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        scores = Score.query(Score.user == user.key)
        return ScoreForms(items=[score.to_form() for score in scores])

# If card is Jack, Queen or King, return score 10 
def helper(card):
  if card > 10:
    return 10
  else:
    return card

api = endpoints.api_server([blackJackApi])
