$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':5000');
    var numbers_received = [];

    //receive details from server
    socket.on('abc', function(msg) {
        console.log("Received message: " + msg.msg);
        numbers_received.push(msg.msg);
        numbers_string = '';
        for (var i = 0; i < numbers_received.length; i++){
            numbers_string = numbers_string + '<p>' + numbers_received[i].toString() + '</p>';
        }
        $('#log').html(numbers_string);
    });

});
