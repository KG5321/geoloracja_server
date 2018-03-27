$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':5000');
    var numbers_received = [];

    //receive details from server
    socket.on('abc', function(msg) {
        console.log("Received message: " + msg);
        //maintain a list of ten numbers
        if (numbers_received.length >= 10){
            numbers_received.shift()
        }
        numbers_received.push(msg);
        numbers_string = '';
        for (var i = 0; i < numbers_received.length; i++){
            numbers_string = numbers_string + '<p>' + numbers_received[i].toString() + '</p>';
        }
        $('#log').html(numbers_string);
    });

});
