import time
import numpy
import pyglet
from pyglet import *
from pyglet.gl import *
import pyglet.gl as GL
import ctypes
import sys


#movint to 2d construct
#box
def pr(string):
    print(string, end="")

class box: #these settings control the pattern. Most settings will result in boring looping patterns
    def __init__(self, number): #good settings in comment
        self.value = 0
        self.number = number 
        self.dt = 0.10 #.10 timestep (in s) adjusting down increases wave failure
        self.friends = []
        self.decay = self.dt/3 #dt/3  #dt/9 decay rate
        self.boost = 0.04 #0.04
        self.excite = 0.22 #.22 excited firing threshold raising reduces chain reaction increases wave loss
        self.falling = True
        self.last = 1
        self.fired = False
        self.frequency = 0.11 #0.11 #target firing frequency in fires/sec
        self.movingAverage = 1
        self.fatigue = 0 #value of fatigue

    def blink(self):
        return self.value


    def set(self, value):
        self.value = value

    def get(self):
        return self.value

    def share(self): #spread value to friends
        for friend in self.friends: #for each of the "friend" connections
            friend.set(friend.get() + self.dt*(self.value/len(self.friends))) #add dt fraction of current energy to friends
        self.value -= self.value*self.dt #so energy is conserved, subtract from self
    
    def eval(self):
        #fire due to low value
        if(self.value < self.boost): #If value less than boost value
            self.fire() #fire
        else:
            self.value -= self.decay*self.value #else apply decay multiplier

        #fire due to excitement
        if(self.last > self.value): #if the current value less than last value
            self.falling = True #we are falling
        else: #if we are not falling
            if(self.value > (self.excite + self.fatigue)): #if we are above the excite threshold, modified by fatigue
                self.fire() #fire
        self.last = self.value #record the last value

        #calculate exertion
        return self.exertion()

    def fire(self):
        #conditions have been met
        if(not self.fired):
            self.value = 1
            self.fired = True

    def exertion(self):
        #fatigue function to insure variation of the pattern
        #dependent on DT
        #we calculate the actual trailing frequency, and adjust fatigue
        if(self.fired):
            self.movingAverage += 1
            self.fired = False
        else:
            self.movingAverage = self.movingAverage*(1-(self.dt*self.frequency))
        #now set the fatigue compensator
        #when average is less than 1, we're good 
        if(self.movingAverage < 1):
            self.fatigue = 0
        else: #we assume that it ranges ~ 2.0 to 1.0
            self.fatigue = (self.movingAverage - 1)*(1 - self.excite)
        return self.fatigue

      







#Pyglet gfx
size = 6

batch = graphics.Batch()

divy = int(216/size) #108/3
divx = int(384/size) #192/3


window = pyglet.window.Window(divx*10,divy*10)
window.set_fullscreen()

hy = int(window.height/divy)
hx = int(window.width/divx)

points = []

#Create the rectangles (old way)
for y in range(divy):
    points.append([])
    for x in range(divx):
        points[y].append(shapes.Rectangle(x=x*hx,y=y*hy,height=hy,width=hx,color=(0,0,0),batch=batch))



###########################################
#create the simulation
#now using 2d
#
#  (0,0) ==> +i
#      ||
#      \/ +j
#

boxes = []
for j in range(divy):
    boxes.append([])
    for i in range(divx):
        boxes[j].append(box(i))

for j in range(len(boxes)):
    for i in range(len(boxes[j])):
        #side and corner boundaries
        if(i == 0): #left side boundary
            if(j==0):
                #top left hand corner
                boxes[j][i].friends.append(boxes[j][len(boxes[j])-1]) # left position (special)
                boxes[j][i].friends.append(boxes[j][i+1]) # right position (ok)
                boxes[j][i].friends.append(boxes[j+1][i]) # bottom position (ok)
                boxes[j][i].friends.append(boxes[len(boxes)-1][i]) # top position (special)
            elif(j==(len(boxes)-1)):
                #bottom left hand corner
                boxes[j][i].friends.append(boxes[j][len(boxes[j])-1]) # left position (special)
                boxes[j][i].friends.append(boxes[j][i+1]) # right position (ok)
                boxes[j][i].friends.append(boxes[0][i]) # bottom position (special)
                boxes[j][i].friends.append(boxes[j-1][i]) # top position (ok)
            else:
                #left side boundary
                boxes[j][i].friends.append(boxes[j][len(boxes[j])-1]) # left position (special)
                boxes[j][i].friends.append(boxes[j][i+1]) # right position (ok)
                boxes[j][i].friends.append(boxes[j+1][i]) # bottom position (ok)
                boxes[j][i].friends.append(boxes[j-1][i]) # top position (ok)
        elif(i == (len(boxes[j])-1)): #right side boundary
            if(j==0):
                #top right hand corner
                boxes[j][i].friends.append(boxes[j][i-1]) # left position (ok)
                boxes[j][i].friends.append(boxes[j][0]) # right position (special)
                boxes[j][i].friends.append(boxes[j+1][i]) # bottom position (ok)
                boxes[j][i].friends.append(boxes[len(boxes)-1][i]) # top position (special)
            elif(j==(len(boxes)-1)):
                #bottom right hand corner
                boxes[j][i].friends.append(boxes[j][i-1]) # left position (ok)
                boxes[j][i].friends.append(boxes[j][0]) # right position (special)
                boxes[j][i].friends.append(boxes[0][i]) # bottom position (special)
                boxes[j][i].friends.append(boxes[j-1][i]) # top position (ok) 
            else:
                #right side boundary
                boxes[j][i].friends.append(boxes[j][i-1]) # left position (ok)
                boxes[j][i].friends.append(boxes[j][0]) # right position (special)
                boxes[j][i].friends.append(boxes[j+1][i]) # bottom position (ok)
                boxes[j][i].friends.append(boxes[j-1][i]) # top position (ok) 

        #top and bottom boundaries
        elif(j==0): # we've already done the corners
                #top side boundary
                boxes[j][i].friends.append(boxes[j][i-1]) # left position (ok)
                boxes[j][i].friends.append(boxes[j][i+1]) # right position (ok)
                boxes[j][i].friends.append(boxes[j+1][i]) # bottom position (ok)
                boxes[j][i].friends.append(boxes[len(boxes)-1][i]) # top position (special)
        elif(j==(len(boxes)-1)):
                #bottom side boundary
                boxes[j][i].friends.append(boxes[j][i-1]) # left position (ok)
                boxes[j][i].friends.append(boxes[j][i+1]) # right position (ok)
                boxes[j][i].friends.append(boxes[0][i]) # bottom position (special)
                boxes[j][i].friends.append(boxes[j-1][i]) # top position (ok)

        else: #default case
            boxes[j][i].friends.append(boxes[j][i-1])
            boxes[j][i].friends.append(boxes[j][i+1])
            boxes[j][i].friends.append(boxes[j+1][i])
            boxes[j][i].friends.append(boxes[j-1][i])


#set initial conditions
for j in range(len(boxes)):
    for i in range(len(boxes[j])):
        boxes[j][i].set(0.4)
boxes[int(len(boxes)/2)][int(len(boxes[0])/2)].set(1.0)


depth = 0
deltaDepth = 1

def update(dt):
    if(True):
        #Update the 2d grid of boxes
        for j in range(len(boxes)):
            for i in range(len(boxes[j])):
                #run simulation
                boxes[j][i].share()
                
        for j in range(len(boxes)):
            for i in range(len(boxes[j])):
                #yes we are sharing twice per timestep, an accidental discovery
                boxes[j][i].share() 
                #eval function
                ret = boxes[j][i].eval()
                #get results
                value = boxes[j][i].blink()

                #scale colors
                R=int(255*(ret)**(1))
                B=int(255*(value)**(1)) 
                G=int(255*(value)**(2)) 




        
                if(R > 255):
                    R = 255
                if(G > 255):
                    G = 255
                if(B > 255):
                    B = 255        

                points[j][i].color=(R,G,B)

        window.clear()
        batch.draw()
    else:
        #modify image pixels
        pass








@window.event
def onKeyPress(symbol, modifiers):
    if(symbol == pyglet.window.key.ESCAPE):
        window.close()
        pyglet.app.event_loop.exit()
        pyglet.app.exit()
        exit()

#interactive mouse
@window.event
def on_mouse_drag(x,y,dx,dy,buttons,modifiers):
    if(buttons & pyglet.window.mouse.LEFT):
        #determine which square we are in using x and y
        global divy
        global divx

        i = int(x/hx) #find which square we're in
        j = int(y/hy)

        #fire the square
        boxes[j][i].fire() 
@window.event
def on_mouse_press(x,y,button,modifiers):
    if(button == pyglet.window.mouse.LEFT):
        #determine which square we are in using x and y
        global divy
        global divx

        i = int(x/hx) #find which square we're in
        j = int(y/hy)

        #fire the square
        boxes[j][i].fire() 




#schedule updates
pyglet.clock.schedule_interval(update,(1/60))

pyglet.app.run() #this is the application loop




    

    
            
