# teleinfo-sender


This script polls /dev/ttyUSB0 and send the frames to a [teleinfo-receiver]  and/or using UDP (unicast or broadcast) for [teleinfo-udp2influx]

If the parameter starts with http, it's treated as [teleinfo-receiver], if not, UDP ip:port couple

exmaple:

    ./send_teleinfo.py http://192.168.3.5/teleinfo/post.php 192.168.3.255:2101
    
    
 ### TODO
 
 - Rewrite the script (currently working but kludgy)
    
[teleinfo-receiver]: https://github.com/babs/teleinfo-receiver
[teleinfo-udp2influx]: https://github.com/babs/teleinfo-udp2influx
