import random
import math
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

from collections import defaultdict
import re

class LearningAgent(Agent):
    """ An agent that learns to drive in the Smartcab world.
        This is the object you will be modifying. """ 

    def __init__(self, env, learning=False, epsilon=1.0, alpha=0.5):
        super(LearningAgent, self).__init__(env)     # Set the agent in the evironment 
        self.planner = RoutePlanner(self.env, self)  # Create a route planner
        self.valid_actions = self.env.valid_actions  # The set of valid actions

        # Set parameters of the learning agent
        self.learning = learning # Whether the agent is expected to learn
        self.Q = dict()          # Create a Q-table which will be a dictionary of tuples
        
        self.epsilon = epsilon   # Random exploration factor
        self.alpha = alpha       # Learning factor
        #self.alpha = 1.0       # Learning factor

        ###########
        ## TO DO ##
        ###########
        # Set any additional class parameters as needed
        self.trial_number = 0
        self.epsilon_start = self.epsilon

    def reset(self, destination=None, testing=False):
        """ The reset function is called at the beginning of each trial.
            'testing' is set to True if testing trials are being used
            once training trials have completed. """

        # Select the destination as the new location to route to
        self.planner.route_to(destination)
        
        ########### 
        ## TO DO ##
        ###########
        # Update epsilon using a decay function of your choice
        # Update additional class parameters as needed
        # If 'testing' is True, set epsilon and alpha to 0
	
        ## Epsilon:
        # default learning:
        #self.epsilon = self.epsilon_start - (self.trial_number)*0.05
        # improved learning
        self.epsilon = 0.995**(self.trial_number + 1)
        
        ## Alpha:
        # improved learning
        self.alpha = 1 - (0.75/1400)*(self.trial_number)
        
        self.trial_number += 1
        if testing == True: 
            self.epsilon = 0
            self.alpha = 0
        else:
            print("\n === Epsilon is set to {} for trial {}===\n:".format(self.epsilon,self.trial_number))
        
        return None

    def build_state(self):
        """ The build_state function is called when the agent requests data from the 
            environment. The next waypoint, the intersection inputs, and the deadline 
            are all features available to the agent. """

        # Collect data about the environment
        waypoint = self.planner.next_waypoint() # The next waypoint 
        inputs = self.env.sense(self)           # Visual input - intersection light and traffic
        deadline = self.env.get_deadline(self)  # Remaining deadline

        ########### 
        ## TO DO ##
        ###########
        
        # NOTE : you are not allowed to engineer eatures outside of the inputs available.
        # Because the aim of this project is to teach Reinforcement Learning, we have placed 
        # constraints in order for you to learn how to adjust epsilon and alpha, and thus learn about the balance between exploration and exploitation.
        # With the hand-engineered features, this learning process gets entirely negated.
        

        # Set 'state' as a tuple of relevant data for the agent        
        #state = None
        state = ("waypoint_"+str(waypoint),)
        r = "light|oncoming|left"
        for i in inputs.keys():
            if re.match(r,i):
                val = str(i)+"_"+str(inputs[i])
                state += (val,)
        
        return state


    def get_maxQ(self, state):
        """ The get_max_Q function is called when the agent is asked to find the
            maximum Q-value of all actions based on the 'state' the smartcab is in. """

        ########### 
        ## TO DO ##
        ###########
        # Calculate the maximum Q-value of all actions for a given state

        maxQ = max(self.Q[state].values())
        if self.env.verbose:
       	    print("maxQ - new approach is {}".format(maxQ))
        
        return maxQ 


    def createQ(self, state):
        """ The createQ function is called when a state is generated by the agent. """

        ########### 
        ## TO DO ##
        ###########
        # When learning, check if the 'state' is not in the Q-table
        # If it is not, create a new dictionary for that state
        #   Then, for each action available, set the initial Q-value to 0.0

        if self.Q == {}:
        	self.Q = {}
        
        if state in self.Q.keys():
       	    #print("State {} already exists".format(state))
       	    temp = None
        else:
       	    #print("State {} doesnt exist. Creating new one".format(state))
       	    self.Q[state] = {}
       	    for action in self.valid_actions:
       	        #print("action is {}".format(action))
                self.Q[state][action] = 0.0	
        
        return


    def choose_action(self, state):
        """ The choose_action function is called when the agent is asked to choose
            which action to take, based on the 'state' the smartcab is in. """

        # Set the agent state and default action
        self.state = state
        self.next_waypoint = self.planner.next_waypoint()
        action = None

        ########### 
        ## TO DO ##
        ###########
        # When not learning, choose a random action
        # When learning, choose a random action with 'epsilon' probability
        # Otherwise, choose an action with the highest Q-value for the current state
        # Be sure that when choosing an action with highest Q-value that you randomly select between actions that "tie".
        #print("Choosing action in state: {}".format(state))
        if not self.learning:
            action = random.choice(self.valid_actions)
        else:
            if random.random() < self.epsilon:
                # Pick random action
                action = random.choice(self.valid_actions)
                if self.env.verbose:
                    print("Picking random action: {}".format(action))
            else:
                # Pick action with max Q value
                maxQ = self.get_maxQ(state)
                best_actions = []
                for act in self.valid_actions:
                     if self.Q[state][act] == maxQ:
                        best_actions.append(act)
                action = random.choice(best_actions)
                if self.env.verbose:
                    print("Picking best action - new approach: {}. Qvalue is {}".format(action, maxQ))
        
        return action
    
    
    def learn(self, state, action, reward):
        """ The learn function is called after the agent completes an action and
            receives a reward. This function does not consider future rewards 
            when conducting learning. """

        ########### 
        ## TO DO ##
        ###########
        # When learning, implement the value iteration update rule
        #   Use only the learning rate 'alpha' (do not use the discount factor 'gamma')
        if self.learning:
            if self.env.verbose:
                print("In learning:\n\t state is {}".format(state))
            self.Q[state][action] = (1.0 - self.alpha) * self.Q[state][action] + self.alpha * (reward) 

        return


    def update(self):
        """ The update function is called when a time step is completed in the 
            environment for a given trial. This function will build the agent
            state, choose an action, receive a reward, and learn if enabled. """
	
        if self.env.verbose:
            print("State at beginining of update is:\n\t{}".format(self.state))
        state = self.build_state()          # Get current state
        if self.env.verbose:
        	print("New state is:\n\t{}".format(state))
        self.createQ(state)                 # Create 'state' in Q-table
        action = self.choose_action(state)  # Choose an action
        reward = self.env.act(self, action) # Receive a reward
        self.learn(state, action, reward)   # Q-learn

    	#print("\nNumber of states in Q after time {} is: {}".format(self.env.t, len(self.Q)))
    	cnt = 0
    	for key in self.Q.keys():
    		for act in self.valid_actions:
    			if self.Q[key][act] != 0.0:
    				cnt += 1
    	print("Number of states in Q after time {} is: {}. Number of non zero Q values (i.e. approx states explored) is: {}\n".format(self.env.t, len(self.Q), cnt))
    
        return
        
    def get_best_action(self, state, silent = False):
	""" New function defined by sbujimal """
       
        maxQ = self.get_maxQ(state)
        best_actions = []
        for act in self.valid_actions:
             if self.Q[state][act] == maxQ:
                best_actions.append(act)
        bestaction = random.choice(best_actions)       
 
        return maxQ,bestaction
        
def run():
    """ Driving function for running the simulation. 
        Press ESC to close the simulation, or [SPACE] to pause the simulation. """

    ##############
    # Create the environment
    # Flags:
    #   verbose     - set to True to display additional output from the simulation
    #   num_dummies - discrete number of dummy agents in the environment, default is 100
    #   grid_size   - discrete number of intersections (columns, rows), default is (8, 6)
    env = Environment()
    #env = Environment(verbose = True)
    #env = Environment(verbose = True, num_dummies = 10, grid_size = (5, 5))
    
    ##############
    # Create the driving agent
    # Flags:
    #   learning   - set to True to force the driving agent to use Q-learning
    #    * epsilon - continuous value for the exploration factor, default is 1
    #    * alpha   - continuous value for the learning rate, default is 0.5
    #agent = env.create_agent(LearningAgent)
    agent = env.create_agent(LearningAgent, learning = True)
    
    ##############
    # Follow the driving agent
    # Flags:
    #   enforce_deadline - set to True to enforce a deadline metric
    #env.set_primary_agent(agent)
    env.set_primary_agent(agent, enforce_deadline = True)

    ##############
    # Create the simulation
    # Flags:
    #   update_delay - continuous time (in seconds) between actions, default is 2.0 seconds
    #   display      - set to False to disable the GUI if PyGame is enabled
    #   log_metrics  - set to True to log trial and simulation results to /logs
    #   optimized    - set to True to change the default log file name
    #sim = Simulator(env)
    # default learning
    #sim = Simulator(env, update_delay = 0.0001, log_metrics = True, display = False)
    # improved learning
    sim = Simulator(env, update_delay = 0.0001, log_metrics = True, display = False, optimized = True)
    
    ##############
    # Run the simulator
    # Flags:
    #   tolerance  - epsilon tolerance before beginning testing, default is 0.05 
    #   n_test     - discrete number of testing trials to perform, default is 0
    #sim.run()
    # default learning
    #sim.run(n_test = 10)
    # improved learning:
    sim.run(n_test = 100, tolerance = 0.001)

    # sbujimal added:
    print("\nQ value is:")
    for key,val in agent.Q.items():
    	print("\tstate:" + str(key))
    	print("\t\taction,value:" + str(val))
	maxQ,action = agent.get_best_action(key, silent = True)
	print("\t\tBest action for this state is: {}. Qvalue is {}".format(action, maxQ))
    print("\n")
    print("\nNumber of states in Q is: {}".format(len(agent.Q)))
    cnt = 0
    for key in agent.Q.keys():
    	for act in agent.valid_actions:
    		if agent.Q[key][act] != 0.0:
    			cnt += 1
    print("Number of non zero Q values (i.e. approx states explored) is: {}\n".format(cnt))


if __name__ == '__main__':
    run()
