var http = require('http');
var fs = require('fs');
var querystring = require('querystring');
const { URLSearchParams } = require('url');
var tags = "try again!";

http.createServer(function (request, response) {


    response.writeHead(200, {
        'Content-Type':'text/plain',
        'Access-Control-Allow-Credentials':true,
        'Access-Control-Allow-Origin':'*'
    });

    var text = "";
    request.on('data', function(chunk){
        text+=chunk.toString();
    });

    request.on('end',function(){
        var childProcess = require('child_process');
        var process = childProcess.spawn('python', ['main.py', text]);
        process.stdout.on('data', function(data){
            response.end(data);
        });
        process.on('error',function(){
            console.log("error!");
        });
        text="";
    });

    

}).listen(8888);