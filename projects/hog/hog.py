"""The Game of Hog."""

from dice import four_sided, six_sided, make_test_dice
from ucb import main, trace, log_current_line, interact

GOAL_SCORE = 100 # The goal of Hog is to score 100 points.

######################
# Phase 1: Simulator #
######################

# Taking turns

def roll_dice(num_rolls, dice=six_sided):
    """Roll DICE for NUM_ROLLS times.  Return either the sum of the outcomes,
    or 1 if a 1 is rolled (Pig out). This calls DICE exactly NUM_ROLLS times.

    num_rolls:  The number of dice rolls that will be made; at least 1.
    dice:       A zero-argument function that returns an integer outcome.
    """
    # These assert statements ensure that num_rolls is a positive integer.
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls > 0, 'Must roll at least once.'
    "*** YOUR CODE HERE ***"
    
    count, total, score= 0, 0, 0
    pig_out = False

    while count < num_rolls:
        score = dice()
        #Pig out rule: if dice() == 1, return 1
        if score == 1:
            pig_out = True
        else:
            total += score 
        count += 1
    #If a one was rolled, then return 1.
    if pig_out:
        return 1
    else:
        return total

def take_turn(num_rolls, opponent_score, dice=six_sided):
    """Simulate a turn rolling NUM_ROLLS dice, which may be 0 (Free bacon).

    NOTE: Return number of points scored for this round

    num_rolls:       The number of dice rolls that will be made.
    opponent_score:  The total score of the opponent.
    dice:            A function of no args that returns an integer outcome.
    """
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls >= 0, 'Cannot roll a negative number of dice.'
    assert num_rolls <= 10, 'Cannot roll more than 10 dice.'
    assert opponent_score < 100, 'The game should be over.'
    "*** YOUR CODE HERE ***"
    #Free Bacon: If a player rolls zero dice, they score one more than the
    #largest digit in their opponent's score.
    if(num_rolls == 0):
        return 1 + max (opponent_score // 10, opponent_score % 10)
    
    #Proceed to roll num_rolls # of dice
    else:
        return roll_dice(num_rolls, dice)

# Playing a game
def select_dice(score, opponent_score):
    """Select six-sided dice unless the sum of SCORE and OPPONENT_SCORE is a
    multiple of 7, in which case select four-sided dice (Hog wild).

    >>> select_dice(4, 24) == four_sided
    True
    >>> select_dice(16, 64) == six_sided
    True
    >>> select_dice(0, 0) == four_sided
    True
    """
    "*** YOUR CODE HERE ***"
    #Hog Wild rule: If your (score + opponent score) is divisable by 7,then select four_sided dice
    #Else, select the six_sided dice.
    if ((score + opponent_score) % 7) == 0:
        return four_sided
    return six_sided

def other(who):
    """Return the other player, for a player WHO numbered 0 or 1.

    >>> other(0)
    1
    >>> other(1)
    0
    """
    return 1 - who

def play(strategy0, strategy1, goal=GOAL_SCORE):
    """Simulate a game and return the final scores of both players, with
    Player 0's score first, and Player 1's score second. Including Swine Swap.

    A strategy is a function that takes two total scores as arguments
    (the current player's score, and the opponent's score), and returns a
    number of dice that the current player will roll this turn.

    strategy0:  The strategy function for Player 0, who plays first.
    strategy1:  The strategy function for Player 1, who plays second.
    """
    who = 0  # Which player is about to take a turn, 0 (first) or 1 (second)
    
    opponent_score, score = 0, 0 

    while(score < goal and opponent_score < goal):
        #Player 0
        if who == 0:
            num_rolls = strategy0(score, opponent_score)   
            dice = select_dice(score, opponent_score)
            score += take_turn(num_rolls, opponent_score, dice)
        #Player 1
        else:     
            num_rolls = strategy1(opponent_score, score) 
            dice = select_dice(opponent_score, score)
            opponent_score += take_turn(num_rolls, score, dice)
                         
        #Swine swap rule 
        if(score == 2 * opponent_score or opponent_score == 2 * score):
            score, opponent_score = opponent_score, score
 
        #Switch players        
        who = other(who)        

    return score, opponent_score

#######################
# Phase 2: Strategies #
#######################

# Basic Strategy

BASELINE_NUM_ROLLS = 5
BACON_MARGIN = 8

def always_roll(n):
    """Return a strategy that always rolls N dice.

    A strategy is a function that takes two total scores as arguments
    (the current player's score, and the opponent's score), and returns a
    number of dice that the current player will roll this turn.

    >>> strategy = always_roll(5)
    >>> strategy(0, 0)
    5
    >>> strategy(99, 99)
    5
    """
    def strategy(score, opponent_score):
        return n
    return strategy

# Experiments

def make_averaged(fn, num_samples=1000):
    """Return a function that returns the average_value of FN when called.

    To implement this function, you will have to use *args syntax, a new Python
    feature introduced in this project.  See the project description.

    >>> dice = make_test_dice(3, 1, 5, 6)
    >>> averaged_dice = make_averaged(dice, 1000)
    >>> averaged_dice()
    3.75
    >>> make_averaged(roll_dice, 1000)(2, dice)
    6.0

    In this last example, two different turn scenarios are averaged.
    - In the first, the player rolls a 3 then a 1, receiving a score of 1.
    - In the other, the player rolls a 5 and 6, scoring 11.
    Thus, the average value is 6.0.
    """
    def average(*args):
        i = 0
        total = 0
        while(i < num_samples):
            total += fn(*args)
            i += 1
        return total / i
    return average

def max_scoring_num_rolls(dice=six_sided):
    """Return the number of dice (1 to 10) that gives the highest average turn
    score by calling roll_dice with the provided DICE.  Print all averages as in
    the doctest below.  Assume that dice always returns positive outcomes.

    >>> dice = make_test_dice(3)
    >>> max_scoring_num_rolls(dice)
    1 dice scores 3.0 on average
    2 dice scores 6.0 on average
    3 dice scores 9.0 on average
    4 dice scores 12.0 on average
    5 dice scores 15.0 on average
    6 dice scores 18.0 on average
    7 dice scores 21.0 on average
    8 dice scores 24.0 on average
    9 dice scores 27.0 on average
    10 dice scores 30.0 on average
    10
    """
    turn = 1
    highest_avg, highest_turn = 0, 0
    calc_avg = make_averaged(roll_dice)

    while(turn <= 10):        
        current_avg = calc_avg(turn, dice)        
        print(turn, "dice scores", current_avg, "on average")
        if current_avg > highest_avg:
            highest_turn = turn
            highest_avg = current_avg
        turn += 1
    return highest_turn

def winner(strategy0, strategy1):
    """Return 0 if strategy0 wins against strategy1, and 1 otherwise."""
    score0, score1 = play(strategy0, strategy1)
    if score0 > score1:
        return 0
    else:
        return 1

def average_win_rate(strategy, baseline=always_roll(BASELINE_NUM_ROLLS)):
    """Return the average win rate (0 to 1) of STRATEGY against BASELINE."""
    win_rate_as_player_0 = 1 - make_averaged(winner)(strategy, baseline)
    win_rate_as_player_1 = make_averaged(winner)(baseline, strategy)
    return (win_rate_as_player_0 + win_rate_as_player_1) / 2 # Average results

def run_experiments():
    """Run a series of strategy experiments and report results."""
    if False: # Change to False when done finding max_scoring_num_rolls
        six_sided_max = max_scoring_num_rolls(six_sided)
        print('Max scoring num rolls for six-sided dice:', six_sided_max)
        four_sided_max = max_scoring_num_rolls(four_sided)
        print('Max scoring num rolls for four-sided dice:', four_sided_max)

    if False: # Change to True to test always_roll(8)
        print('always_roll(8) win rate:', average_win_rate(always_roll(8)))

    if False: # Change to True to test always_roll(5)
        print('always_roll(5) win rate:', average_win_rate(always_roll(5)))

    if False: # Change to True to test bacon_strategy
        print('bacon_strategy win rate:', average_win_rate(bacon_strategy))

    if False: # Change to True to test swap_strategy
        print('swap_strategy win rate:', average_win_rate(swap_strategy))

    if True: # Change to True to test final_strategy
        print('final_strategy win rate:', average_win_rate(final_strategy))

    "*** You may add additional experiments as you wish ***"

# Strategies

def bacon_strategy(score, opponent_score):
    """This strategy rolls 0 dice if that gives at least BACON_MARGIN points,
    and rolls BASELINE_NUM_ROLLS otherwise.

    >>> bacon_strategy(0, 0)
    5
    >>> bacon_strategy(70, 50)
    5
    >>> bacon_strategy(50, 70)
    0
    """
    "*** YOUR CODE HERE ***"
    #Free Bacon: If a player rolls zero dice, she scores one more than the
    #largest digit in her opponent's score.
    #Calculate the free bacon score: 1 + max (opponent_score // 10, opponent_score % 10)
    bacon_score = 1 + max (opponent_score // 10, opponent_score % 10)
    if bacon_score >= BACON_MARGIN:
        return 0
    else:
        return BASELINE_NUM_ROLLS

def swap_strategy(score, opponent_score):
    """This strategy rolls 0 dice when it would result in a beneficial swap and
    rolls BASELINE_NUM_ROLLS if it would result in a harmful swap. It also rolls
    0 dice if that gives at least BACON_MARGIN points and rolls
    BASELINE_NUM_ROLLS otherwise.

    >>> swap_strategy(23, 60) # 23 + (1 + max(6, 0)) = 30: Beneficial swap
    0
    >>> swap_strategy(27, 18) # 27 + (1 + max(1, 8)) = 36: Harmful swap
    5
    >>> swap_strategy(50, 80) # (1 + max(8, 0)) = 9: Lots of free bacon
    0
    >>> swap_strategy(12, 12) # Baseline
    5
    """
    "*** YOUR CODE HERE ***"
    bacon_score = score + 1 + max (opponent_score // 10, opponent_score % 10)

    #Free bacon into beneficial swine swap
    if (bacon_score == (opponent_score // 2)):
        return 0
    #Free bacon into harmful swap
    elif (bacon_score == opponent_score * 2):
        return BASELINE_NUM_ROLLS
    else: 
        #Free bacon score is larger than our bacon_margin = 5
        return bacon_strategy(score, opponent_score)

RISKIER_ROLL = 6
SAFER_ROLL = 4
HOG_WILD_ROLL = 4

def final_strategy(score, opponent_score):
    """Write a brief description of your final strategy.

    We break our code into two parts: 
        1.) We are losing (score < opponent_score)
            a.) We try and use the special rules (Pig out, swine swap, hog wild, and free bacon) to our advantage.
            b.) Otherwise, we play riskier and roll 6.
        2.) We are winning (score >= opponent_score)
            a.) We try and use the special rules (Pig out, swine swap, hog wild, and free bacon) to our advantage.
            b.) Otherwise, we play safer and roll 4.

    When we are losing:
        1.) We prioritize free baconing our opponent into a beneficial swine swap for us.
        2.) If we are one point away from a beneficial swine swap, employ our ROLL 10 STRAT. 
            a.) It's a hail mary strategy. Rolling 10 dice gives us the greatest chance of pigging out and getting a 1.
                If we don't get a one, we get a large boost of points! Win win!
        3.) Then we check if our bacon score is a reasonable score (bacon_score >= 8). If so, free bacon!
        4.) We try to force our opponent into hog wild by using free bacon.
        5.) Now we check if we in hog wild. 
            a.) If we are, then we roll 4 dice. (Maximize our points)
        6.) If we are not in hog wild, and because we are down in points, we make a risker roll (roll 6 dice).

    When we are winning:
        1.) We avoid free baconing ourselves into a harmful swine swap. We instead make a safer roll (roll 4 dice)
        2.) We check if our bacon score is a reasonable score (bacon_score >= 8). If so, free bacon!
        3.) We try to force our opponent into hog wild by using free bacon.
        4.) Now we check if we in hog wild. 
            a.) If we are, then we roll 4 dice. (Maximize our points)
        5.) If we are not in hog wild, and because we are up in points, we make a safer roll (roll 4 dice). 
    """
    "*** YOUR CODE HERE ***"
    #Calculating the points IF we free bacon'D.
    bacon_score = 1 + max (opponent_score // 10, opponent_score % 10)
    
    #You have less score than your opp.
    if (score < opponent_score): 
        #Free bacon into beneficial swine swap
        if (score + bacon_score == (opponent_score // 2)):            
            return 0

        #The Roll 10 strategy!
        #If we one point away from a good swine swap, we roll 10 dice. (Greatest chance of pig out = rolling a 1)
        #OR, if 10 works out, then we get a large boost of points! Win win!
        elif (score == ((opponent_score // 2) - 1)):
            return 10
        
        else:
        #Free bacon score is larger than our bacon_margin = 8
            if (bacon_score >= BACON_MARGIN):
                return 0
            else:
                #Forcing opp into hog wild using free bacon
                if (bacon_score + score + opponent_score % 7 == 0):
                    return 0
                else:
                    #If WE are in hog wild (dice = 4 sided)
                    if (score + opponent_score % 7 == 0):
                        return HOG_WILD_ROLL
                    #All else fails, make a riskier roll (roll 6)
                    else:
                        return RISKIER_ROLL
    
    #You have more score than your opp.
    else: 
        #Avoid free baconing ourselves into harmful swap 
        if (score + bacon_score == opponent_score * 2):
            return SAFER_ROLL
        else:
        #Free bacon score is larger than our bacon_margin = 8
            if (bacon_score >= BACON_MARGIN):
                return 0
            else:
                #Force opponent into hog wild using free bacon
                if (bacon_score + score + opponent_score % 7 == 0):
                    return 0
                else:
                    #If WE are in hog wild (dice = 4 sided)
                    if (score + opponent_score % 7 == 0):
                        return HOG_WILD_ROLL
                    else:
                        return SAFER_ROLL

##########################
# Command Line Interface #
##########################

# Note: Functions in this section do not need to be changed.  They use features
#       of Python not yet covered in the course.

def get_int(prompt, min):
    """Return an integer greater than or equal to MIN, given by the user."""
    choice = input(prompt)
    while not choice.isnumeric() or int(choice) < min:
        print('Please enter an integer greater than or equal to', min)
        choice = input(prompt)
    return int(choice)

def interactive_dice():
    """A dice where the outcomes are provided by the user."""
    return get_int('Result of dice roll: ', 1)

def make_interactive_strategy(player):
    """Return a strategy for which the user provides the number of rolls."""
    prompt = 'Number of rolls for Player {0}: '.format(player)
    def interactive_strategy(score, opp_score):
        if player == 1:
            score, opp_score = opp_score, score
        print(score, 'vs.', opp_score)
        choice = get_int(prompt, 0)
        return choice
    return interactive_strategy

def roll_dice_interactive():
    """Interactively call roll_dice."""
    num_rolls = get_int('Number of rolls: ', 1)
    turn_total = roll_dice(num_rolls, interactive_dice)
    print('Turn total:', turn_total)

def take_turn_interactive():
    """Interactively call take_turn."""
    num_rolls = get_int('Number of rolls: ', 0)
    opp_score = get_int('Opponent score: ', 0)
    turn_total = take_turn(num_rolls, opp_score, interactive_dice)
    print('Turn total:', turn_total)

def play_interactive():
    """Interactively call play."""
    strategy0 = make_interactive_strategy(0)
    strategy1 = make_interactive_strategy(1)
    score0, score1 = play(strategy0, strategy1)
    print('Final scores:', score0, 'to', score1)

@main
def run(*args):
    """Read in the command-line argument and calls corresponding functions.

    This function uses Python syntax/techniques not yet covered in this course.
    """
    import argparse
    parser = argparse.ArgumentParser(description="Play Hog")
    parser.add_argument('--interactive', '-i', type=str,
                        help='Run interactive tests for the specified question')
    parser.add_argument('--run_experiments', '-r', action='store_true',
                        help='Runs strategy experiments')
    args = parser.parse_args()

    if args.interactive:
        test = args.interactive + '_interactive'
        if test not in globals():
            print('To use the -i option, please choose one of these:')
            print('\troll_dice', '\ttake_turn', '\tplay', sep='\n')
            exit(1)
        try:
            globals()[test]()
        except (KeyboardInterrupt, EOFError):
            print('\nQuitting interactive test')
            exit(0)
    elif args.run_experiments:
        run_experiments()