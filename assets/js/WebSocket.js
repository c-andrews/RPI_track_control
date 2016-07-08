

var WebSocketManager = function() {
	this._connect();
}


WebSocketManager.prototype = {


	_ws: null,
	_url: "ws://raspberrypi.local:8888/ws",
	// _url: "ws://192.168.0.42:8888/ws",
	// _url: "ws://localhost:8888/ws",
	_error: null,
	_closed: null,
	_connected: null,
	_tries: 0,
	


	_connect: function() {

		try {
			this._ws = new WebSocket( this._url );
		} catch(e) {}
		
		if ( this._ws )
		{
			this._ws.onerror = this._onWSError.bind( this );
			this._ws.onopen = this._onWSOpen.bind( this );
			this._ws.onclose = this._onWSClosed.bind( this );
			this._ws.onmessage = this._onWSMessage.bind( this );	
		}
	},



	_reconnect: function() {

		this._tries ++;

		if ( this._tries > 4 ) return;

		if ( this._ws )
		{
			this._ws.onerror = null;
			this._ws.onopen = null;
			this._ws.onclose = null;
			this._ws.onmessage = null;
			this._ws = null;
		}

		this._connect();
	},



	_onWSOpen: function( e )
	{
		console.log( "[WebSocket] OPEN" );

		var conn_status = document.getElementById('conn_text');
			conn_status.innerHTML = "Connected!"
			// conn_status.classList += " ";/

		$("#conn_text").addClass( "connected" );
		$("#conn_text").removeClass( "warning" );

		this._connected = true;
	},



	_onWSClosed: function( e )
	{
		console.log( "[WebSocket] CLOSED" );

		var conn_status = document.getElementById('conn_text');
			conn_status.innerHTML = "Disonnected!"
			// conn_status.classList += " warning";

		$("#conn_text").removeClass( "connected" );
		$("#conn_text").addClass( "warning" );

		this._closed = true;

		this._reconnect();
	},



	_onWSError: function( e )
	{
		console.log( "[WebSocket] ERROR:", e );
		this._error = true;
	},



	_onWSMessage: function( e )
	{
		console.log( "[WebSocket] MESSAGE:", e.data );
		var data = e.data.split( ";" );
	},



	send: function( data )
	{
		console.log( "[WebSocket] SENDING:", data );

		if ( !this._connected || this._error || this._closed ) return;

		this._ws.send( data );
	}


}