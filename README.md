# OOP_Ex1
Assignment 1:  

Noah Weiss 326876786  
Rashi Pachino 345174478    

Sources from Assignment 0 that are still relevant to Assignment 1:  
  https://trace.tennessee.edu/cgi/viewcontent.cgi?article=3380&context=utk_chanhonoproj  
  https://web.eecs.umich.edu/~baveja/RLMasses/node2.html  
  https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=9003300  
  
The explanation for the elevator problem is also the same as Assignment 0.  

  The conventional elevator allows the passenger to choose a direction of travel while still outside the elevator, and only once inside the elevator, the passenger chooses his/her desired floor. The elevator will continue only in the chosen direction, and pick up passengers along the way, if the passenger is traveling in the same direction. When multiple elevators work together, the algorithm becomes more intricate. While this design works, it is not optimal. Picking up passengers along the way elongates a passenger’s wait time inside the elevator. In addition, conventional elevators can end up working heal to heal instead of grouping floors together to specific elevators, causing an unnecessary increase in power. The smart elevator design allows the passenger to choose a floor before entering the elevator and directs the passenger to an assigned elevator car. This design is said to lessen the passenger wait time as well as the time spent inside the elevator.  

In this assignment we will formulate an offline algorithm for the smart elevator to maximize reward and minimize costs.  

The Offline Algorithm:  
  The offline algorithm receives the list of calls (including call name, time, source, destination and status of the elevator) ahead of time 
  and must allocate an elevator to each call at the beginning, not in real time. This allows for a more intricate algorithm, 
  as we do not know the position of the elevator at any given time. Therefore, our algorithm acts as follows:  

Our Algorithm:  
  All calls are kept in a dictionary. The key beginning the ID of the elevator, and the value being a list of dictionaries, in which the key is an int representing the next floor in the elevator's job list, and the value being the call itself.  
  This way, similarly, to the previous assignment, each elevator will have a list of floors to visit, however, this time we have access to the call associated with the floor as well.  
  
  Since we do not already know the position of the elevator at any given time, we wrote a function called pos_at_time which receives an elevator, 
  its call list and a time and mathematically calculates on which floor the elevator will be sitting at that specific time. 
  This function uses the elevator's details (speed, start time, stop time, close time, open time). 
  We created another function called future_call_list which also receives an elevator, its call list, and a time, 
  and returns what the elevator's call bank will look like at the given time. 
  
  time_to_complete_call is a function we wrote that receives a call, and returns how long it would take an elevator to complete the call.
  
  fastest_elev uses this function to determine which elevator would give the minimal wait time for a call.
  
  After creating these functions, we now have access to the position of an elevator at any time, what its job list looks like at the time
  and which elevevator would complete the job the fastest.  
  
  Therefore, the algorithm can iterate through the list of jobs and add each floor based on the elevator algorithm given in the instructions of the Assignment and based on the online algorithm we wrote for the previous assignment. 
