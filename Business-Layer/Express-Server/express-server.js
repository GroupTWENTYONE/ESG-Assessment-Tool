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

const { connectDB } = require("./db");

function extractCompanyFromPrompt(prompt) {
    const match = prompt.match(/(?:of|for)\s+([A-Za-z0-9 .,&-]+?)(?:\s+and\b|[?.]|$)/i);
    return match ? match[1].trim() : null;
}

app.post("/api/forward", async (req, res) => {
    const userPrompt = req.body.prompt;

  try{
    const db = await connectDB();
    const companyName = extractCompanyFromPrompt(userPrompt);
    const companies = await db.collection("companies").find({ name: new RegExp(companyName.trim(), "i") }).toArray();
    const context = companies.map(c => `Company: ${c.name}, ESG Score: ${c.spglobal_esg_score}`).join("\n");
    const finalPrompt = `
        You are an ESG expert.
        Use the following company data to answer the question.
        But never mention that data has been provided to you.

        DATA:
        ${context}

        QUESTION:
        ${userPrompt}
    `;

    const ollamaResponse = await fetch("http://ollama:11434/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            model: "llama3-groq-tool-use:8b",
            prompt: finalPrompt,
            stream: false
      })
    });

    const data = await ollamaResponse.json();
    res.json(data);
  }catch(err){
    console.error(err);
    res.status(500).json({ error: err.message });
  }
});

app.listen(80, () => console.log("Server running on http://localhost:80"))