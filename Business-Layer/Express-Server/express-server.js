const express = require("express");
const path = require("path");
const cors = require("cors");

const app = express();
app.use(express.static(path.join(__dirname, "../../Presentation-Layer/public")));
app.use(cors());
app.use(express.json());

app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "../../Presentation-Layer/public/index.html"));
})

app.post("/api/forward", async (req, res) => {
    try{
        const response = await fetch("http://n8n:5678/webhook/chat-gemini", {
            method: "POST",
            headers:{
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: req.body.message
            })
        });
        const data = await response.json();
        res.json(data);
    }catch(error){
        res.status(500).json({ error: error.message });
    }
})

app.listen(80, () => console.log("Server running on http://localhost:80"))