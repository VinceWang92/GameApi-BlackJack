BlackJack API

##Game Description:
 - This BlackJack is a single player game, like common blackjack game but there are some slight difference in order to meet the api demand. 
1 When registering, you will automatically get 100 dollars, and each game you will bet 10 dollars. 
2.  When a registered user create a new game, you and dealer can get one card separately showing you.
3.  Going to make-move api with the url key, give a decision either hit or stand. If you stand, dealer will get cards until over 16. If you hit, you will get one card. If the card value is Jack, Queen or King, the score is 10. If the card value is Ace, the score is just 1.  If the score of one side is over 21, that score will burst to 0. By comparing the scores, the game will show who wins.
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
 
 - **get_user_rankings** 

 - **new_game**
     
 - **get_game**
    
 - **stop_game**

 - **make_move**
    
 - **get_user_games**

 - **get_game_history**

 - **get_high_scores**
    
 - **get_user_scores**

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
