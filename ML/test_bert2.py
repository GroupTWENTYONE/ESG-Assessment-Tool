import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertModel

# === GPU oder CPU ===
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# === Beispielhafte Firmendaten ===
firm_data = [
    {
        "company_id": "A",
        "texts": [
            "The company is a leader in clean energy.",
            "Strong corporate ethics and transparent governance.",
            "Diversity hiring increased workplace inclusion."
        ],
        "esg_score": 90
    },
    {
        "company_id": "B",
        "texts": [
            "Oil spills and regulatory violations.",
            "Executives involved in bribery scandals.",
            "No diversity programs or worker safety."
        ],
        "esg_score": 20
    },
    {
        "company_id": "C",
        "texts": [
            "Community outreach programs support social causes.",
            "Environmental protection reduced pollution.",
            "Strict data privacy measures protect user rights."
        ],
        "esg_score": 88
    }
]

extended_firm_data = [
    {
        "company_id": "FIRM001",
        "texts": [
            "The company has implemented zero-waste manufacturing.",
            "All electricity comes from certified renewable sources.",
            "Sustainability reports are verified by third parties."
        ],
        "esg_score": 92
    },
    {
        "company_id": "FIRM002",
        "texts": [
            "Workers complain about unsafe conditions and unpaid overtime.",
            "No diversity or inclusion programs are in place.",
            "The company has been fined for multiple environmental violations."
        ],
        "esg_score": 18
    },
    {
        "company_id": "FIRM003",
        "texts": [
            "The board includes independent members from diverse backgrounds.",
            "Green product development is central to R&D strategy.",
            "A whistleblower policy is clearly defined and enforced."
        ],
        "esg_score": 85
    },
    {
        "company_id": "FIRM004",
        "texts": [
            "CEO bonuses have increased while massive layoffs continue.",
            "Air pollution from factories remains unchecked.",
            "Corruption investigations are ongoing in multiple regions."
        ],
        "esg_score": 25
    },
    {
        "company_id": "FIRM005",
        "texts": [
            "The company supports employee well-being and mental health.",
            "Remote work and flexible hours are promoted.",
            "Inclusive hiring targets are met and published."
        ],
        "esg_score": 88
    },
    {
        "company_id": "FIRM006",
        "texts": [
            "Despite a sustainability claim, the supply chain lacks oversight.",
            "Employee turnover is high, and complaints remain unresolved.",
            "Some diversity hiring exists but lacks top-level support."
        ],
        "esg_score": 48
    },
    {
        "company_id": "FIRM007",
        "texts": [
            "Reforestation projects are funded annually.",
            "100% of packaging is biodegradable.",
            "Open-source ESG data is shared for industry use."
        ],
        "esg_score": 93
    },
    {
        "company_id": "FIRM008",
        "texts": [
            "Excessive water use threatens local communities.",
            "Human rights violations were reported in overseas operations.",
            "No ESG initiatives are documented or communicated."
        ],
        "esg_score": 12
    },
    {
        "company_id": "FIRM009",
        "texts": [
            "Environmental audits are performed biannually.",
            "Carbon emissions are reported but not reduced.",
            "Board composition is improving, but slowly."
        ],
        "esg_score": 61
    },
    {
        "company_id": "FIRM010",
        "texts": [
            "Data privacy violations have led to regulatory fines.",
            "Workers are not unionized and fear retaliation.",
            "The firm has no published ethics code."
        ],
        "esg_score": 22
    },
    {
        "company_id": "FIRM011",
        "texts": [
            "Sustainability KPIs are linked to executive compensation.",
            "ESG metrics are audited and reported quarterly.",
            "Global inclusion summits are hosted annually."
        ],
        "esg_score": 96
    },
    {
        "company_id": "FIRM012",
        "texts": [
            "The company publishes ESG claims with no verifiable data.",
            "Board meetings lack transparency and public access.",
            "There are unresolved labor disputes in key markets."
        ],
        "esg_score": 35
    },
    {
        "company_id": "FIRM013",
        "texts": [
            "Wastewater is treated and reused on-site.",
            "Employees receive ESG training as part of onboarding.",
            "Public policy engagement is based on sustainability goals."
        ],
        "esg_score": 91
    },
    {
        "company_id": "FIRM014",
        "texts": [
            "The company is involved in tax evasion and environmental fraud.",
            "Safety standards are frequently violated.",
            "Shareholders have no ESG-related voting rights."
        ],
        "esg_score": 10
    },
    {
        "company_id": "FIRM015",
        "texts": [
            "Some eco-products exist, but profit goals override ESG plans.",
            "Diversity efforts are tokenistic and unmeasured.",
            "Water usage is reduced, but energy still comes from coal."
        ],
        "esg_score": 42
    },
    {
        "company_id": "FIRM016",
        "texts": [
            "AI ethics are integrated into product design.",
            "Renewable energy is used at all headquarters.",
            "Annual ESG hackathons engage employees."
        ],
        "esg_score": 87
    },
    {
        "company_id": "FIRM017",
        "texts": [
            "Mining operations have caused major environmental damage.",
            "The company is the target of multiple corruption probes.",
            "There are no plans to shift away from fossil fuels."
        ],
        "esg_score": 8
    },
    {
        "company_id": "FIRM018",
        "texts": [
            "Carbon neutrality has been achieved since 2020.",
            "A circular economy model is implemented in manufacturing.",
            "All operations are verified under GRI and SASB standards."
        ],
        "esg_score": 98
    },
    {
        "company_id": "FIRM019",
        "texts": [
            "The company shows ESG progress, but lags behind competitors.",
            "Governance structure was updated, but still lacks clarity.",
            "Some transparency exists, yet not in high-risk regions."
        ],
        "esg_score": 55
    },
    {
        "company_id": "FIRM020",
        "texts": [
            "No internal ESG tracking exists.",
            "Employees report feeling unsafe and unheard.",
            "The company was delisted for financial misconduct."
        ],
        "esg_score": 5
    }
]


# === Tokenizer ===
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')


# === Dataset ===
class CompanyESGDataset(Dataset):
    def __init__(self, firm_data, tokenizer, max_length=128, max_blocks=10):
        self.firm_data = firm_data
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.max_blocks = max_blocks

    def __len__(self):
        return len(self.firm_data)

    def __getitem__(self, idx):
        entry = self.firm_data[idx]
        texts = entry["texts"][:self.max_blocks]
        label = torch.tensor(entry["esg_score"] / 100.0, dtype=torch.float)

        # Pad to max_blocks with empty strings if needed
        while len(texts) < self.max_blocks:
            texts.append("")

        encodings = self.tokenizer(
            texts,
            add_special_tokens=True,
            padding='max_length',
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt"
        )
        return {
            "input_ids": encodings["input_ids"],
            "attention_mask": encodings["attention_mask"],
            "label": label
        }


# === Modell mit Attention-Pooling ===
class ESGAggregatorModel(nn.Module):
    def __init__(self, pretrained_model="bert-base-uncased"):
        super().__init__()
        self.bert = BertModel.from_pretrained(pretrained_model)
        self.attn = nn.Linear(self.bert.config.hidden_size, 1)
        self.regressor = nn.Linear(self.bert.config.hidden_size, 1)

    def forward(self, input_ids, attention_mask):
        batch_size, num_blocks, seq_len = input_ids.size()

        input_ids = input_ids.view(-1, seq_len)
        attention_mask = attention_mask.view(-1, seq_len)

        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        cls_outputs = outputs.last_hidden_state[:, 0, :]  # CLS Token → [B*num_blocks, hidden]

        cls_outputs = cls_outputs.view(batch_size, num_blocks, -1)
        attn_weights = torch.softmax(self.attn(cls_outputs), dim=1)  # [B, num_blocks, 1]
        pooled = torch.sum(attn_weights * cls_outputs, dim=1)  # [B, hidden]

        score = self.regressor(pooled).squeeze(1)
        score = torch.sigmoid(score)
        return score


# === Trainingsfunktion ===
def train_model(model, dataloader, optimizer, epochs=10):
    model.train()
    loss_fn = nn.MSELoss()
    for epoch in range(epochs):
        total_loss = 0
        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["label"].to(device)

            optimizer.zero_grad()
            outputs = model(input_ids, attention_mask)
            loss = loss_fn(outputs, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(dataloader):.4f}")


# === Prediction-Funktion ===
def predict_company_score(model, texts):
    model.eval()
    with torch.no_grad():
        # Ensure consistent input structure
        max_blocks = 10
        while len(texts) < max_blocks:
            texts.append("")

        encodings = tokenizer(
            texts[:max_blocks],
            padding='max_length',
            truncation=True,
            max_length=128,
            return_tensors="pt"
        )
        input_ids = encodings['input_ids'].unsqueeze(0).to(device)  # [1, num_blocks, seq_len]
        attention_mask = encodings['attention_mask'].unsqueeze(0).to(device)

        pred = model(input_ids, attention_mask)
        return float(pred.item() * 100)


# === Main Execution ===
if __name__ == "__main__":
    # Init Dataset & Dataloader
    all_data = firm_data + extended_firm_data
    dataset = CompanyESGDataset(all_data, tokenizer)
    dataloader = DataLoader(dataset, batch_size=2, shuffle=True)

    # Init Model & Optimizer
    model = ESGAggregatorModel().to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)

    # Train
    train_model(model, dataloader, optimizer, epochs=10)

    # Predict
    print("\n--- Prediction Example ---")
    example_texts = [
        "The company invests in solar energy and biodiversity.",
        "Transparency reports are published quarterly.",
        "CEO involved in environmental violations and corruption."
    ]
    score = predict_company_score(model, example_texts)
    print(f"Predicted ESG Score: {score:.2f}")

    excellent_firm = [
        "The company operates with 100% renewable energy across all facilities.",
        "Carbon emissions have been reduced by 70% over the past five years.",
        "All suppliers are certified for environmental and ethical compliance.",
        "The board is gender-balanced and includes independent oversight.",
        "The company offers employee stock ownership and mental health programs.",
        "Zero tolerance for corruption and full financial transparency.",
        "AI ethics guidelines are externally audited and publicly accessible.",
        "Inclusive hiring policies ensure representation across all levels.",
        "Sustainability reports are verified by third parties annually.",
        "Recycling initiatives have led to 95% waste reduction."
    ]

    score = predict_company_score(model, excellent_firm)
    print(f"Excellent firm ESG Score: {score:.2f}")

    terrible_firm = [
        "The company has repeatedly ignored environmental regulations.",
        "Hazardous waste is dumped in local rivers without permits.",
        "Executives are under investigation for tax evasion and bribery.",
        "There are no safety measures in factories, leading to frequent injuries.",
        "Employees report discrimination and retaliation for whistleblowing.",
        "The board is made up entirely of insiders with conflicts of interest.",
        "No efforts have been made to track or reduce carbon footprint.",
        "A major data breach exposed sensitive customer information.",
        "Child labor allegations have emerged in the overseas supply chain.",
        "No ESG reporting is conducted or planned."
    ]

    score = predict_company_score(model, terrible_firm)
    print(f"Terrible firm ESG Score: {score:.2f}")

    mixed_firm = [
        "The company donates to local communities but lacks emissions goals.",
        "There are diversity initiatives, but leadership remains homogeneous.",
        "Efforts to improve transparency are underway, but data is incomplete.",
        "Workplace safety has improved, but some violations persist.",
        "Green product lines exist, yet overall energy use is still fossil-heavy.",
        "Governance is structured, though lacking independent oversight.",
        "The company has a sustainability team, but no published targets.",
        "Pay equity is a focus, but wage gaps remain in technical roles.",
        "Training on ethical AI is optional and not widely adopted.",
        "There is no formal ESG strategy, but some initiatives exist."
    ]

    score = predict_company_score(model, mixed_firm)
    print(f"Mixed firm ESG Score: {score:.2f}")
