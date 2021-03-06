
##  State changes 


Execution of an OpenMAX component is driven by a state-transition model.
A component will start in the `Loaded`state, transition to the `Idle`state and then to the `Executing`state.
At least, that is the idea. In practice, the state transitions will
only occur for a component when conditions are _exactly_ right for that component.


The hardest transition to get right is from `Loaded`to `Idle`. Any _enabled_ component has ports which have to be set up
and if that is not done exactly right then nothing will happen.
Being _exactly right_ means that all of the
resources such as buffers have to be allocated and configured _correctly_ , which is often not so easy.
So most programmers seem to default to _disabling_ all of a component's ports at the beginning in order that this
transition will occur, and then try enabling them afterwards.
[The dramatic over-emphasis in this section is the result of
bitter experience, both by myself and - I am sure - all of
the other OpenMAX programmers!]
