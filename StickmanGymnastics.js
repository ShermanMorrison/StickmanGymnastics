
// var imported = document.createElement('script');
// imported.src = '../StickmanGymnasticsHeader.js';
// document.getElementsByTagName('script')[0].parentNode.appendChild(script);


///////////////////
//event listeners//
///////////////////



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


	//IN_GAME:

	//if (!JUMP){
	//	ON_GROUND = man.is_on_ground();
	//}
	man.update_center_of_mass(g);

}

var render = function(){
	context.clearRect(0, 0, canvas.width, canvas.height);
	man.draw();
}



