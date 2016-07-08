
var ws;
var turntableController;
var switchController;


// left: 37, up: 38, right: 39, down: 40,
// spacebar: 32, pageup: 33, pagedown: 34, end: 35, home: 36
var keys = {37: 1, 38: 1, 39: 1, 40: 1};


function preventDefault(e) {
	e = e || window.event;
	if (e.preventDefault) e.preventDefault();
	e.returnValue = false;  
}

function preventDefaultForScrollKeys(e) {
	if ( keys[ e.keyCode ]) {
		preventDefault(e);
		return false;
	}
}



$(document).ready( function () {
	
	// Create the Web Socket
	ws = new WebSocketManager();

	// Create the controllers
	switchController = new SwitchController();
	turntableController = new TurntableController();


	$( "#power_btn" ).on( "click", function(){
		ws.send( "shutdown;0" );
	})

	$( "#update_btn" ).on( "click", function(){
		ws.send( "update;0" );
	})


	// PREVENT PAGE SCROLL
	if (window.addEventListener) // older FF
    	window.addEventListener('DOMMouseScroll', preventDefault, false);
	
	window.onwheel 		= preventDefault; // modern standard
	window.onmousewheel = document.onmousewheel = preventDefault; // older browsers, IE
	window.ontouchmove  = preventDefault; // mobile
	document.onkeydown  = preventDefaultForScrollKeys;

});