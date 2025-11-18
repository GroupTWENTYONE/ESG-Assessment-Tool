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

    addMessage(userMessage, "user");
    document.getElementById("user-message").value = "";
    
    //machineReply();
    
    try{
        const response = await fetch("https://postman-echo.com/get?msg=Hi", { // URL HIER ANPASSEN
            method: "GET",
            headers: {
                "Content-Type": "application/json"
            }
        });

        const data = await response.json();
        console.log(data);
        addMessage(data, "machine");
    }catch(error){
        addMessage(error, "machine");
    }
    /**/
}