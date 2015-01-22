"""

Refresh the webpage if the music is not working in the 
"START" and "TUTORIAL" modes!

STICKMAN GYMNASTICS

Controls:

"left arrow" : faces stickman to the left, hold to run
"right arrow" : faces stickman to the right, hold to run
"w" : long position, for handstands
"e" : arched position 
"r" : hollow position
"t" : tucks stickman into a ball, speeding up his rotation
"space" " : when on the ground, causes stickman to jump

Skills:
    DISCLAIMER: this game is challenging, 
    but these skills can all be performed
    consistently with practice.
    
    frontflip: hold r, release r, press space, hold t
    backflip: hold e,immediately press space, 
              immediately press and hold t
    back-handsprings: hold e, immediately press space.
                      repeat each time on hands and feet
    
    

Future Improvements:
   Add interactivity
"""

import simplegui
import math
import random
     
### GLOBAL VARS ###
image = simplegui.load_image("https://dl.dropboxusercontent.com/s/xk0d8ljhq0jzbdf/danish-mens-gymnastics-team.jpg?token_hash=AAHyBZfuy_ZYfzBB-hG9O9WNrB722G5F7jAesVyGJraFBg")

epic = simplegui.load_sound('https://www.dropbox.com/s/05vefa8s3yc6owb/Transformers.mp3?dl=1')
pain = simplegui.load_sound('https://www.dropbox.com/s/w6jvudujm3sgc1v/pain.mp3?dl=1')
pain.set_volume(.1)
transformers = simplegui.load_sound('https://www.dropbox.com/s/qb14lqma69seagr/ArurianDance.mp3?dl=1')
epic.set_volume(1)
transformers.set_volume(1)

epic_timer = 0
transformer_timer = 0


counter = 0

lives_before_super_jump = 50
level = 1
lives = 3
level_count = 0
angle_pre_jump = 0
angle_post_jump = 0

TITLE_SCREEN = True
HOW_TO_PLAY = False
HIGH_SCORES = False
TUTORIAL = False

DID_SUPER_JUMP = False

high_scores = []

WIDTH = 800
HEIGHT = 600
xo = 300 	# initial neck_base[0]
h = 450	# initial neck_base[1]
rad = math.pi/180 
g = [0,5] # gravitational acceleration constant vector
head_weight = 80 # weight of stick man's head
dt = .2

score = 0
time_left = 30

limb_list = [] # list of stick figure limbs
limb_angles = [-30*rad,-45*rad,20*rad,10*rad,45*rad,3*rad,10*rad,-25*rad,-5*rad] # list of stick figure limb angles with the downward vertical (given angle about cm = 0)
limb_lengths = [36,22,22,18,18,24,24,30,30]  # limb lengths

center_of_mass = [0,0] # center of mass

max_rotational_momentum = 80000

fulcrum_index = 50
vel = [0,0] # linear velocity of center of mass
accel = [0,0] # angular velocity of center of mass
tot_mass = sum(limb_lengths)
cm_angle = 0*rad  # angle to rotate rigid man around cm by
fulcrum_angle = 0*rad # change to angle_base
rotational_momentum = 0
moment_of_inertia = 0 # stick man's moment about his center_of_mass
angular_momentum = 0 #keep track of angular momentum
torque = 0
net_body_change = 0 # sum of displacements from conform_rigid_man

artificial_momentum = 0

pos_list = [] # positions of bases on ground
ground = HEIGHT- 20
fulcrum = [0, ground]
low = ground
pos_before_jump = fulcrum

neck_base = [xo,h]	# keep track of neck position as base point for limb positions given limb_angles, neglecting relation to center of mass

make_limb_list_neck = [xo,h]

PLANTED = False


IN_GAME = False

# body positions
STANDING = 0
ARCHED = 1
HOLLOW = 2
TUCKED = 3
LONG = 4
RUNNING = 5

RUN = False
stride_period = 30
run_time = 0 # change run position when run_time exceeds half of stride period
init_vel = [0,0] # vel for jump just after running

STATE_VECTOR = [True, False, False, False, False, False]



CHANGED_BODY = False # changed body position

# status
ON_GROUND = False
RESTING = False

# action flags
JUMP = False

# direction
RIGHT = True
PREV_RIGHT = True

JUMPED = False
direction = RIGHT

### FUNCTION DEFINITIONS ###
def get_dist(vector1,vector2):
    return math.sqrt((vector1[0] - vector2[0])**2 + (vector1[1] - vector2[1])**2)

def angle_to_vector(angle):
    return [math.sin(angle),math.cos(angle)] #angle is from downwards vertical

def vector_to_angle(vector):
    if get_dist(vector,[0,0]) < .000001:
        return 0
    ang = math.asin(vector[1]/get_dist(vector,[0,0])) # angle is from downwards vertical
    if vector[0] >=0:
        ang = 90*rad - ang
    else:
        ang = -90*rad - ang
    if ang < 0:
        ang = -180*rad - ang
    return ang

def get_center_of_mass(limb_list):
    """return center of mass"""
    global limb_lengths #weights
    global limb_angles
    #global head_weight, neck_base
    
    x_centers = []
    y_centers = []
    xcm = 0
    ycm = 0
    
    for limb in limb_list:
        x_centers.append((limb.get_pos1()[0] + limb.get_pos2()[0]) * .5)
        y_centers.append((limb.get_pos1()[1] + limb.get_pos2()[1]) * .5)
        
    # add head weight 
    neck_base = limb_list[0].get_pos1()
    head_pos = [neck_base[0] + 10*angle_to_vector(limb_angles[0])[0], neck_base[1] - 10*angle_to_vector(limb_angles[0])[1]]    
    
    tot_weight = sum(limb_lengths) + head_weight
    
    for i in xrange(len(x_centers)):
        xcm += (x_centers[i]*limb_lengths[i])/tot_weight
        ycm += (y_centers[i]*limb_lengths[i])/tot_weight
    
    xcm += head_pos[0]*head_weight/tot_weight
    ycm += head_pos[1]*head_weight/tot_weight
    return [xcm,ycm]

def conform_rigid_man():
    """
    accelerate limb angles towards rigid man configuration
    Updates limb positions
    """
    global limb_angles, RIGHT, PREV_RIGHT, STATE_VECTOR, run_time, stride_period
    
    net_change = 0
    
    
    if RIGHT:
        if STATE_VECTOR[STANDING]:
            new_limb_angles = [-30*rad,-45*rad,20*rad,10*rad,45*rad,3*rad,10*rad,-25*rad,-5*rad]        
        elif STATE_VECTOR[ARCHED]:
            new_limb_angles = [10*rad,210*rad,230*rad,190*rad,220*rad,10*rad,50*rad,35*rad,45*rad]
        elif STATE_VECTOR[HOLLOW]:
            new_limb_angles = [0*rad,160*rad,110*rad,170*rad,150*rad,-20*rad,30*rad,-30*rad,-35*rad]
        elif STATE_VECTOR[TUCKED]:
            new_limb_angles = [-30*rad,-40*rad,-25*rad,35*rad,45*rad,105*rad,120*rad,-20*rad,-30*rad] 
        elif STATE_VECTOR[RUNNING]:
            if run_time < stride_period/2:
                new_limb_angles = [0*rad,-35*rad,40*rad,45*rad,110*rad,-40*rad,80*rad,-60*rad,35*rad] 
            else:    
                new_limb_angles = [0*rad,40*rad,-35*rad,110*rad,45*rad,80*rad,-40*rad,35*rad,-100*rad] 
    else:
        if STATE_VECTOR[STANDING]:
            new_limb_angles = [30*rad,45*rad,-20*rad,-10*rad,-45*rad,-3*rad,-10*rad,25*rad,5*rad] 
        if STATE_VECTOR[ARCHED]:
            new_limb_angles = [-10*rad,-210*rad,-230*rad,-190*rad,-220*rad,-10*rad,-50*rad,-35*rad,-45*rad]    
        elif STATE_VECTOR[HOLLOW]:
            new_limb_angles = [-0*rad,-160*rad,-110*rad,-170*rad,-150*rad,20*rad,-30*rad,30*rad,35*rad]      
        elif STATE_VECTOR[TUCKED]:
            new_limb_angles = [30*rad,40*rad,25*rad,-35*rad,-45*rad,-105*rad,-120*rad,20*rad,30*rad]
        elif STATE_VECTOR[RUNNING]:
            if run_time < stride_period/2:
                new_limb_angles = [-0*rad,35*rad,-40*rad,-45*rad,-110*rad,40*rad,-80*rad,60*rad,-35*rad] 
            else:    
                new_limb_angles = [-0*rad,-40*rad,35*rad,-110*rad,-45*rad,-80*rad,40*rad,-35*rad,100*rad] 
    
    if STATE_VECTOR[LONG]:
        new_limb_angles =  [0*rad,-150*rad,150*rad,-170*rad,170*rad,-20*rad,20*rad,-10*rad,10*rad]
    
    
    for i in xrange(len(limb_angles)):
        limb_angles[i] += .15* (new_limb_angles[i] - limb_angles[i])
        net_change += .15* (new_limb_angles[i] - limb_angles[i])
 
    return 20000*net_change    
        

def place_rigid_man(center_of_mass, angle):
    """
    translate and rotate rigid man to cm and angle about cm
    Updates limb positions
    """ 
    pass

def make_limb_list(neck_base, limb_angles, limb_lengths):
    """
    Sets limbs, neglecting rotation about cm
    """
    global limb_list
    
    xo = neck_base[0]
    yo = neck_base[1]
    new_limb_list = []

    # torso
    new_limb_list.append(Limb(neck_base,limb_angles[0],limb_lengths[0]))
    # left upper arm
    new_limb_list.append(Limb(neck_base,limb_angles[1],limb_lengths[1]))
    # right upper arm
    new_limb_list.append(Limb(neck_base,limb_angles[2],limb_lengths[2]))
        
    # left lower arm 
    new_limb_list.append(Limb([xo + angle_to_vector(limb_angles[1])[0] * limb_lengths[1],yo + angle_to_vector(limb_angles[1])[1] * limb_lengths[1]],limb_angles[3],limb_lengths[3]))
    # right lower arm
    new_limb_list.append(Limb([xo + angle_to_vector(limb_angles[2])[0] * limb_lengths[2],yo + angle_to_vector(limb_angles[2])[1] * limb_lengths[2]],limb_angles[4],limb_lengths[4]))
        
    xc = neck_base[0] + angle_to_vector(limb_angles[0])[0] * limb_lengths[0] 
    yc = neck_base[1] + angle_to_vector(limb_angles[0])[1] * limb_lengths[0]
        
    # left upper leg
    new_limb_list.append(Limb([xc,yc],limb_angles[5],limb_lengths[5]))
        
    # right upper leg
    new_limb_list.append(Limb([xc,yc],limb_angles[6],limb_lengths[6]))
        
    # left lower leg
    new_limb_list.append(Limb([xc + angle_to_vector(limb_angles[5])[0] * limb_lengths[5],yc + angle_to_vector(limb_angles[5])[1] * limb_lengths[5]],limb_angles[7],limb_lengths[7]))
    # lower right leg
    new_limb_list.append(Limb([xc + angle_to_vector(limb_angles[6])[0] * limb_lengths[6],yc + angle_to_vector(limb_angles[6])[1] * limb_lengths[6]],limb_angles[8],limb_lengths[8]))

    limb_list = new_limb_list 
    
def rotate_rigid_man(pos,my_ang):
    """
    Rotates limbs to angle from downwards vertical about pos
    """
    global limb_list, neck_base, center_of_mass, fulcrum_index
    global fulcrum_angle
    global IN_GAME
    
    count = -1
    
    # if pos == pseudo_center_of_mass, then we translate stickman to his true center of mass 
    flag_cm = False 
    if pos == center_of_mass:
        pos = get_center_of_mass(limb_list) # get pseudo-center of mass (cm of make_limb_list man)
        flag_cm = True
    else:
        if fulcrum_index == 9:
            pos = [limb_list[0].get_pos1()[0] - .2*(limb_list[0].get_pos2()[0] - limb_list[0].get_pos1()[0])  , limb_list[0].get_pos1()[1] - .2*(limb_list[0].get_pos2()[1] - limb_list[0].get_pos1()[1])]    
        else:    
            pos = limb_list[fulcrum_index].get_pos2() # get pseudo fulcrum
        #print "fulcrum"
        #print pos
    
    if flag_cm:   
        for limb in limb_list:
            
            count += 1
            
            # get vectors from pos to limb positions
            vector1 = [limb.get_pos1()[0] - pos[0],limb.get_pos1()[1] - pos[1]]
            vector2 = [limb.get_pos2()[0] - pos[0],limb.get_pos2()[1] - pos[1]]
            
            # get vector lengths
            r1 = get_dist(vector1,[0,0])
            r2 = get_dist(vector2,[0,0])
            
            # get vector angles
            ang1 = vector_to_angle(vector1)
            ang2 = vector_to_angle(vector2)
            
            
            # reset limb positions
            limb.set_pos1([pos[0] + r1*angle_to_vector(ang1 + my_ang)[0],pos[1] + r1*angle_to_vector(ang1 + my_ang)[1]])
            limb.set_pos2([pos[0] + r2*angle_to_vector(ang2 + my_ang)[0],pos[1] + r2*angle_to_vector(ang2 + my_ang)[1]])
    else:
        
        # fulcrum is the fulcrum to go to
        if fulcrum_index == 9:
            pseudo_fulcrum_to_real_fulcrum = [fulcrum[0] - pos[0] , fulcrum[1] -  pos[1]]
                        
        else:
            pseudo_fulcrum_to_real_fulcrum = [fulcrum[0] - pos[0] , fulcrum[1] -  pos[1]]
        
        
        count = 0
        
        while True:
            #print "yo"
            num_below = 0
            count += 1
            BELOW_GROUND = False
            
            for limb in limb_list:
                
                # get vectors from pos to limb positions
                vector1 = [limb.get_pos1()[0] - pos[0],limb.get_pos1()[1] - pos[1]]
                vector2 = [limb.get_pos2()[0] - pos[0],limb.get_pos2()[1] - pos[1]]
                
                # get vector lengths
                r1 = get_dist(vector1,[0,0])
                r2 = get_dist(vector2,[0,0])
                
                # get vector angles
                ang1 = vector_to_angle(vector1)
                ang2 = vector_to_angle(vector2)
                
                pos1 = [pos[0] + r1*angle_to_vector(ang1 + my_ang)[0],pos[1] + r1*angle_to_vector(ang1 + my_ang)[1]]
                pos2 = [pos[0] + r2*angle_to_vector(ang2 + my_ang)[0],pos[1] + r2*angle_to_vector(ang2 + my_ang)[1]]
                
                pos1 = [pos1[0] + pseudo_fulcrum_to_real_fulcrum[0], pos1[1] + pseudo_fulcrum_to_real_fulcrum[1]]
                pos2 = [pos2[0] + pseudo_fulcrum_to_real_fulcrum[0], pos2[1] + pseudo_fulcrum_to_real_fulcrum[1]]
                                
                #print "pos1[1]"
                #print pos1[1]
                #print "pos2[1]"
                #print pos2[1]
                
                if (pos2[1] > ground + 1):
                    #print "aaa"
                    #print pos2[1]
                    num_below += 1
                    #print "num_below"
                    #print num_below
                
            head_pos = [limb_list[0].get_pos1()[0] - .2*(limb_list[0].get_pos2()[0] - limb_list[0].get_pos1()[0])  , limb_list[0].get_pos1()[1] - .2*(limb_list[0].get_pos2()[1] - limb_list[0].get_pos1()[1])]
                
            head_pos = [head_pos[0] + pseudo_fulcrum_to_real_fulcrum[0], head_pos[1] + pseudo_fulcrum_to_real_fulcrum[1]]
                
            if (head_pos[1] > ground + 1):
                #print "headaaa"
                #print head_pos
                num_below += 1  
                #print "num_below"
                #print num_below
            """
            print "num_below"
            print num_below
            print "count"
            print count           
            """
            if num_below == 1:
                break
            
            # don't allow timeout    
            if count > 5:
                break
                
            if num_below  > 1:
                    
                #print "angle adjustment"    
                #print ((-1)**count) * .1 * count
                my_ang += ((-1)**count) * .5 *count*rad
                #print my_ang
                fulcrum_angle = my_ang                

                
        # reset limb positions
        for limb in limb_list:
            
            # get vectors from pos to limb positions
            vector1 = [limb.get_pos1()[0] - pos[0],limb.get_pos1()[1] - pos[1]]
            vector2 = [limb.get_pos2()[0] - pos[0],limb.get_pos2()[1] - pos[1]]
                
            # get vector lengths
            r1 = get_dist(vector1,[0,0])
            r2 = get_dist(vector2,[0,0])
                
            # get vector angles
            ang1 = vector_to_angle(vector1)
            ang2 = vector_to_angle(vector2)            
            
            limb.set_pos1([pos[0] + r1*angle_to_vector(ang1 + my_ang)[0],pos[1] + r1*angle_to_vector(ang1 + my_ang)[1]])
            limb.set_pos2([pos[0] + r2*angle_to_vector(ang2 + my_ang)[0],pos[1] + r2*angle_to_vector(ang2 + my_ang)[1]])
              
                
    if flag_cm:
        # translate rigid man from pseudo_cm to center_of_mass   
        pos = get_center_of_mass(limb_list)
        # center of mass is the true cm to go to
        pseudo_cm_to_real_cm = [center_of_mass[0] - pos[0], center_of_mass[1] - pos[1]]
        for limb in limb_list:
            pos1 = limb.get_pos1()
            limb.set_pos1([pos1[0] + pseudo_cm_to_real_cm[0], pos1[1] + pseudo_cm_to_real_cm[1]])
            pos2 = limb.get_pos2()
            limb.set_pos2([pos2[0] + pseudo_cm_to_real_cm[0], pos2[1] + pseudo_cm_to_real_cm[1]])            
        
    else:
        # translate rigid man to fulcrum
        #print "fulcrum_index"
        #print fulcrum_index

        for limb in limb_list:
            pos1 = limb.get_pos1()
            limb.set_pos1([pos1[0] + pseudo_fulcrum_to_real_fulcrum[0], pos1[1] + pseudo_fulcrum_to_real_fulcrum[1]])
            pos2 = limb.get_pos2()
            limb.set_pos2([pos2[0] + pseudo_fulcrum_to_real_fulcrum[0], pos2[1] + pseudo_fulcrum_to_real_fulcrum[1]])        
        

        
    # update cm (does nothing if rotation was about cm)
    center_of_mass = get_center_of_mass(limb_list)


    #print limb_list[1].get_pos1()
    
    if fulcrum_index == 9:
        IN_GAME = False
        
def new_game():
    """
    start new game
    Initialize limbs, center of mass, and angle about center of mass
    """
    
    global limb_angles, limb_lengths, limb_list, center_of_mass, cm_angle, neck_base
    global time_left, score, vel
    global ON_GROUND
    global IN_GAME, PLANTED, TITLE_SCREEN, HOW_TO_PLAY, HIGH_SCORES, TUTORIAL
    global fulcrum_index
    global rotational_momentum, artificial_momentum
    global level, lives, transformers, epic
    global epic_timer, transformer_timer
    
    epic_timer = 0
    transformer_timer = 0
    
    if TUTORIAL:
        transformers.play()
    else:    
        epic.play()
    
    level = 1
    lives = 3
    
    rotational_momentum = 0
    artificial_momentum = 0
    limb_angles = [-30*rad,-45*rad,20*rad,10*rad,45*rad,3*rad,10*rad,-25*rad,-5*rad] # list of stick figure limb angles with the downward vertical (given angle about cm = 0)

    make_limb_list(neck_base, limb_angles, limb_lengths)
    center_of_mass = get_center_of_mass(limb_list)
    
    cm_angle = 0
    rotate_rigid_man(center_of_mass, cm_angle)
    
    vel = [0,0]
    time_left = 30
    score = 0
    
    ON_GROUND = False
    IN_GAME = True
    TITLE_SCREEN = False
    HOW_TO_PLAY = False
    HIGH_SCORES = False
    PLANTED = False
    fulcrum_index = 50
    #vel = [0,0]

def update_center_of_mass(accel):
    """
    update center_of_mass
    """
    global center_of_mass, vel
    
    for i in xrange(2):
        center_of_mass[i] += vel[i]*dt + .5 * accel[i] * dt**2 

    for i in xrange(2):
        vel[i] += accel[i] * dt                         

### BODY POSITION FUNCTIONS ###        
def stand():
    global STANDING, ARCHED, HOLLOW, TUCKED, LONG
    
    for i in xrange(len(STATE_VECTOR)):
        STATE_VECTOR[i] = False
    STATE_VECTOR[STANDING] = True
    
def lengthen():
    global STANDING, ARCHED, HOLLOW, TUCKED, LONG, STATE_VECTOR
    
    for i in xrange(len(STATE_VECTOR)):
        STATE_VECTOR[i] = False
    STATE_VECTOR[LONG] = True 
    
def arch():
    global STANDING, ARCHED, HOLLOW, TUCKED, LONG, STATE_VECTOR
    
    for i in xrange(len(STATE_VECTOR)):
        STATE_VECTOR[i] = False
    STATE_VECTOR[ARCHED] = True

def hollow():
    global STANDING, ARCHED, HOLLOW, TUCKED, LONG, STATE_VECTOR
    
    for i in xrange(len(STATE_VECTOR)):
        STATE_VECTOR[i] = False
    STATE_VECTOR[HOLLOW] = True

    
def tuck():
    global STANDING, ARCHED, HOLLOW, TUCKED, LONG, STATE_VECTOR
    
    for i in xrange(len(STATE_VECTOR)):
        STATE_VECTOR[i] = False
    STATE_VECTOR[TUCKED] = True

def run():
    global STANDING, ARCHED, HOLLOW, TUCKED, LONG, RUNNING, STATE_VECTOR
    
    for i in xrange(len(STATE_VECTOR)):
        STATE_VECTOR[i] = False
    STATE_VECTOR[RUNNING] = True
    
def get_moment(pos):
    """
    Returns moment of inertia about position
    """
    global limb_list, head_weight
    
    global limb_lengths #weights
    global limb_angles
    
    moment = 0 # moment of inertia
    
    xcm = 0
    ycm = 0
    
    for limb in limb_list:
        x_center = (limb.get_pos1()[0] + limb.get_pos2()[0]) * .5
        y_center = (limb.get_pos1()[1] + limb.get_pos2()[1]) * .5
        dist = get_dist([x_center,y_center],pos)
        moment += limb.get_length() * (dist**2)
        
        
    # add moment due to head
    head_pos = [limb_list[0].get_pos1()[0] - .2*(limb_list[0].get_pos2()[0] - limb_list[0].get_pos1()[0])  , limb_list[0].get_pos1()[1] - .2*(limb_list[0].get_pos2()[1] - limb_list[0].get_pos1()[1])]
        
    dist = get_dist(head_pos, pos)
    moment += head_weight * (get_dist([0,0],[10*angle_to_vector(limb_angles[0])[0], -10*angle_to_vector(limb_angles[0])[1]]) ** 2)

    if STATE_VECTOR[ARCHED]:
        moment *= .3
    elif STATE_VECTOR[TUCKED]:
        moment *= .6
        
    return moment

def compute_new_angle(base, point, old_base, old_point):
    """
    compute angle about cm between make_limb_list stickman and current stickman 
    Used when rotation base point changes between cm and fulcrum
    """
    global limb_list, center_of_mass
    
    old_vector = [old_point[0] - old_base[0], old_point[1] - old_base[1]]
    vector = [point[0] - base[0],point[1] - base[1]]
    
    
    #print "old_vector"
    #print old_vector
    #print "vector"
    #print vector
    
    old_angle = vector_to_angle(old_vector)
    angle = vector_to_angle(vector)
    

    #print "old_angle"
    #print angle
    #print "angle"
    #print old_angle
    
    return angle - old_angle

def put_stickman_above_ground():
    """
    Lift stickman off the ground
    """
    global limb_list, ground, center_of_mass, fulcrum_index, fulcrum
    
    low = fulcrum	# low[1]
    
    for i in xrange(len(limb_list)):
        if limb_list[i].get_pos2()[1] > low[1]:
            low = limb_list[i].get_pos2()

        
    head_pos = [limb_list[0].get_pos1()[0] - .2*(limb_list[0].get_pos2()[0] - limb_list[0].get_pos1()[0])  , limb_list[0].get_pos1()[1] - .2*(limb_list[0].get_pos2()[1] - limb_list[0].get_pos1()[1])]    
    
    if head_pos[1] > low[1]:
        low = head_pos
        fulcrum_index = 9
        
    height_to_add = (ground - 4) - low[1]
    
    for limb in limb_list:
        limb.set_pos1([limb.get_pos1()[0], limb.get_pos1()[1] + height_to_add])
        limb.set_pos2([limb.get_pos2()[0], limb.get_pos2()[1] + height_to_add])
        
    center_of_mass[1] += height_to_add
    
def put_stickman_on_ground():
    """
    Lift stickman back onto ground
    """
    global limb_list, ground, center_of_mass, fulcrum_index, low
    
    low = [0,0]	
    
    for i in xrange(len(limb_list)):
        if limb_list[i].get_pos2()[1] > low[1]:
            low = limb_list[i].get_pos2()
            fulcrum_index = i
        
    head_pos = [limb_list[0].get_pos1()[0] - .2*(limb_list[0].get_pos2()[0] - limb_list[0].get_pos1()[0])  , limb_list[0].get_pos1()[1] - .2*(limb_list[0].get_pos2()[1] - limb_list[0].get_pos1()[1])]    
    
    if head_pos[1] > low[1]:
        low = head_pos
        fulcrum_index = 9
        
    height_to_add = (ground + 1) - low[1]
    
    for limb in limb_list:
        limb.set_pos1([limb.get_pos1()[0], limb.get_pos1()[1] + height_to_add])
        limb.set_pos2([limb.get_pos2()[0], limb.get_pos2()[1] + height_to_add])
        
    center_of_mass[1] += height_to_add

    #print "fulcrum from put_stickman_on_ground"
    #print low
    
    if fulcrum_index < 9:
        return limb_list[fulcrum_index].get_pos2()    # new fulcrum
    else:
        return [head_pos[0], head_pos[1] + height_to_add]

def is_on_ground():
    global limb_list, ground, max_rotational_momentum
    
    for limb in limb_list:
        if limb.get_pos2()[1] > ground:
            return True

    head_pos = [limb_list[0].get_pos1()[0] - .2*(limb_list[0].get_pos2()[0] - limb_list[0].get_pos1()[0])  , limb_list[0].get_pos1()[1] - .2*(limb_list[0].get_pos2()[1] - limb_list[0].get_pos1()[1])]    
   
    if head_pos[1] > ground:
        return True
    
    return False

def hop():
    global vel
    vel = [10,-10]

def jump(init_vel):
    """ jump """
    global vel, center_of_mass, fulcrum, rotational_momentum, STATE_VECTOR, limb_angles, JUMPED
    global artificial_momentum, DID_SUPER_JUMP

    
    vel = [init_vel[0] + center_of_mass[0] - fulcrum[0], init_vel[1] + center_of_mass[1] - fulcrum[1]]
        
    #print limb_angles[2]*180/math.pi
    if abs(limb_angles[2]*180/math.pi) > 111:
        if (RIGHT and rotational_momentum < -0) or (not(RIGHT) and rotational_momentum > 0):
            rotational_momentum = 0
            
    if abs(artificial_momentum) > max_rotational_momentum:
        vel[1] *= 3.2
        rotational_momentum *= .60
        artificial_momentum *= .3
        DID_SUPER_JUMP = True
        
    
    if STATE_VECTOR[ARCHED]:
        if RIGHT:
            vel[0] += -70
        else:
            vel[0] += 70

    if (STATE_VECTOR[TUCKED] == True):
        vel[0] *= .02
        vel[1] *= .02
    else:
        vel[0] *= .2
        vel[1] *= .2   
    
    if RUN:
        vel = [0,0]
    else:
        JUMPED = True        
        
def draw(canvas):
    global neck_base, limb_list, limb_angles, limb_lengths, center_of_mass, fulcrum, fulcrum_angle, fulcrum_index
    global low
    global vel, accel, g, dt
    global cm_angle, fulcrum_angle
    global make_limb_list_neck
    global net_body_change
    global ON_GROUND, PLANTED
    global JUMP, STANDING, LONG, ARCHED, HOLLOW, TUCKED, STATE_VECTOR

    global score, time_left
    global old_neck, old_fulcrum, new_neck
    global WIDTH
    global CHANGED_BODY
    global IN_GAME, image, TITLE_SCREEN, HOW_TO_PLAY, HIGH_SCORES
    global rotational_momentum
    global run_time, stride_period, RUN, init_vel
    global level, level_count
    global angle_pre_jump, angle_post_jump
    global high_scores
    global max_rotational_momentum, JUMPED, artificial_momentum
    global TUTORIAL
    global lives, DID_SUPER_JUMP, lives_before_super_jump, counter, direction, pos_before_jump
    global transformers, epic, transformer_timer, epic_timer
    
    epic_timer += 1
    transformer_timer += 1
    
    if epic_timer > 8000:
        epic_timer = 0
        epic.rewind()
        epic.play()
    elif transformer_timer > 8000:
        transformer_timer = 0
        transformers.rewind()
        transformers.play()
        
        
    #print "IN_GAME"
    #print IN_GAME
    
    #print limb_angles[0] * 180/math.pi
    
    if not(HOW_TO_PLAY or HIGH_SCORES):
        canvas.draw_image(image, (447 / 2, 336 / 2), (447, 336), (WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    if IN_GAME:
        # ON_GROUND reflects last state 
        if not(JUMP):
            ON_GROUND = is_on_ground()      

        net_body_change = conform_rigid_man() # get new angles
    
        # update stick man, neglecting relationship to center_of_mass
        make_limb_list(neck_base, limb_angles, limb_lengths) # (1) get new limb positions, neglecting relationship to center_of_mass
               
        # translate rigid man into correct position 
        
        
        #rotate_rigid_man(center_of_mass, cm_angle) #debugging- get t-1 position
    
        if not(ON_GROUND): 
            #print "start" 
            #print center_of_mass
            #print cm_angle
            rotate_rigid_man(center_of_mass, cm_angle)
        else:
            #rotate_rigid_man(center_of_mass, cm_angle)
            rotate_rigid_man(fulcrum, fulcrum_angle)
            #print fulcrum
            
        
        # man is at cm_angle at this point
        #print "A"  
        #print [limb.get_pos1() for limb in limb_list]
        #canvas.draw_circle(limb_list[0].get_pos1() , 7, 2, "Green","Green")
        #print center_of_mass
        #print cm_angle
        #print limb_list[1].get_pos1()      
        
        
        
        #print "was ON_GROUND"
        #print ON_GROUND
    
        accel = g
        
        if not(ON_GROUND):
            #print "He was in the air before OR HE JUMPED!"
            update_center_of_mass(accel) # update center_of_mass
            moment_of_inertia = get_moment(center_of_mass) # get moment about center_of_mass
            cm_angle += rotational_momentum/moment_of_inertia * dt
            #print "end"     
            #print center_of_mass
            #print cm_angle
            make_limb_list(neck_base, limb_angles, limb_lengths) # (1) get new limb positions, neglecting relationship to center_of_mass
            rotate_rigid_man(center_of_mass, cm_angle) # (2) rotate rigid man about his true center of mass   
        
        center_of_mass = [center_of_mass[0] % WIDTH, center_of_mass[1]]
        # is_on_ground() reflects current state
        #print "is_on_ground()"
        #print is_on_ground()
        
        # in the air
        if not(is_on_ground()):
            if ON_GROUND:
                angle_pre_jump = cm_angle
                make_limb_list(neck_base, limb_angles, limb_lengths) # (1) get new limb positions, neglecting relationship to center_of_mass
                old_neck = limb_list[0].get_pos1()
                old_cm = get_center_of_mass(limb_list)
                rotate_rigid_man(fulcrum, fulcrum_angle) # rotate about fulcrum (which is now in the air from a jump)
                new_neck = limb_list[0].get_pos1()
                cm_angle = compute_new_angle(center_of_mass, new_neck, old_cm, old_neck) # compute corresponding cm_angle    
       
        # on the ground    
        else:
            if not(STATE_VECTOR[ARCHED]):
                rotational_momentum *= .94
                artificial_momentum *= .97
            else:
                rotational_momentum *= .98
                artificial_momentum *= .995
            if not(ON_GROUND):
                angle_post_jump = cm_angle
                #print "He wasn't on the ground til now!"
                make_limb_list(neck_base, limb_angles, limb_lengths) # (1) get new limb positions, neglecting relationship to center_of_mass            
                
                rotate_rigid_man(center_of_mass, cm_angle) # rotate about center of mass
                #print "limb_list[8].get_pos2()"
                #print limb_list[8].get_pos2()
                fulcrum = put_stickman_on_ground() # lift stickman onto the ground, get fulcrum and fulcrum_index

                PLANTED = True
                # get old_fulcrum and old_neck
                make_limb_list(neck_base, limb_angles, limb_lengths) # (1) get new limb positions, neglecting relationship to center_of_mass            
                if fulcrum_index == 9:
                    old_fulcrum = [limb_list[0].get_pos1()[0] - .2*(limb_list[0].get_pos2()[0] - limb_list[0].get_pos1()[0])  , limb_list[0].get_pos1()[1] - .2*(limb_list[0].get_pos2()[1] - limb_list[0].get_pos1()[1])]
                else:
                    old_fulcrum = limb_list[fulcrum_index].get_pos2()
                old_neck = limb_list[0].get_pos1()
                
                rotate_rigid_man(center_of_mass, cm_angle) # rotate about center of mass 
                new_neck = limb_list[0].get_pos1()         
                """
                print "old_fulcrum"
                print old_fulcrum
                print "fulcrum"
                print fulcrum
                """
                #canvas.draw_circle(fulcrum,4,2,'Red','Red')
                
                fulcrum_angle = compute_new_angle(fulcrum, new_neck, old_fulcrum, make_limb_list_neck) # compute corresponding fulcrum_angle (now on the ground)           
            else:  
                #print "He's still on the ground!"
                make_limb_list(neck_base, limb_angles, limb_lengths) # (1) get new limb positions, neglecting relationship to center_of_mass            
                rotate_rigid_man(fulcrum, fulcrum_angle)
    
        if PLANTED:
            #print "He's still on the ground!"
            make_limb_list(neck_base, limb_angles, limb_lengths) # (1) get new limb positions, neglecting relationship to center_of_mass            
            rotate_rigid_man(fulcrum, fulcrum_angle)        
    
                #print "fulcrum angle"
                #print fulcrum_angle/rad
                
            moment_of_inertia = get_moment(fulcrum) # get moment about fulcrum
            fulcrum_angle += rotational_momentum/moment_of_inertia * dt
    

        
        if JUMP and ON_GROUND:
            rotational_momentum += net_body_change
            artificial_momentum += net_body_change            
            put_stickman_above_ground()
            jump(init_vel) #jump (change linear velocity of cm)
            ON_GROUND = False
            PLANTED = False
        
        
        elif RUN:
            if is_on_ground():
                if run_time > stride_period:
                    run_time = 0
                run()
                run_time += 1
                cm_angle = 0
                if RIGHT:
                    center_of_mass[0] += 8
                    init_vel = [50,-50]
                else:
                    center_of_mass[0] -= 8
                    init_vel = [-50,-50]
        else:
            init_vel[0] *= .95
            init_vel[1] *= .95
            
        rotational_momentum = min(rotational_momentum,max_rotational_momentum)
        artificial_momentum = min(artificial_momentum,max_rotational_momentum)
        
        if CHANGED_BODY and ON_GROUND:
            CHANGED_BODY = False
            fulcrum = put_stickman_on_ground() # lift stickman onto the ground, get fulcrum and fulcrum_index
                        
        #canvas.draw_circle(fulcrum,7, 2, "Blue","Blue") # draw rotation point          
        #canvas.draw_circle(get_center_of_mass(limb_list), 4, 2, 'Red')   # draw true cm   
    
         
        for limb in limb_list:
            limb.draw(canvas)
    
        # draw neck and head
        canvas.draw_line(limb_list[0].get_pos1(),[limb_list[0].get_pos1()[0] - .2*(limb_list[0].get_pos2()[0] - limb_list[0].get_pos1()[0])  , limb_list[0].get_pos1()[1] - .2*(limb_list[0].get_pos2()[1] - limb_list[0].get_pos1()[1])],2,"White")
        canvas.draw_circle([limb_list[0].get_pos1()[0] - .2*(limb_list[0].get_pos2()[0] - limb_list[0].get_pos1()[0])  , limb_list[0].get_pos1()[1] - .2*(limb_list[0].get_pos2()[1] - limb_list[0].get_pos1()[1])], 7, 2, "White","Black")
            
        canvas.draw_line([0,ground],[WIDTH,ground],2,"White")
        
        #canvas.draw_circle(fulcrum,4,2,'Green','Green')
        
        # if head hits ground, end game
        if (limb_list[0].get_pos1()[1] - .2*(limb_list[0].get_pos2()[1] - limb_list[0].get_pos1()[1])  > ground):
            
            counter = 30
            lives -= 1
            rotational_momentum = 0
            artificial_momentum = 0
            limb_angles = [-30*rad,-45*rad,20*rad,10*rad,45*rad,3*rad,10*rad,-25*rad,-5*rad] # list of stick figure limb angles with the downward vertical (given angle about cm = 0)
            
            make_limb_list(neck_base, limb_angles, limb_lengths)
            center_of_mass = get_center_of_mass(limb_list)
            
            cm_angle = 0
            rotate_rigid_man(center_of_mass, cm_angle)
            
            vel = [0,0]
            
            ON_GROUND = False
            PLANTED = False
            fulcrum_index = 50
            
            IN_GAME = True
            
            if lives == 0:
                if TUTORIAL:
                    transformers.rewind()
                else:    
                    epic.rewind()
                IN_GAME = False
                TITLE_SCREEN = True
                if score not in high_scores:
                    high_scores.append(score)  
            
        #time_left -= 0.0/30.0    

            
        canvas.draw_text('Score: ' + str(score), (80, 50), 20, 'Gray', 'serif')
        canvas.draw_text('Lives: ' + str(lives), (240, 50), 20, 'Gray', 'serif')
        if TUTORIAL:
            canvas.draw_text('Level: ' + str(level), (380, 50), 20, 'Gray', 'serif')
        else:
            canvas.draw_text('Skill: ' + str(level), (380, 50), 20, 'Gray', 'serif')
        #canvas.draw_text('Time Left: ' + str(math.ceil(time_left)), (180, 50), 20, 'Gray', 'serif')
        
        canvas.draw_text('Super Jump',(601,50),20,'Red','serif')
        canvas.draw_line([600,80],[600 + abs(artificial_momentum)/1000,80],15,'Red')
        canvas.draw_line([600,90],[600,70],5,'Yellow')
        canvas.draw_line([600 + max_rotational_momentum/1000,90],[600 + max_rotational_momentum/1000,70],5,'Yellow')
        #print "Q"
        #print [limb.get_pos1() for limb in limb_list]
        #canvas.draw_circle(limb_list[0].get_pos1() , 7, 2, "Redif","Red")   
        
        #print center_of_mass
        #print cm_angle
        #print limb_list[1].get_pos1() 
        
        
        #canvas.draw_text('pre jump angle = ' + str(angle_pre_jump/rad),(100,220),20,'Red','serif')   
        #canvas.draw_text('post jump angle = ' + str(angle_post_jump/rad),(100,250),20,'Red','serif')         
        
        if TUTORIAL:
            if level == 1:
                canvas.draw_text('Hold the right arrow to run right',(100,100),20,'Red','serif')
                
                
                if RUN and RIGHT:
                    level_count += 1
                else:
                    level_count = 0
                    
                if level_count >= 60:
                    level += 1
                     
                    
            elif level == 2:
                
                if level_count >= 60:
                    if level_count == 60:
                        score += 50
                    level_count += 1
                    canvas.draw_text('Well done!',(100,100),20,'Green','serif')
                    
                if level_count > 80:
                    level_count = 0
                
                if level_count < 60:
                    canvas.draw_text('Hold the left arrow to run left',(100,100),20,'Red','serif')
                
                
                    if RUN and not(RIGHT):
                        level_count += 1
                        if level_count >= 60:
                            level += 1
                    else:
                        level_count = 0
                        
                    
                     
                    
            elif level == 3:
                
                if level_count >= 60:
                    if level_count == 60:
                        score += 50
                    level_count += 1
                    canvas.draw_text('Well done!',(100,100),20,'Green','serif')
                if level_count > 80:
                    level_count = 0  
                    
                if level_count < 60:
                    canvas.draw_text('Do a front flip.',(100,100),20,'Red','serif')
                    canvas.draw_text('Hold r to get into the hollow body position.',(100,130),20,'Red','serif')
                    canvas.draw_text('Release r and press space to jump.',(100,160),20,'Red','serif')
                    canvas.draw_text('Then press t to tuck',(100,190),20,'Red','serif')        
      
                    if JUMPED and (RIGHT and angle_post_jump/rad < angle_pre_jump/rad - 300) or (not(RIGHT) and angle_post_jump/rad > angle_pre_jump/rad + 300):
                        JUMPED = False
                        level += 1
                        level_count = 60
             
            elif level == 4:      
                canvas.draw_text('Do a handstand!',(100,100),20,'Red','serif')
                canvas.draw_text('Do a half front flip and press w when upside down to put down your hands!',(100,140),20,'Red','serif') 
                

                if STATE_VECTOR[LONG] and (.8*math.pi < abs(cm_angle) < 1.2*math.pi):
                    level_count += 1
                else:
                    level_count = 0
                    
                if level_count >= 60:
                    level += 1

            elif level == 5:
                if level_count >= 60:
                    level_count += 1
                    canvas.draw_text('Good job!',(100,100),20,'Green','serif')
                    score += 100
                if level_count >= 80:
                    level_count = 0                 
                            
                        
                if level_count < 60:
                    canvas.draw_text('Do a back flip.',(100,100),20,'Red','serif')
                    canvas.draw_text('Press e to throw back into an arched body position.',(100,130),20,'Red','serif')
                    canvas.draw_text('Without releasing e, immediately press space to jump.',(100,160),20,'Red','serif')
                    canvas.draw_text('Then press t to tuck',(100,190),20,'Red','serif')        
      
                    if JUMPED and (RIGHT and angle_post_jump/rad > angle_pre_jump/rad + 300) or (not(RIGHT) and angle_post_jump/rad < angle_pre_jump/rad - 300):
                        JUMPED = False
                        level += 1
                        level_count = 60

                        
            elif level == 6:
                
                if  (60 <= level_count) and (level_count < 80):
                    level_count += 1
                    canvas.draw_text('Nice!',(100,100),20,'Green','serif')
                    score += 100
                if level_count == 80:
                    level_count = 0      
                 
                if level_count < 60:    
                    canvas.draw_text('Do Back handsprings to achieve a Super Jump:',(100,100),20,'Red','serif')    
                    canvas.draw_text('Press e and then spacebar when feet/hands hit the ground.',(100,130),20,'Red','serif')
                    
                    if DID_SUPER_JUMP:
                        #flag = True
                        JUMPED = False
                        level_count = 100
                        lives_before_super_jump = lives
                    
                if level_count >= 100:     
                    if is_on_ground() and lives_before_super_jump == lives:
                        level_count = 61
                        level += 1
                    elif lives_before_super_jump != lives:
                        level_count = 0
                        DID_SUPER_JUMP = False
                        
            elif level == 7:
                if level_count >= 60:
                    level_count += 1
                    canvas.draw_text('Nice!',(100,100),20,'Green','serif')
                    score += 150
                if level_count >= 100:
                    level_count = 0
                if level_count < 60:    
                    canvas.draw_text('Congratulations! You have completed the tutorial.',(100,100),20,'Green','serif')
    
                    
        # in real game, not in tutorial   
        else:  
              
            if level == 1:
                if level_count >= 60:
                    level_count += 1
                    canvas.draw_text('Good job!',(100,100),20,'Green','serif')
                    score += 100
                if level_count >= 80:
                    level_count = 0                 
                            
                        
                if level_count < 60:
                    canvas.draw_text('Do a backflip.',(100,100),20,'Red','serif')     
      
                    if JUMPED and (RIGHT and angle_post_jump/rad > angle_pre_jump/rad + 300) or (not(RIGHT) and angle_post_jump/rad < angle_pre_jump/rad - 300):
                        JUMPED = False
                        level = random.randint(1,6)
                        level_count = 60

                        
            elif level == 2:
                
                if level_count >= 60:
                    level_count += 1
                    canvas.draw_text('Good job!',(100,100),20,'Green','serif')
                    score += 100
                if level_count >= 80:
                    level_count = 0                 
                            
                        
                if level_count < 60:
                    canvas.draw_text('Do a double backflip.',(100,100),20,'Red','serif')
     
                     
                    if JUMPED and (RIGHT and angle_post_jump/rad > angle_pre_jump/rad + 1100) or (not(RIGHT) and angle_post_jump/rad < angle_pre_jump/rad - 1100):
                        JUMPED = False
                        level_count = 100
                        lives_before_super_jump = lives
                    
                if level_count >= 100:     
                    if is_on_ground() and lives_before_super_jump == lives:
                        level_count = 61
                        level = random.randint(1,6)
                    elif lives_before_super_jump != lives:
                        level_count = 0
                        
            elif level == 3:
                if 60 <= level_count < 91:
                    level_count += 1
                    canvas.draw_text('Nice!',(100,100),20,'Green','serif')
                    score += 150
                if 90 < level_count < 99:
                    level_count = 0
                if level_count < 60:   
                    canvas.draw_text('Do a gainer! This is a running backflip',(100,100),20,'Red','serif')
                    canvas.draw_text('where you land in front of the point where you start!',(100,140),20,'Red','serif')
                    canvas.draw_text('HINT: You can also backflip with r. It\'s only a little bit scary, I promise!',(100,180),20,'Red','serif')
                                        
                    #print "hi!"
                    #print fulcrum
                    if JUMPED:
                        
                        JUMPED = False
                        level_count = 100
                        lives_before_super_jump = lives
                    else:
                        #print "yo"
                        direction = RIGHT
                        pos_before_jump = fulcrum	   

                        
                if level_count >= 100:    
                    canvas.draw_text('Do a gainer! This is a running backflip',(100,100),20,'Red','serif')
                    canvas.draw_text('where you land in front of the point where you start!',(100,140),20,'Red','serif')
                    canvas.draw_text('HINT: You can also backflip with r. It\'s only a little bit scary, I promise!',(100,180),20,'Red','serif')
                           


                    if is_on_ground():

                        if ((direction and angle_post_jump/rad > angle_pre_jump/rad + 290) or (not(direction) and angle_post_jump/rad < angle_pre_jump/rad - 290)) and lives_before_super_jump == lives and ((pos_before_jump[0] < fulcrum[0] and direction) or (pos_before_jump[0] > fulcrum[0] and not(direction))):
                            level_count = 61
                            level = random.randint(1,6)
                        else:
                            level_count = 0        
             
            elif level == 4:      
                canvas.draw_text('Do a handstand!',(100,100),20,'Red','serif')
                canvas.draw_text('Do a half front flip and press w when upside down to put down your hands!',(100,140),20,'Red','serif') 
                

                if STATE_VECTOR[LONG] and (.8*math.pi < abs(cm_angle) < 1.2*math.pi):
                    level_count += 1
                else:
                    level_count = 0
                    
                if level_count >= 60:
                    level = random.randint(1,6)
                    
                    
            elif level == 5:
                
                if level_count >= 60:
                    if level_count == 60:
                        score += 50
                    level_count += 1
                    canvas.draw_text('Well done!',(100,100),20,'Green','serif')
                if level_count > 80:
                    level_count = 0  
                    
                if level_count < 60:
                    canvas.draw_text('Do a front flip.',(100,100),20,'Red','serif')     
      
                    if JUMPED and (RIGHT and angle_post_jump/rad < angle_pre_jump/rad - 300) or (not(RIGHT) and angle_post_jump/rad > angle_pre_jump/rad + 300):
                        JUMPED = False
                        level = random.randint(1,6)
                        level_count = 60
                        
            elif level == 6:
                
                if level_count >= 60:
                    level_count += 1
                    canvas.draw_text('Good job!',(100,100),20,'Green','serif')
                    score += 100
                if level_count >= 80:
                    level_count = 0                 
                            
                        
                if level_count < 60:
                    canvas.draw_text('Do a triple backflip.',(100,100),20,'Red','serif')
     
                     
                    if JUMPED and (RIGHT and angle_post_jump/rad > angle_pre_jump/rad + 1400) or (not(RIGHT) and angle_post_jump/rad < angle_pre_jump/rad - 1400):
                        JUMPED = False
                        level_count = 100
                        lives_before_super_jump = lives
                    
                if level_count >= 100:     
                    if is_on_ground() and lives_before_super_jump == lives:
                        level_count = 61
                        level = random.randint(1,6)
                    elif lives_before_super_jump != lives:
                        level_count = 0
        
        if counter == 30:
            counter -= 1
            pain.play()
        elif counter == 0:
            pain.rewind()
        else:
            counter -= 1
            
        if is_on_ground():
            JUMPED = False
            DID_SUPER_JUMP = False
    else:
        
        if TITLE_SCREEN:
            canvas.draw_text('STICKMAN GYMNASTICS', (WIDTH/2 - 180, 60), 30, 'grey', 'monospace')
            #canvas.draw_text('Click to anywhere to begin', (WIDTH/2 - 130, 85), 15, 'grey', 'monospace')
            
            canvas.draw_line([320,140],[470,140],35,'Grey')
            canvas.draw_text('Start', [365,145], 20 , 'Black', 'monospace')
            canvas.draw_line([320,180],[470,180],35,'Grey')
            canvas.draw_text('Tutorial', [345,185], 20 , 'Black', 'monospace')
            canvas.draw_line([320,220],[470,220],35,'Grey')
            canvas.draw_text('How To Play', [328,225], 20 , 'Black', 'monospace')
            canvas.draw_line([320,260],[470,260],35,'Grey')
            canvas.draw_text('High Scores', [328,265], 20 , 'Black', 'monospace')
    
    
        elif HOW_TO_PLAY:

            color = 'Silver'
            canvas.draw_text('Controls:', [100,145], 20 , color , 'monospace')
    
            canvas.draw_text('left arrow : faces stickman to the left, hold to run', [100,230], 20 , color , 'monospace')
            canvas.draw_text('right arrow : faces stickman to the right, hold to run', [100,260], 20 , color , 'monospace')
            canvas.draw_text('w : long position, for handstands', [100,290], 20 , color , 'monospace')
            canvas.draw_text('e : arched position ', [100,320], 20 , color , 'monospace')
            canvas.draw_text('r : hollow position', [100,350], 20 , color , 'monospace')
            canvas.draw_text('t : tucks stickman into a ball, speeding up his rotation', [100,380], 20 , color , 'monospace')
            canvas.draw_text('space : causes stickman to jump if he is on the ground', [100,410], 20 , color , 'monospace')
                                                                                 
        
        elif HIGH_SCORES:
            high_scores.sort(reverse = True)
            
            color = 'Silver'
            
            canvas.draw_text('High Scores', [340,100], 20 , color , 'monospace')
            
            for i in xrange(min(10, len(high_scores))):
                
                canvas.draw_text(str(i + 1) + '. ' + str(high_scores[i]), [100,140 + 25*i], 20 , color , 'monospace')
            
def key_down(key):
    global JUMP, RUN, RIGHT, PREV_RIGHT, CHANGED_BODY, STATE_VECTOR, vel
            
    if key == simplegui.KEY_MAP["space"]:
        if RUN:
            pass
        else:
            JUMP = True
    if key == simplegui.KEY_MAP["w"]:
        lengthen() 
        CHANGED_BODY = True  
    if key == simplegui.KEY_MAP["e"]:
        arch() 
        CHANGED_BODY = True
    if key == simplegui.KEY_MAP["r"]:
        hollow() 
        CHANGED_BODY = True  
    if key == simplegui.KEY_MAP["t"]:
        tuck()    
        CHANGED_BODY = True
    if key == simplegui.KEY_MAP["right"]:            
        RIGHT = True        
        RUN = True
        JUMP = True
        CHANGED_BODY = True
    if key == simplegui.KEY_MAP["left"]:        
        RIGHT = False        
        RUN = True
        JUMP = True
        CHANGED_BODY = True
        
def key_up(key):
    global JUMP, RUN, CARTWHEEL, RIGHT, PREV_RIGHT, CHANGED_BODY
    PREV_RIGHT = RIGHT
    if key == simplegui.KEY_MAP["space"]:
        if RUN:
            pass
        else:
            JUMP = False
    if key == simplegui.KEY_MAP["w"]:
        stand() 
        CHANGED_BODY = True  
    if key == simplegui.KEY_MAP["e"]:
        stand() 
        CHANGED_BODY = True
    if key == simplegui.KEY_MAP["r"]:
        stand() 
        CHANGED_BODY = True 
    if key == simplegui.KEY_MAP["t"]:
        stand() 
        CHANGED_BODY = True
    if key == simplegui.KEY_MAP["right"]:      
        stand()
        JUMP = False
        RUN = False
    if key == simplegui.KEY_MAP["left"]:       
        stand()
        JUMP = False
        RUN = False     
    
def mouse_handler(pos):
    global TITLE_SCREEN, HOW_TO_PLAY, HIGH_SCORES, TUTORIAL
    
    """
    canvas.draw_line([300,140],[450,140],35,'Grey')
    canvas.draw_text('Start', [345,145], 20 , 'Black', 'monospace')
    canvas.draw_line([300,180],[450,180],35,'Grey')
    canvas.draw_text('How To Play', [308,185], 20 , 'Black', 'monospace')
    canvas.draw_line([300,220],[450,220],35,'Grey')
    canvas.draw_text('High Scores', [308,225], 20 , 'Black', 'monospace')
    """
    if TITLE_SCREEN:
        if (320<pos[0]<470) and (123<pos[1]<157):           
            TUTORIAL = False
            TITLE_SCREEN = False
            HOW_TO_PLAY = False  
            HIGH_SCORES = False
            new_game()
        elif (320<pos[0]<470) and (163<pos[1]<197):
            TUTORIAL = True
            TITLE_SCREEN = False
            HOW_TO_PLAY = False  
            HIGH_SCORES = False
            new_game()
        elif (320<pos[0]<470) and (203<pos[1]<237):   
            TITLE_SCREEN = False
            HOW_TO_PLAY = True
        elif (320<pos[0]<470) and (243<pos[1]<277):   
            TITLE_SCREEN = False
            HIGH_SCORES = True
            
    elif HOW_TO_PLAY:
        HOW_TO_PLAY = False
        TITLE_SCREEN = True
        
    elif HIGH_SCORES:
        HIGH_SCORES = False
        TITLE_SCREEN = True
        
    
    
### LIMB CLASS ###
class Limb:
    """ 
    Holds joint position, angle from downwards vertical neglecting angle about cm, and limb length.
    """
    def __init__(self,pos1,angle,length):
        self.pos1 = pos1 
        self.angle = angle
        self.length = length
        self.pos2 = self.get_end()
        
    def draw(self,canvas):
        canvas.draw_line(self.pos1,self.pos2,2,"White")
         
    def get_pos1(self):
        return self.pos1
    
    def get_pos2(self):
        return self.pos2
    
    def get_angle(self):
        return self.angle
        
    def get_length(self):
        return self.length
    
    def get_end(self):
        limb_unit_vector = angle_to_vector(self.angle)
        limb_end = [0,0]
        for i in xrange(2):
            limb_end[i] = self.pos1[i] + self.length * limb_unit_vector[i]
        return limb_end

    def set_pos1(self, new_pos):
        self.pos1 = new_pos
        
    def set_pos2(self, new_pos):
        self.pos2 = new_pos

# initialize frame
# E left, R right, Space jump, Y arch, U hollow, I tuck, O extend
frame = simplegui.create_frame("Vector Gymnastics", WIDTH, HEIGHT) 


# register handlers
frame.set_draw_handler(draw)

frame.set_keydown_handler(key_down)
frame.set_keyup_handler(key_up)

frame.set_mouseclick_handler(mouse_handler)
# get things rolling
frame.start()

