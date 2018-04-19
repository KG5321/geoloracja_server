$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':80');
    var numbers_received = [];

    //receive details from server
    socket.on('abc', function(msg) {
        console.log("Received message: " + msg.msg);
        numbers_received.push(msg.msg);
        numbers_string = '';
        for (var i = 0; i < numbers_received.length; i++){
            numbers_string = numbers_string +
            '<div class="container-fluid"><div class="row"><div class="alert alert-success" role="alert">' +
            numbers_received[i].toString()+
            '</div></div></div>';
        }
        $('#log').html(numbers_string);
    });

});
