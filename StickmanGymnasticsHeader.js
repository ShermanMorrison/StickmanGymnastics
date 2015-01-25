var animate = window.requestAnimationFrame || 
			window.webkitRequestAnimationFrame ||
			window.mozRequestAnimationFrame ||
			function(callback) { window.setTimeout(callback, 1000/60) };

///////////////
//global vars//
///////////////

//canvas
var canvas = document.createElement('canvas');
var width = 600;
var height = 800;
canvas.width = width;
canvas.height = height;
var context = canvas.getContext('2d');

//game vars
var keysDown = {};


xo = 300;
yo = 450;
rad = Math.PI/180;
g = [0,5];
headWeight = 80;
dt = .2;

ground = height - 20;

STANDING = '';
LONG = 'w';
ARCHED = 'e';
HOLLOW = 'r';
TUCKED = 't';
RUNNING = 'arrow';


////////////////////
//global functions//
////////////////////

var angle_to_vector = function(angle){
	//alert(angle);
	//alert(Math.sin(angle) + ", " + Math.cos(angle));
	return [Math.sin(angle), Math.cos(angle)]; // angle is from downwards vertical
}


/////////////////////
//class definitions//
/////////////////////
function Limb(pos1,angle,length){
	this.pos1 = pos1;
	this.angle = angle;
	this.len = length;
	var limbUnitVector = angle_to_vector(angle);
	this.pos2 = [0,0];
	//alert("pos2 = " + this.pos2);
	for (var i = 0; i < 2; i++){
		this.pos2[i] = pos1[i] + length * limbUnitVector[i];
	}
}
Limb.prototype.draw = function(offset){
	//var ctx=canvas.getContext("2d");
	context.beginPath();
	//document.write("pos1 = " + this.pos1);
	//document.write("pos2 = " + this.pos2);	
	context.moveTo(this.pos1[0] + offset[0], this.pos1[1] + offset[1]);
	context.lineTo(this.pos2[0] + offset[0], this.pos2[1] + offset[1]);
	context.stroke();
}
Limb.prototype.get_pos1 = function(){
	return this.pos1;
}
Limb.prototype.get_pos2 = function(){
	return this.pos2;
}
Limb.prototype.get_angle = function(){
	return this.angle;
}
Limb.prototype.get_length = function(){
	return this.length;
}
Limb.prototype.get_end = function(){
	var limbUnitVector = angle_to_vector(self.angle);
	var limbEnd = [0,0];
	for (var i = 0; i < 2; i++){
		limbEnd[i] = this.pos1[i] + this.length * limbUnitVector[i];
	}
	//document.write("limbEnd = " + limbEnd);
	return limbEnd;
}
Limb.prototype.set_pos1 = function(newPos){
	this.pos1 = newPos;
}
Limb.prototype.set_pos2 = function(newPos){
	this.pos2 = newPos;
}

function Man(){
	this.JUMP, this.ONGROUND = false;
	this.RIGHT = true;
	this.STATE = STANDING;
	this.net_body_change = 0;
	this.neckBase = [xo,yo];
	this.limbList = [];
	this.limbAngles = [-30*rad,-45*rad,10*rad,10*rad,35*rad,3*rad,10*rad,-25*rad,-5*rad];
	this.limbLengths = [36,22,22,18,18,24,24,30,30];
	//alert("rad = " + rad);
	//alert("this.limbAngles[0] = " + this.limbAngles[0]);

	this.make_limb_list();

	this.origCenterOfMass = this.get_center_of_mass();
	this.centerOfMass = this.get_center_of_mass(); //this will be updated as stickman moves

	this.vel = [0,0];
	this.diff = [0,0];
}
Man.prototype.make_limb_list = function(){
	this.limbList = [];
	this.limbList.push(new Limb(this.neckBase, this.limbAngles[0], this.limbLengths[0])); //torso
	this.limbList.push(new Limb(this.neckBase, this.limbAngles[1], this.limbLengths[1])); //left upper arm
	this.limbList.push(new Limb(this.neckBase, this.limbAngles[2], this.limbLengths[2])); //right upper arm

	//left lower arm
	this.limbList.push(new Limb([xo + angle_to_vector(this.limbAngles[1])[0] * this.limbLengths[1], yo + angle_to_vector(this.limbAngles[1])[1] * this.limbLengths[1]],this.limbAngles[3], this.limbLengths[3])); //left lower arm
	//right lower arm
	this.limbList.push(new Limb([xo + angle_to_vector(this.limbAngles[2])[0] * this.limbLengths[2], yo + angle_to_vector(this.limbAngles[2])[1] * this.limbLengths[2]],this.limbAngles[4], this.limbLengths[4])); //left lower arm
	
    xc = this.neckBase[0] + angle_to_vector(this.limbAngles[0])[0] * this.limbLengths[0]; 
    yc = this.neckBase[1] + angle_to_vector(this.limbAngles[0])[1] * this.limbLengths[0];

	//left upper leg
	this.limbList.push(new Limb([xc,yc],this.limbAngles[5],this.limbLengths[5]));
	//right upper leg
	this.limbList.push(new Limb([xc,yc],this.limbAngles[6],this.limbLengths[6]));	

	//left lower leg
	this.limbList.push(new Limb([xc + angle_to_vector(this.limbAngles[5])[0] * this.limbLengths[5],yc + angle_to_vector(this.limbAngles[5])[1] * this.limbLengths[5]],this.limbAngles[7],this.limbLengths[7]));
	//right lower leg
	this.limbList.push(new Limb([xc + angle_to_vector(this.limbAngles[6])[0] * this.limbLengths[6],yc + angle_to_vector(this.limbAngles[6])[1] * this.limbLengths[6]],this.limbAngles[8],this.limbLengths[8]));	

}
Man.prototype.draw = function(){
	//draw head
 	headPos = [this.diff[0] + this.limbList[0].get_pos1()[0] - .2*(this.limbList[0].get_pos2()[0] - this.limbList[0].get_pos1()[0]), 
 				this.diff[1] + this.limbList[0].get_pos1()[1] - .2*(this.limbList[0].get_pos2()[1] - this.limbList[0].get_pos1()[1])]
 	context.beginPath();
	context.arc(headPos[0], headPos[1], 8, 2*Math.PI, false);
	context.fillStyle = "#000000";
	context.fill();
	//draw limbs
	for (var limb in this.limbList) {
		//alert("hi");
		//document.write("limblist.length = " + this.limbList.length);
		//document.write("this.limblist[limb] = " + this.limbList[limb]);
		 if (this.limbList[limb] != null){
		 	this.limbList[limb].draw(this.diff);
		 }
	}
}
Man.prototype.get_head_pos = function(){
	return [this.limbList[0].get_pos1()[0] - 0.2 * (this.limbList[0].get_pos2()[0] - 
					this.limbList[0].get_pos1()[0]), 
				this.limbList[0].get_pos1()[1] - .2*(this.limbList[0].get_pos2()[1] - 
					this.limbList[0].get_pos1()[1]) ];
}
Man.prototype.get_center_of_mass = function(){
	xCenters = [];
    yCenters = [];
    xcm = 0;
    ycm = 0;
    
    totWeight = 0;

    for (var limbo in this.limbList){
    	limb = this.limbList[limbo];
    	totWeight += limb.len;
    	try{
	    	xCenters.push(limb.get_pos1()[0] + limb.get_pos2()[0] * .5);
			yCenters.push(limb.get_pos1()[1] + limb.get_pos2()[1] * .5);
		}
		catch(err){
			document.write("limb in limbList has l1 = " + this.limbList[0] + " ");
		}
    }

    //add head weight
    try{
    	neckBase = this.limbList[0].get_pos1();
	}
	catch(err){
		document.write("limbList[0].get_pos1() method is null");
	}
    headPos = this.get_head_pos();

    totWeight += headWeight;

    for (var i = 0; i < this.limbList.length; i++){
    	xcm += (xCenters[i] * this.limbLengths[i])/totWeight;
    	ycm += (yCenters[i] * this.limbLengths[i])/totWeight;
    }

    xcm += headPos[0] * headWeight / totWeight;
    ycm += headPos[1] * headWeight / totWeight;

    return [xcm, ycm];
}
Man.prototype.update_center_of_mass = function(accel){
	for (var i = 0; i < 2; i++){
		this.centerOfMass[i] += this.vel[i] * dt + 0.5 * accel[i] * Math.pow(dt, 2);
		this.vel[i] += accel[i] * dt;
	}
	this.diff = [this.centerOfMass[0] - this.origCenterOfMass[0],
				this.centerOfMass[1] - this.origCenterOfMass[1]];
}
Man.prototype.is_on_ground = function(){
	for (var limb in this.limbList){
		if (this.limbList[limb].get_pos2()[1] + this.diff[1] > ground){
			return true;
		}
	}

	if (this.get_head_pos()[1] > ground){
		return true;
	}
	return false;
}
Man.prototype.conform_rigid_man = function(){

	newLimbAngles = [-30*rad,-45*rad,10*rad,10*rad,35*rad,3*rad,10*rad,-25*rad,-5*rad];

	if (this.STATE == STANDING){
		newLimbAngles = [-30*rad,-45*rad,10*rad,10*rad,35*rad,3*rad,10*rad,-25*rad,-5*rad];
	}
	else if (this.STATE == ARCHED){
		newLimbAngles = [10*rad,210*rad,230*rad,190*rad,220*rad,10*rad,50*rad,35*rad,45*rad];
	}
	else if (this.STATE == HOLLOW){
		newLimbAngles = [0*rad,160*rad,110*rad,170*rad,150*rad,-20*rad,30*rad,-30*rad,-35*rad];
	}
	else if (this.STATE == TUCKED){
		newLimbAngles = [-30*rad,-40*rad,-25*rad,35*rad,45*rad,105*rad,120*rad,-20*rad,-30*rad];
	}
	else if (this.STATE == LONG){
		newLimbAngles = [0*rad,-150*rad,150*rad,-170*rad,170*rad,-20*rad,20*rad,-10*rad,10*rad];
	}
	else if (this.STATE == RUNNING){
		//complete..
	}

	//flip sign of angles if facing left
	if (!this.RIGHT){
		for (var i in newLimbAngles){
			newLimbAngles[i] *= -1;
		}
	}

	//update limb angles and calculate netChange
	for (var i in this.limbAngles){
		this.limbAngles[i] += 0.15 * (newLimbAngles[i] - this.limbAngles[i]);
		this.netChange += 3000 * (newLimbAngles[i] - this.limbAngles[i]);
	}
}
Man.prototype.set_state = function(char){
	this.STATE = char;
}
Man.prototype.set_right = function(){
	this.RIGHT = true;
}
Man.prototype.set_left = function(){
	this.RIGHT = false;
}