BlackJack API

##Game Description:
 - This BlackJack is a single player game, like common blackjack game but there are some slight difference in order to meet the api demand. 
1.   When registering, you will automatically get 100 dollars, and each game you will bet 10 dollars. 
2.  When a registered user create a new game, you and dealer can get one card separately showing you.
3.  Going to make-move api with the url key, give a decision either hit or stand. If you stand, dealer will get cards until over 16. If you hit, you will get one card. If the card value is Jack, Queen or King, the score is 10. If the card value is Ace, the score is just If the score of one side is over 21, that score will burst to 0. By comparing the scores, the game will show who wins.
4.  Get High Scores Api: You can see top scores ordered and created by all users.
5.  Get User Ranking: Not rank by average score, because user plays with the dealer and try to get just more score than the dealer. So I rank players by the dollars they won. 

## Installation Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
in the App Engine admin console and would like to use to host your instance of this sample.
2.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer. (Or Run Google App Engine Launcher. Choose to add an existing application and select
the project's directory. Click the run button.)
3.  Ensure it's running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer. 
 

##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.
 - Design.txt: Description of the game design decisions and process.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists. The welcome email is added to the task queue.

 - **get_user_rankings** 
    - Path: 'user/rankings'
    - Method: GET
    - Parameters: NONE
    - Returns: All users in the database in descending order by dollars won.
    - Description: Ranks all the users in the database based on their dollars
    won.   

 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. user_name provided must correspond to an
    existing user - will raise a NotFoundException if not. Also informs the user
    that they begin the game with 100 dollars.

 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game. Displays the player's and dealer's former
    cards.
    
 - **stop_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: DELETE
    - Parameters: urlsafe_game_key
    - Returns: Message that they game has been deleted.
    - Description: Deletes an active game. Raises exceptions if the game does not
    exist or if the game has been completed.

 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, dicision
    - Returns: GameForm with new game state.
    - Description: Make a dicision of Stand or Hit.
    
 - **get_user_games**
    - Path: 'user/games'
    - Method: GET
    - Parameters: user_name, email (optional)
    - Returns: GameForms for all active and finished games belonging to a user.
    - Description: Returns all games in the database belonging to a specific user 
    that have played.

 - **get_game_history**
    - Path: 'game/{urlsafe_game_key}/history'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: String message containing the history of the specified game.
    - Descriptions: Displays a history of the user's guesses for a specific game.

 - **get_high_scores**
    - Path: 'scores'
    - Method: PUT
    - Parameters: num_results
    - Returns: ScoreForms.
    - Description: Returns all Scores in the database order by the scores
    in descending order. The number of displayed scores can be limited by the user.
    
 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms. 
    - Description: Returns all Scores recorded by the given player.
    Will raise a NotFoundException if the User does not exist.

##Models Included:
 - **User**
    - Stores unique user_name, (optional) email address, total points scored and
    total games played.
    
 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.
    
 - **Score**
    - Records completed games. Associated with Users model via KeyProperty.
    
##Forms Included:
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, points, next card, game_over flag, message, user_name).
 - **NewGameForm**
    - Used to create a new game (user_name)
 - **MakeMoveForm**
    - Inbound make move form (guess, bet).
 - **ScoreRequestForm**
    - Userd to limit the number of returned scores.
 - **ScoreForm**
    - Representation of a completed game's Score (user_name, date, points).
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **UserForms**
    - Representation of a User's information (user_name, email, total_points, total_games, average_score)
 - **UserForms**
    - Multiple UserForm Container
 - **StringMessage**
    - General purpose String container.
