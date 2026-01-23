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
    
    document.getElementById("user-message").value = "";

    try{
        addMessage(userMessage, "user");
        const response = await fetch("api/forward", {
            method: "POST",
            headers:{
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "model": "llama3",
                "prompt": userMessage,
                "stream": false
            })
        });

        if(!response.ok){
            // Read the error from the API for better debugging
            const errorText = await response.text(); 
            throw new Error(`API Request Failed: ${response.status} - ${errorText.substring(0, 100)}...`);
        }

        const data = await response.json();
        console.log(data);
        // **CRITICAL: Use data.response to get the message from Ollama**
        if(data.response){
            addMessage(data.response, "machine");
        }else{
            addMessage("Error: Could not find 'response' field in API data.", "machine");
        }
    }catch(error){
        alert(error.message); // can't access property "output", data[0] is undefined
    }
}