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
var JUMP, ON_GROUND = false;

xo = 300;
yo = 450;
rad = Math.PI/180;
g = [0,5];
headWeight = 80;
dt = .2;

ground = height - 20;

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
	//this.pos1 = [0,0]; // x,y position of one end
	this.pos1 = pos1;
	this.angle = angle;
	this.len = length;
	var limbUnitVector = angle_to_vector(angle);
	this.pos2 = [0,0];
	//alert("pos2 = " + this.pos2);
	for (var i = 0; i < 2; i++){
		this.pos2[i] = pos1[i] + length * limbUnitVector[i];
	}
	//alert("pos2 = " + this.pos2);
	//document.write("limbEnd = " + limbEnd);

	// this.pos2[0] = limbEnd[0];
	// this.pos2[1] = limbEnd[1];
	//this.pos2 = this.get_end();
	//this.pos2 = [100,100];
	

}
Limb.prototype.draw = function(){
	//var ctx=canvas.getContext("2d");
	context.beginPath();
	//document.write("pos1 = " + this.pos1);
	//document.write("pos2 = " + this.pos2);	
	context.moveTo(this.pos1[0],this.pos1[1]);
	context.lineTo(this.pos2[0],this.pos2[1]);
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
	var that = this;
	this.neckBase = [xo,yo];
	this.limbList = [];
	this.limbAngles = [-30*rad,-45*rad,10*rad,10*rad,35*rad,3*rad,10*rad,-25*rad,-5*rad];
	this.limbLengths = [36,22,22,18,18,24,24,30,30];
	//alert("rad = " + rad);
	//alert("this.limbAngles[0] = " + this.limbAngles[0]);


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

Man.prototype.is_on_ground = function(){
	for (var limb in this.limbList) {
		if (limb.length >= 2){
			if (limb.pos2[1] > ground) {  // TODO!! IMPLEMENT get_pos2 & initialize ground !!
				return True;
			}
		}
	}

	head_pos = [this.limbList[0].get_pos1()[0] - 0.2 * (this.limbList[0].get_pos2()[0] - 
					this.limbList[0].get_pos1()[0]), 
				this.limbList[0].get_pos1()[1] - .2*(this.limbList[0].get_pos2()[1] - 
					this.limbList[0].get_pos1()[1]) ];

	if (head_pos[1] > ground) {
		return true;
	}
	return false;
}
Man.prototype.draw = function(){
	//draw head
 	headPos = [this.limbList[0].get_pos1()[0] - .2*(this.limbList[0].get_pos2()[0] - this.limbList[0].get_pos1()[0])  , this.limbList[0].get_pos1()[1] - .2*(this.limbList[0].get_pos2()[1] - this.limbList[0].get_pos1()[1])]
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
		 	this.limbList[limb].draw();
		 }
	}
}