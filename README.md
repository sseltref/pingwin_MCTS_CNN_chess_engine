# piNgwiN - Monte Carlo Tree Search and Convolutional Neural Networks based chess engine 
This is an early version of my chess engine. You can play it in terminal by running pingwin.py.  
Engine settings parameters description:  
exploration_constant --- exploration value of MCTS,  
bias_constant --- tells engine how much to bias the moves based on CNNs outputs vs MCST values,  
killer_rate --- the ratio between average MCTS score and minmax score --- set between 0 and 1,  
simulation_depth --- Markov Chain Monte Carlo simulation depth, very computationally complex, best set to 0,  
bias_neural_network --- agile, standard, heavy --- tells engine which CNN move bias models to use,  
position_eval_neural_network --- agile, standard, heavy --- tells engine which CNN position evaluation models to use.  
    
Moves are passed in UCI notation.

# pingwin on lichess - lichess.org/@/pingwin_siepacz
