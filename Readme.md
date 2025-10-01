To Execute the Webserver in remote way within a wifi community

## Find the IP of the Host device 
shell : ipconfig -> ipv4 : Copy it

## Replace the index.html
change : const ws = new WebSocket('ws://192.168.1.5:8080');

to : const ws = new WebSocket('ws://ipv4_address:8080');

## Run the Websocket
$ node server.js

## Create a IP bounded server
$ python -m http.server 8000

## Visit this in browser by connecting to a common wifi
http://ipv4_address:8000/index.html