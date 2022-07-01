# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import random
from text import difficulty_drinks, trueOrfalse, joker, neverHaveIEver, wouldYouRather

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        atr = handler_input.attributes_manager.session_attributes
        atr["paused"] = "false"
        atr["nameinit"] = "false"
        atr["gameinit"] = "false"
        
        speak_output = "Welcome to DrinkingGames! Who is playing tonight?"
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class PlayerIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        atr = handler_input.attributes_manager.session_attributes
        if (atr["nameinit"] =="true"):
            return False
        return ask_utils.is_intent_name("PlayerIntent")(handler_input)

    def handle(self, handler_input):
        
        #list of player names
        slots = handler_input.request_envelope.request.intent.slots
        playerNames = slots["names"].value
        playerNamesList = playerNames.split(" ")
        
        #highscore list
        length = len(playerNamesList)
        highScore = [0]
        while(length > 1):
            highScore.append(0)
            length -= 1
        
        #session attribute für Spieler und Besteliste
        atr = handler_input.attributes_manager.session_attributes
        atr["playerNamesList"] = playerNamesList
        atr["highscore"] = highScore
        atr["nameinit"] = "true"
        
        speak_output = 'Nice to have you here! So which game do you want to play? '
        speak_output += 'You can choose between three games: <emphasis level="moderate">True or False</emphasis>, <emphasis level="moderate">Never have I ever</emphasis> and<emphasis level="moderate">Would you rather</emphasis>'
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class GameIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        atr = handler_input.attributes_manager.session_attributes
        if (atr["gameinit"] =="true"):
            return False
        return ask_utils.is_intent_name("GameIntent")(handler_input)

    def handle(self, handler_input):
        
        #session attributes
        atr = handler_input.attributes_manager.session_attributes
        #slot
        slots = handler_input.request_envelope.request.intent.slots
        
        #save difficulty and number of rounds
        drink = slots["difficulty"].value
        rounds = slots["time"].value
        game = slots["game"].value
        
        atr["rounds"] = rounds
        atr["usedNumbers"] = [0]
        atr["game"] = game
        atr["gameinit"] = "true"
        # output which drink is recommended and set joker probability
        # lower joker_prob -> higher chance of getting a joker
        if drink == "easy":
            atr["joker_prob"] = str(2)
            speak_output = difficulty_drinks[0]
        elif drink == "advance":
            atr["joker_prob"] = str(5)
            speak_output = difficulty_drinks[1]
        else:
            atr["joker_prob"] = str(8)
            speak_output = difficulty_drinks[2]
        
        speak_output = speak_output + "If you want the rules of " + game + " just ask me for the rules of the game "
        speak_output += "If you already know the rules... are you ready?"
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class PlayingIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        atr = handler_input.attributes_manager.session_attributes
        if (atr["paused"] =="true" or atr["nameinit"] == "false" or atr["gameinit"] == "false"):
            return False
        return ask_utils.is_intent_name("PlayingIntent")(handler_input)

    def handle(self, handler_input):
        atr = handler_input.attributes_manager.session_attributes
        
        speak_output = ""
        joker_prob = int(atr["joker_prob"])
        # Joker or not?
        if (random.randrange(10)<joker_prob):    # the lower joker_prob, the more likely it is to get a joker
            speak_output = '<audio src="soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_bridge_02"/> <amazon:emotion name="excited" intensity="high">JOKER!</amazon:emotion> '+joker[random.randrange(len(joker))]+' <break time="5s"/> Alright. Next question. '
            
        
        #game
        game = atr["game"]
        game = game.lower()
        
        #round
        game_round = atr["rounds"]
        game_round = int(game_round)
        
        #Used Questions
        used_numbers = atr["usedNumbers"]
        length=0
        
        #list length
        if (game == "true or false"):
            length = len(trueOrfalse)
        elif (game == "never have i ever"):
            length = len(neverHaveIEver)
        elif (game == "would you rather"):
            length = len(wouldYouRather)
        
        if(game_round > 0):
            #random number
            randInt = random.randrange(length)
            
            #checking if random number is already used
            if(game == "true or false"):
                while((randInt%2 == 0) or (randInt in used_numbers)):
                    randInt = random.randrange(length)
            elif(game == "never have i ever" or game == "would you rather"):
                while(randInt in used_numbers):
                    randInt = random.randrange(length)
                
            #save used number, so questions won't repeat
            used_numbers.append(randInt)
            atr["usedNumbers"] = used_numbers
            
            #decrease rounds
            game_round -= 1
            atr["rounds"] = game_round
            
            
            if (game == "true or false"):
                #picks random player to answer question
                playerName = atr["playerNamesList"]
                playerLength = len(playerName)
                randomInt = random.randrange(playerLength)
                #for highscore
                atr["randomInt"] = randomInt
                playerNameGuess = playerName[randomInt].lower()
                speak_output = speak_output+playerNameGuess + " this one is for you. " + trueOrfalse[randInt] + " Is it true or false ?"
                
            elif(game == "never have i ever"):
                
                speak_output = speak_output+ "Now: "+ neverHaveIEver[randInt]
                
            elif(game == "would you rather"):
                playerName = atr["playerNamesList"]
                playerLength = len(playerName)
                randomInt = random.randrange(playerLength)
                playerNameGuess = playerName[randomInt].lower()
                
                speak_output = speak_output+playerNameGuess + " this one is for you. " + wouldYouRather[randInt]
                
        #end of game, no rounds left
        else:
            speak_output = "Game Over"
            return (
            handler_input.response_builder
                .speak(speak_output)
                .response
            )
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class CorrectionIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        #atr = handler_input.attributes_manager.session_attributes
        #game =atr["game"] 
        #if ( game.lower()!="true or false"):
        #    return False
        return ask_utils.is_intent_name("CorrectionIntent")(handler_input)
    
    def handle(self, handler_input):
        #user input
        eingabe = handler_input.request_envelope.request.intent.slots['userInput'].value
        eingabe = eingabe.lower()
        
        #gamerounds
        atr = handler_input.attributes_manager.session_attributes
        game_round = atr["rounds"]
        game_round = int(game_round)
        
        #randomInt indize for player
        randomInt = atr["randomInt"]
        randomInt = int(randomInt)
        
        #highscore list
        highscore = atr["highscore"]
        
        #list of used numbers
        used_numbers = atr["usedNumbers"]
        
        #finding right answer
        intAnswer = used_numbers[-1]
        right_answer = trueOrfalse[intAnswer+1]
        
        #player names
        playerNames = atr["playerNamesList"]
        lengthPlayerNames = len(playerNames)
        
        #checking if user input is correct 
        if((eingabe.lower() in right_answer.lower())):
            #points for right answer for player
            highscore[randomInt] += 100
            atr["highscore"] = highscore
            speak_output = '<amazon:emotion name="excited" intensity="medium" >Thats correct! 100 points for you </amazon:emotion> ' + playerNames[randomInt] + "."
        else:
            #points for right answer for player
            highscore[randomInt] -= 50
            atr["highscore"] = highscore
            speak_output = '<amazon:emotion name="disappointed" intensity="medium">Thats not correct! -50 points for </amazon:emotion> ' + playerNames[randomInt] + "."
        
        if(game_round != 0):
            speak_output += " Guys Are you ready for the next question?"
            
            return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
            )
        
        #output highscore
        points = atr["highscore"]
        index = 0
        highscoreResult = "The results are "
        
        #gives out every players points
        while(index < lengthPlayerNames):
            highscoreResult += playerNames[index] + " has " + str(points[index]) + " points. "
            index += 1
        
        speak_output += " That was your last question. " + highscoreResult + "We hope you liked our Drinking Game! Have fun partying!"
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class PauseIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.PauseIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        atr = handler_input.attributes_manager.session_attributes
        atr["paused"] = "true"
        speak_output = "The Game is paused"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class ResumeIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        atr = handler_input.attributes_manager.session_attributes
        if (atr["paused"] == "false"):
            return False
        return ((ask_utils.is_intent_name("AMAZON.ResumeIntent")(handler_input)))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        atr = handler_input.attributes_manager.session_attributes
        atr["paused"] = "false"
        speak_output = "Great. The game resumes."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class ExplainIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("ExplainIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        game = slots["game"].value
        game = game.lower()
        
        speak_output = ""
        
        if (game == "true or false"):
            speak_output += "I will make a statement to which one of you has to decide if my statement is true or if it is false. I will choose who has to answer. If your answer is correct, you can decide who has to drink."
            speak_output += "If your answer is incorrect you have to drink yourself. I will keep a highscore to see who is the best. The best players will get a reward, while the worst players will get punished"
        elif (game == "never have i ever"):
            speak_output += "I will make a statement like: never have i ever eaten a booger. If you have never eaten a booger in your life before you dont have to drink. But if you have eaten a booger before you have to drink."
        elif (game == "would you rather"):
            speak_output += "I will choose one of you and ask you a question where you have to decide between the first option or the second option. If the majority of Players agree with you, you can choose who has to drink."
            speak_output += "If the majority disagrees with you, you have to drink. If it is a tie, everyone has to drink."
        else :
            speak_output += 'You can choose between three games: <prosody rate="slow">True or False</prosody>, <prosody rate="slow">Never have I ever</prosody> and <prosody rate="slow">Would you rather</prosody>'
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class RepeatIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("RepeatIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        atr = handler_input.attributes_manager.session_attributes
        used_numbers=atr["usedNumbers"]    # list of integers
        game = atr["game"]
        game = game.lower()
        
        # get last element in list
        last_number = used_numbers[-1]
        
        if (last_number == 0):
            speak_output = "I have not asked a question yet. To continue please say "
            return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )
        
        last_question = ""
        
        if (game == "true or false"):
            last_question += trueOrfalse[last_number]
        elif (game == "never have i ever"):
            last_question += neverHaveIEver[last_number]
        elif (game == "would you rather"):
            last_question += wouldYouRather[last_number]
        else:
            last_question = "It seems we ran in a problem here."
        
        
        speak_output = 'I repeat <break time="1s"/> ' + last_question

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class SettingsIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("SettingsIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        atr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        
        if (slots["einstellungen"].lower() == "player"):
            atr["nameinit"] = "false"
            speak_output = "Who is Playing?"
        elif (slots["einstellingen"].lower() == "player"):
            atr["gameinit"] = "false"
            speak_output = "What game do you want to play?"
        else:
            speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can say Hello or Help. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        atr = handler_input.attributes_manager.session_attributes
        if (intent_name.lower() == "playingintent"):
            if (atr["paused"] == "true"):
                speak_output = "If you want to continue the game, just say Resume"
            elif (atr["nameinit"] == "false"):
                speak_output = "Please tell me your names first"
            elif (atr["gameinit"] == "false"):
                speak_output = "Please tell me what game you want to play first"
            else:
                speak_output = " "
        elif (intent_name.lower() == "playerintent"):
            speak_output = 'if you want to change the player names, say <emphasis level="moderate">player settings</emphasis>'
        elif (intent_name.lower() == "gameintent"):
            speak_output = 'if you want to change the player names, say <emphasis level="moderate">game settings</emphasis>'
        else:
            speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(PlayerIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(ExplainIntentHandler())
sb.add_request_handler(PauseIntentHandler())
sb.add_request_handler(ResumeIntentHandler())
sb.add_request_handler(RepeatIntentHandler())
sb.add_request_handler(SettingsIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(CorrectionIntentHandler())
sb.add_request_handler(GameIntentHandler())
sb.add_request_handler(PlayingIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()