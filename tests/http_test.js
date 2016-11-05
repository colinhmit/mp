var http = require('http');

var options = {
  host: 'localhost',
  port: 4808,
  path: '/stream/yoda'
};


http.get(options, function(resp){
      resp.on('data', function(chunk){
        console.log(chunk);
      });
    }).on("error", function(e){
      console.log("Got error: " + e.message);
    });

sleep(0.1);

http.get(options, function(resp){
      resp.on('data', function(chunk){
        console.log(chunk);
      });
    }).on("error", function(e){
      console.log("Got error: " + e.message);
    });

sleep(0.1);
http.get(options, function(resp){
      resp.on('data', function(chunk){
        console.log(chunk);
      });
    }).on("error", function(e){
      console.log("Got error: " + e.message);
    });

sleep(0.1);
http.get(options, function(resp){
      resp.on('data', function(chunk){
        console.log(chunk);
      });
    }).on("error", function(e){
      console.log("Got error: " + e.message);
    });

sleep(0.1);
http.get(options, function(resp){
      resp.on('data', function(chunk){
        console.log(chunk);
      });
    }).on("error", function(e){
      console.log("Got error: " + e.message);
    });

sleep(0.1);
http.get(options, function(resp){
      resp.on('data', function(chunk){
        console.log(chunk);
      });
    }).on("error", function(e){
      console.log("Got error: " + e.message);
    });

sleep(0.1);
http.get(options, function(resp){
      resp.on('data', function(chunk){
        console.log(chunk);
      });
    }).on("error", function(e){
      console.log("Got error: " + e.message);
    });

sleep(0.1);
http.get(options, function(resp){
      resp.on('data', function(chunk){
        console.log(chunk);
      });
    }).on("error", function(e){
      console.log("Got error: " + e.message);
    });

sleep(0.1);


function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
