var alive_second = 0;
var heartbeat_rate = 5000;

var myChannel = "Homesafe";


function handleClick(cb){
	if(cb.checked)
	{
		value = true;
	}
	else
	{
		value = false;
	}
	var btnStatus = new Object();
	btnStatus[cb.id] = value;
	var event = new Object();
	event.event = btnStatus;
	console.log("Calling publishUpdate from handleClick");
	publishUpdate(event, myChannel);
}

pubnub = new PubNub({
        publishKey : "pub-c-4c71c151-b075-498f-bfbc-c6f3221ed3b6",
        subscribeKey : "sub-c-12924b4c-2f48-11eb-9713-12bae088af96",
        uuid: "7c6d9aa8-d4d1-4061-bc11-b6f590355178"
    })

pubnub.addListener({
        status: function(statusEvent) {
            if (statusEvent.category === "PNConnectedCategory") {
                console.log("Connected to PubNub");
            }
        },
        message: function(message) {
            var msg = message.message;
            console.log(msg);
            document.getElementById("Motion_id").innerHTML = msg["motion"];
        },
        presence: function(presenceEvent) {
        }
    })

pubnub.subscribe({
        channels: [myChannel]
    });

function publishUpdate(data, channel){
    pubnub.publish({
        channel: channel,
        message: data
        },
        function(status, response){
            if(status.error){
                console.log(status)
            }
            else{
                console.log("Message published with timetoken", response.timetoken)
                }
            }
        );
}


