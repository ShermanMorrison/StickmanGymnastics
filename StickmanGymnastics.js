
// var imported = document.createElement('script');
// imported.src = '../StickmanGymnasticsHeader.js';
// document.getElementsByTagName('script')[0].parentNode.appendChild(script);


///////////////////
//event listeners//
///////////////////
window.addEventListener("keydown", function(event){
	keysDown[event.keyCode] = true;
});

window.addEventListener("keyup", function(event){
	delete keysDown[event.keyCode];
});


///////////
//objects//
///////////
var man = new Man();



///////////////
//main script//
///////////////

window.onload = function(){
	document.body.appendChild(canvas);
	animate(step);
}

var step = function(){
	// do all updates and rendering
	update();
	render();
	animate(step);
}

var update = function(){
// 	STANDING = 0;
// ARCHED = 1;
// HOLLOW = 2;
// TUCKED = 3;
// LONG = 4;
// RUNNING = 5;

	man.set_state(STANDING);

	for (var key in keysDown){
		if (key == 87){
			man.set_state(LONG);
		}
		else if (key == 69){
			man.set_state(ARCHED);
		}
		else if (key == 82){
			man.set_state(HOLLOW);
		}	
		else if (key == 84){
			man.set_state(TUCKED);
		}
		if (key == 37){
			man.set_left();
		}
		if (key == 39){
			man.set_right();
		}

	}

	//IN_GAME:


	if (!man.JUMP){
		man.ONGROUND = man.is_on_ground();
	}

	man.conform_rigid_man(); //get new body angles
	man.make_limb_list(); //update limbList


	if (!man.ONGROUND){
		man.update_center_of_mass(g);
		//get moment about cm
	}

	if (!man.is_on_ground()){

	}
	else{

	}
}

var render = function(){
	context.clearRect(0, 0, canvas.width, canvas.height);
	man.draw();
}



