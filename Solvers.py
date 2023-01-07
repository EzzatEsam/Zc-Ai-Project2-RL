from shutil import get_terminal_size
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
    for j in range(env.bounds[1] - 1, -1, -1):
        for i in range(env.bounds[0]):
            print('🤖' if (np.array([i, j]) & robot).all()  else '⬜', end='')
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

def q_learning(env, q={}, n={}, f=lambda q, n: (q+1)/(n+1), alpha=lambda n: 60/(n+59), error=1e-6, verbose=False):
    '''Q-learning implementation that trains on an environment till no more actions can be taken'''
    if verbose: visualizer = Visualizer(env)
    while env.state is not None:
        if verbose: visualizer.visualize([env.state])
        state = env.state
        action = max(env.actions(),
                     key=lambda next_action: f(q.get((state, next_action), 0), n.get((state, next_action), 0)))
        n[(state, action)] = n.get((state, action), 0) + 1
        reward = env.apply(action)
        q[(state, action)] = q.get((state, action), 0) \
                           + alpha(n[state, action]) \
                           * (reward
                              + env.discount * max((q.get((env.state, next_action), 0) for next_action in env.actions()), default=0)
                              - q.get((state, action), 0))
    print(state)
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
    while time() < start_time + duration and next(i) < n_iterations:
        env = env_ctor()
        q, n = q_learning(env, **q_learning_params)
    print("duration: ", time() - s)
    return q_learning_params['q'], q_learning_params['n']

from random import choice, randrange
import numpy as np

class DeliveryRobot(Environment):
    
    def __init__(self, x: int, y: int, current_holding: int, list_remaining_crates: list, bounds, max_reward, discount):
        self.state = (x, y, current_holding, list_remaining_crates)
        
        self.pickup_locations = [[1, 2], [8, 6]]
        self.dropoff_locations = [[2, 9], [5, 5]]

        self.bounds = bounds
        self.max_reward = max_reward
        self.discount = discount
    
    def actions(self):
        if self.state is None: return []
        if not bool(self.state[-1]) and self.state[2] == 0: return ['Finish']

        if list(self.state[:2]) in self.pickup_locations and self.state[2] == 0: return ['Pickup'] 
        if list(self.state[:2]) in self.dropoff_locations and self.state[2] != 0: return ['Dropoff'] 

        return ['up', 'down', 'left', 'right']
    
    def apply(self, action):
        up = lambda position: (position[0], min(position[1] + 1, self.bounds[1] - 1))
        down = lambda position: (position[0], max(position[1] - 1, 0))
        left = lambda position: (max(position[0] - 1, 0), position[1])
        right = lambda position: (min(position[0] + 1, self.bounds[0] - 1), position[1])

        if action == 'up': 
            up(self.state[:2])
            if self.state[2] == 0: return -0.2 * self.max_reward
        if action == 'down': 
            down(self.state[:2])
            if self.state[2] == 0: return -0.2 * self.max_reward
        if action == 'left': 
            left(self.state[:2])
            if self.state[2] == 0: return -0.2 * self.max_reward
        if action == 'right': 
            right(self.state[:2])
            if self.state[2] == 0: return -0.2 * self.max_reward
        
        elif action == 'Pickup': 
            temp = list(self.state)
            temp[2] = temp[-1].pop()
            self.state = tuple(temp)
            return 0.4 * self.max_reward
        
        elif action == 'Dropoff': 
            self.state[2] = 0
            self.state[:2] = (0, 0)
            return 0  
        
        elif action == 'Finish': self.state = None; return +self.max_reward

    @classmethod
    def new_random_instance(cls, bounds, max_reward, discount):
        x, y = randrange(bounds[0]), randrange(bounds[1])
        return cls(x, y, 0, tuple([i for i in range(1, 9)]), bounds = bounds, max_reward = max_reward, discount = discount)


_visualizers[DeliveryRobot] = _robot_visualizer

q, n = {}, {}
# simulate(lambda: DeliveryRobot.new_random_instance((14, 14), 100, 0.1), duration=60, q=q, n=n)
simulate(lambda: DeliveryRobot.new_random_instance((14, 14), 100, 0.1), n_iterations=5, q=q, n=n, verbose=False)
print(q)