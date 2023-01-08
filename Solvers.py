from tabnanny import verbose
from map_data import *

from shutil import get_terminal_size
from random import choice, randrange


terminal_width, _ = get_terminal_size()

_visualizers = {}

def _default_visualizer(_, state):
    '''Generic visualizer for unknown problems.'''
    print(state)

class Visualizer:
    '''Visualization and printing functionality encapsulation.'''

    def __init__(self, problem):
        '''Constructor with the problem to visualize.'''
        self.problem = problem
        self.counter = 0
    
    def visualize(self, frontier):
        '''Visualizes the frontier at every step.'''
        self.counter += 1
        print(f'Frontier at step {self.counter}')
        for state in frontier:
            print()
            _visualizers.get(type(self.problem), _default_visualizer)(self.problem, state)
        print('-' * terminal_width)

def _robot_visualizer(env, state):
    '''Custom visualizer for Tom and Jerry.'''
    robot = env.state[:2]
    crates = [ building_to_position[bl] for bl in state[3 :] if bl > 0]
    for j in range(env.bounds[1] - 1, -1, -1):
        for i in range(env.bounds[0]):
            if (i , j) ==  robot :
                print('🤖' , end='')
            elif (i ,j) in crates :
                print('📦' , end = '')
            else :
                print('⬜',end = '') 
        print()

class Environment:
    '''
    Abstract base class for an (interactive) environment formulation.
    It declares the expected methods to be used to solve it.
    All the methods declared are just placeholders that throw errors if not overriden by child "concrete" classes!
    '''
    
    def __init__(self):
        '''Constructor that initializes the problem. Typically used to setup the initial state.'''
        self.state = None
    
    def actions(self):
        '''Returns an iterable with the applicable actions to the current environment state.'''
        raise NotImplementedError
    
    def apply(self, action):
        '''Applies the action to the current state of the environment and returns the new state from applying the given action to the current environment state; not necessarily deterministic.'''
        raise NotImplementedError
    
    @classmethod
    def new_random_instance(cls):
        '''Factory method to a problem instance with a random initial state.'''
        raise NotImplementedError

def action_from_q(env, q, verbose=True):
    '''Get the best action for the current state of the environment from Q-values'''
    return max((action for action in env.actions()), key=lambda action: q.get((env.state, action), 0))

def q_learning(env, q ={}, n ={}, f=lambda q, n: (q+1)/(n+1), alpha=lambda n: 60/(n+59), error=1e-6, verbose=False , states_target = None):
    '''Q-learning implementation that trains on an environment till no more actions can be taken'''
    if verbose: visualizer = Visualizer(env)
    if states_target : states = []
    while env.state is not None:
        if verbose: visualizer.visualize([env.state])
        state = env.state
        if states_target : states.append(state)
        action = max(env.actions(),
                     key=lambda next_action: f(q.get((state, next_action), 0), n.get((state, next_action), 0)))
        n[(state, action)] = n.get((state, action), 0) + 1
        reward = env.apply(action)
        q[(state, action)] = q.get((state, action), 0) \
                           + alpha(n[state, action]) \
                           * (reward
                              + env.discount * max((q.get((env.state, next_action), 0) for next_action in env.actions()), default=0)
                              - q.get((state, action), 0))
    
    if states_target :
        states_target.give_me_my_states(states , env)

    return q, n

from math import inf
from time import time
from itertools import count

def simulate(env_ctor, n_iterations=inf, duration=inf, **q_learning_params):
    '''A helper function to train for a fixed number of iterations or fixed time'''
    for param in ('q', 'n'): q_learning_params[param] = q_learning_params.get(param, {})
    start_time = time()
    i = count()
    s = time()
    idx = 0
    while time() < start_time + duration and next(i) < n_iterations:
        env = env_ctor()
        q, n = q_learning(env, **q_learning_params)
        print(f'Iteration {idx}'); idx+=1;
    print("duration: ", time() - s)
    return q_learning_params['q'], q_learning_params['n']




class DeliveryRobot(Environment):
    
    def __init__(self, start_pos : tuple , crates_pickup_locations : tuple , crates_dropoff_locations : tuple
     , max_reward, discount):
        """ The constructor for the delivery bot env

        Building integer encoding :
            OSS --> 1
            AB  --> 2
            NB  --> 3
            HB  --> 4
            NONE --> 0

        Args:
            start_pos (tuple): (x ,y) the start location of the robt
            crates_pickup_locations (tuple): a tuple containing crates pick up locations  ex ( 3,3,3,3 , 4,4,4,4 )
            crates_dropoff_locations (tuple): a tuple containing crates drop off locations  ex (1,2,2,1,1,1,2,1 )
            max_reward (float): _description_
            discount (float): _description_
        """     
        x , y , pickup_locations , dropoff_locations = start_pos[0] , start_pos[1] , crates_pickup_locations , crates_dropoff_locations;
        currently_holding = (0 ,)
        self.state = (x , y) + currently_holding +  pickup_locations 
        #print( f'Current state : {self.state}')
        
        self.dropoff_locations = dropoff_locations

        self.bounds = (14,14)
        self.max_reward = max_reward
        self.discount = discount
        self.start_pos = start_pos
    
    def decode_state(self, state) :
        x = state[0]
        y = state[1]
        currently_holding = state[2]
        pickup_locations = state[3 :]
        return (x , y) , currently_holding , pickup_locations


    def actions(self):

        if self.state is None: return []

        pos ,currently_holding ,  pickup_locations = self.decode_state(self.state)
        current_building = position_to_building.get(pos , -1)
        # print(f'Currently holding {currently_holding}')
        # print(f'Current state {self.state}')

        if not   currently_holding and  all (not pick_up for pick_up in pickup_locations) : return ['Finish']

        if not currently_holding and current_building != -1  and current_building in pickup_locations  : 
            return ['Pickup'] 
            
        if currently_holding and  self.dropoff_locations[currently_holding -1] == current_building  : 
            return ['Dropoff'] 

        return ['up', 'down', 'left', 'right']
    
    def apply(self, action):
        # print(f'Action is {action}')
        # print(f'Current state is {self.state}')

        up = lambda position: (position[0], min(position[1] + 1, self.bounds[1] - 1))
        down = lambda position: (position[0], max(position[1] - 1, 0))
        left = lambda position: (max(position[0] - 1, 0), position[1])
        right = lambda position: (min(position[0] + 1, self.bounds[0] - 1), position[1])

        pos ,currently_holding ,  pickup_locations = self.decode_state(self.state)
        current_building = position_to_building.get(pos , -1)

        if action == 'up': 
            self.state = ( up(pos)+ (currently_holding , )+ pickup_locations ) 
            return -0.2 * self.max_reward
        if action == 'down': 
            self.state = ( down(pos) + (currently_holding , )+  pickup_locations ) 
            return -0.2 * self.max_reward
        if action == 'left': 
            self.state =  (left(pos) + (currently_holding , )+  pickup_locations ) 
            return -0.2 * self.max_reward
        if action == 'right': 
            self.state =  ( right(pos) + (currently_holding , )+  pickup_locations )
            return -0.2 * self.max_reward
        
        elif action == 'Pickup': 
            crate_idx = pickup_locations.index(current_building) 
            temp = list(pickup_locations)
            temp[crate_idx ] = 0 ; # Mark crate as taken 
            pickup_locations = tuple(temp)

            currently_holding = crate_idx +1
            self.state = pos + (currently_holding ,)  +  pickup_locations

            return 0.4 * self.max_reward
        
        elif action == 'Dropoff':             
            currently_holding = 0 

            self.state = self.start_pos + (currently_holding ,) +  pickup_locations

            return 0.4 * self.max_reward
            
        elif action == 'Finish': self.state = None; return +self.max_reward

    
def generate_env() :
    pick_ups = ( 3,3,3,3 , 4,4,4,4 )
    drop_offs = (1,2,2,1,1,1,2,1 )
    start_pos = (7 , 1)
    return DeliveryRobot(crates_dropoff_locations= drop_offs ,crates_pickup_locations= pick_ups ,
    start_pos= start_pos ,discount= 0.1 ,max_reward= 100   ) 

_visualizers[DeliveryRobot] = _robot_visualizer



class ai_master :

    def give_me_my_states(self, states , env) : 
        self.states = states;
        self.env = env

    def start(self , iterations = 250  ) :
        q, n = {}, {}
        # simulate(lambda: DeliveryRobot.new_random_instance((14, 14), 100, 0.1), duration=60, q=q, n=n)
        simulate(generate_env , n_iterations=iterations, q=q, n=n, verbose=False ,f=lambda q, n: 1/(n+1))
        simulate(generate_env , n_iterations=1, q=q, n=n, verbose=False ,f=lambda q, n: q , states_target = self  )
        #print(q)
        