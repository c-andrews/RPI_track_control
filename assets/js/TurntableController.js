

var TurntableController = function() {
	this._init();
}


TurntableController.prototype = {

	angle: null,
	motor_step: 0,
	halfstep: 0,
	step: 0,
	max_steps: 0,
	curr_angle: 0,
	turntable_radius: 0,
	speed: 0,
	message: null,
	trans_x: 150,
	trans_y: 150,
	in_transition: 0,
	$turningTrack: null,
	template: null,


	_init : function() {

		console.log( "INIT" );

		this.angle = new Array();
		this.max_steps = 200;
		this.motor_step = 360 / 200;
		this.halfstep = 2;
		this.step = this.motor_step / this.halfstep;
		this.curr_angle = 0;
		this.turntable_radius = 246;
		this.speed = 5;
		this.message = { "speed": this.speed, "angle": this.curr_angle }
		this.in_transition = 0;
		this.curr_angle = 0;

		this.$turningTrack = $( "#turning_track" );


		var turningTrack_w = 66;
		var turningTrack_h = 481;

		this.trans_x = turningTrack_w * 0.5;
		this.trans_y = turningTrack_h * 0.5;
		
		console.log( this.trans_x );
		console.log( this.trans_y );


		this.template = '<svg class="track" xmlns="http://www.w3.org/2000/svg" width="40px" height="78px" viewBox="0 0 40 78"><rect x="0" y="7" width="40" height="4"></rect><rect x="0" y="17" width="40" height="4"></rect><rect x="0" y="27" width="40" height="4"></rect><rect x="0" y="37" width="40" height="4"></rect><rect x="0" y="47" width="40" height="4"></rect><rect x="0" y="57" width="40" height="4"></rect><rect x="0" y="67" width="40" height="4"></rect><rect x="6" y="0" width="2" height="78"></rect><rect x="32" y="0" width="2" height="78"></rect></svg>'


		var angles = [ 
			0,
			12,
			24,
			180,
			348,
			336,
			// 20.699999999999996,
			// 36.89999999999997,
			// 275.40000000000066,
			// 284.40000000000043
		]


		this.setConnectingTracks( angles );

		// for ( i=0; i<360; i=i+this.step )
		// {
		// 	this.angle.push( i );
		// }

		// console.log( this.angle );


		// this._update( 0.005 );
	},



	setConnectingTracks: function( angles ) {

		var total = angles.length;
		var centerX = 0//1024 * 0.5;
		var centerY = 0//768 * 0.5;
		var $elements = $( ".connecting_track" );

		// $elements.hide();

		for ( var i=0; i<total; i++ )
		{
			var x = centerX + this.turntable_radius * Math.cos(( angles[i]+0 )*Math.PI/180 );
			var y = centerY + this.turntable_radius * Math.sin(( angles[i]+0 )*Math.PI/180 );
			var a = ( Math.atan2( x, y ) * 180 / Math.PI ) - 90;

			// console.log( "POSITION:", x, y, a );

			// var $element = $( "<div id='connecting_track_"+i+"' class='connecting_track'><img class='track' src='assets/images/connecting_track.svg' width='40px' height='74px' /></div>" );
			var $element = $( "<div id='connecting_track_"+i+"' class='connecting_track'>"+ this.template +"</div>" );

			$element.attr( "data-rotation", angles[i] )



			$( "#connecting_track_container " ).append( $element );

			TweenLite.set( "#connecting_track_"+i, { top:x, left:y });
			TweenLite.set( "#connecting_track_"+i+" .track", { rotation:a, transformOrigin:"20px 0" });
			
		}

		$( ".connecting_track .track" ).on( "mouseover touchstart", { self:this }, this.onMouseOver );
		$( ".connecting_track .track" ).on( "mouseout touchend", { self:this }, this.onMouseOut );
		$( ".connecting_track .track" ).on( "click", { self:this }, this.onClick );
	},



	onMouseOver: function( e ) {

		var self = e.data.self
		if ( self.in_transition == 1 ) return;

		var $target = $( e.currentTarget );
		TweenLite.to( $target, 0.25, { fill:"#DDD" });
	},



	onMouseOut: function( e ) {

		var self = e.data.self
		if ( self.in_transition == 1 ) return;

		var $target = $( e.currentTarget );
		TweenLite.to( $target, 0.25, { fill:"#777" });
	},



	onClick: function( e ) {

		var self = e.data.self;
		var $target = $( e.currentTarget );
		var $parent = $target.parent();

		var angle = parseInt( $parent.attr( "data-rotation" ));

		if ( self.in_transition == 0 )
		{
			console.log( "ROTATE TO:", angle );

			$(".connecting_track").removeClass( "active" );

			$parent.addClass( "active" );
			
			self.rotateElement( angle );
		}
	},



	rotateElement: function ( angle ) {
		
		if ( this.in_transition == 0 ) 
		{

			this.in_transition = 1;

			var current = this.curr_angle;

			if ( !current ) current = 0;


			var degrees = Math.round( angle / this.step ) * this.step;

			console.log( "DEGREES:", degrees );

			if ( degrees <= 0 )
			{
				this.curr_angle = Math.abs( degrees );
			}
			else
			{
				this.curr_angle = 360 - degrees;
			}

			console.log( "CURRENT ANGLE:", current );
			console.log( "NEW ANGLE:", this.curr_angle );

			var dist = Math.abs( current - this.curr_angle );

			console.log( "DIST:", dist );

			if ( dist > 180 ) dist = 360 - dist;

			console.log( "DIST:", dist );

			var duration = Math.abs(( dist / this.speed ) / this.step );

			console.log( "TRANS DURATION:", duration );


			TweenMax.to( this.$turningTrack, duration, { shortRotation:this.curr_angle, transformOrigin:""+this.trans_x+"px "+this.trans_y+"px", ease:Linear.easeNone, onComplete:this.transitionComplete, onCompleteParams:[this] });


			this.message.angle = this.curr_angle;

			ws.send(  "turntable" + ";" + this.message.angle.toString() + ";" + this.message.speed.toString());
		}
	},



	transitionComplete: function( self ) {

		self.in_transition = 0;
	},


}