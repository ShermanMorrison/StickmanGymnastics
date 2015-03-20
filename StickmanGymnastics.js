
// var imported = document.createElement('script');
// imported.src = '../StickmanGymnasticsHeader.js';
// document.getElementsByTagName('script')[0].parentNode.appendChild(script);

///////////
//objects//
///////////
var man = new Man();

///////////////////
//event listeners//
///////////////////
window.addEventListener("keydown", function(event){
	keysDown[event.keyCode] = true;
});

window.addEventListener("keyup", function(event){
    //if ((event.keyCode == 37) || (event.keyCode == 39)){
    //    man.stop_running();
    //}
	delete keysDown[event.keyCode];
});






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
            if (Object.keys(keysDown).length == 1) {
                man.set_state(RUNNING);
            }
            man.set_left();
		}
		if (key == 39){
            if (Object.keys(keysDown).length == 1) {
                man.set_state(RUNNING);
            }
            man.set_right();
		}
        if (key == 32){
            man.set_jump();
        }

	}

	//IN_GAME:


    //if (!man.JUMP){
	man.ONGROUND = man.is_on_ground();
	//}
	//var wasOnGround = man.ONGROUND;

	man.conform_rigid_man(); //get new body angles
	man.update_limb_angles(); //update body's configuration, but still upright

	//if (wasOnGround){
	//	man.ONGROUND = wasOnGround;
	//}
	//stickman is in the air
	if (!man.ONGROUND){
        man.JUMP = false;
		man.update_diff_by_accel(g);
		// CASE 1 : He is still in the air
		
		man.rotate(man.get_location()); //rotate man

		// CASE 2 : He has just landed
	}

	//stickman is on the ground
	else{	

		if (!(man.STATE == ARCHED)){
			// reduce stickman's rotational momentum by a lot
		}
		else {
			//reduce stickman's rotation momentum by a little
		}


		// CASE 1 : JUMP
        if (man.JUMP){
            man.jump();
            man.update_diff_by_accel(g);
        }
		// CASE 2 : RUN

		// CASE Else : Rotate stickman about ground fulcrum
		//determine fulcrum
		//put him back on the ground on the fulcrum
		//update fulcrum (it may have changed after conforming rigid man) ??? When to do conform_rigid_man()?

	}
    man.update_diff_by_cm(); //update cm based on body position
    if (man.fulcrumIndex == 10){
        var head_pos = man.get_head_pos();
        if (man.get_center_of_mass()[0] < head_pos[0]) {
            man.rotate_rigid_man([head_pos[0] + man.diff[0], head_pos[1] + man.diff[1]], -.03);
        }
        else{
            man.rotate_rigid_man([head_pos[0] + man.diff[0], head_pos[1] + man.diff[1]], .03);
        }
    }
}

var render = function(){
	context.clearRect(0, 0, canvas.width, canvas.height);
	man.draw();
    draw_ground();
}



