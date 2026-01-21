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
    const clientMessage = req.body.prompt; 

    try{
        const response = await fetch("http://n8n:5678/webhook/ESG-chatbot", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: clientMessage })
        });

        // 1. First, check if the response status is OK (e.g., 200)
        if(!response.ok){
            console.error(`External API returned status: ${response.status}`);
            const errorText = await response.text();
            console.error("External API Body:", errorText);
            throw new Error(`External API Error: Status ${response.status}`);
        }

        // 2. Clone the response so we can safely read it twice
        const responseClone = response.clone();
        
        try{
            // Attempt to parse as JSON (what you originally wanted)
            const data = await response.json();
            res.json(data);
        }catch(jsonError){
            // 3. If JSON parsing fails, read the raw text for debugging
            const rawText = await responseClone.text();
            console.error("JSON PARSE FAILED. Raw Response from N8N:", rawText);
            // Re-throw the error or send a descriptive 500
            throw new Error("Could not parse JSON response from N8N. Check server console for raw text.");
        }

    }catch(error){
        console.error("Final PROXY CRASH:", error.message);
        res.status(500).json({ error: error.message });
    }
});

app.listen(80, () => console.log("Server running on http://localhost:80"))