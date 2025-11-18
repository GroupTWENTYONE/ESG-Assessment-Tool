function addMessage(text, side){
    var message = document.createElement("div");
    if(side === "user"){
        message.className = "message user";
        message.textContent = text;
    }else{
        message.className = "message machine";
        message.textContent = text;
    }
    document.getElementById("chat-messages").appendChild(message);
}

setTimeout(function(){
    var chat = document.getElementById("chat-messages");
    chat.firstElementChild?.remove();

    addMessage("Hello, how can I help you?", "machine");
}, 2000);

function machineReply(){
    setTimeout(function(){ 
        addMessage("Currently I cannot give you the answer as this functionality has not been implemented yet.", "machine")
    }, 2000);
}

async function send(){
    var userMessage = document.getElementById("user-message").value;
    if(userMessage === "")
        return;
    
    try{
        addMessage(userMessage, "user");
        const response = await fetch("/api/forward", {
            method: "POST",
            headers:{
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: userMessage
            })
        });

        const data = await response.json();
        addMessage(data[0].output, "machine");
    }catch(error){
        addMessage(error, "machine");
    }

    document.getElementById("user-message").value = "";
}