

var SwitchController = function() {

	this._init();
}

SwitchController.prototype = {
	

	// ws.send(  "switch" + ";" + switchID );

	_buttons: null,


	_init: function() {
		
		this._buttons = $( ".switch_button" );

		this._buttons.on( "click", { self:this }, this._onButtonClick );
	},


	_onButtonClick : function( e ) {

		var self = e.data.self;

		var $target = $( e.currentTarget );
		var isActive = $target.hasClass( "active" );
		var id = parseInt( $target.data( "id" ));
		var on = parseInt( $target.data( "on" ));
		var off = parseInt( $target.data( "off" ));

		var $point = $( "#point-"+id );
			$point.removeClass( "active" );

		console.log( "[SwitchController] BUTTON:", id, "IS ACTIVE:", isActive, "SWITCH:", ( isActive?off:on ));

		if ( isActive == true )
		{
			$target.removeClass( "active" );
			
			self._moveToFront( $point, ".closed" );
			// self._deactivate( id );
			self._deactivate( off );
		}
		else
		{
			$target.addClass( "active" );
			$point.addClass( "active" );

			self._moveToFront( $point, ".open" );
			// self._activate( id );
			self._activate( on );
		}


		$( ".switch_button" ).prop( 'disabled', true );

		setTimeout( function(){
			$( ".switch_button" ).prop('disabled', false);
		}, 250 )
	},


	_activate: function( id ) {
		ws.send(  "switch" + ";" + id.toString() + ";" + "1");
	},


	_deactivate: function( id ) {
		ws.send(  "switch" + ";" + id.toString() + ";" + "0" );
	},


	_moveToFront: function( $point, className ) {

		var $target = $point.find( className ).first();
		$target.appendTo( $point );
	}



}