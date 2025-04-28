# Load
import json
import os
from torch import device
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader, random_split
from transformers import BertTokenizer, BertModel
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# === Tokenizer ===
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# === Dataset ===
class CompanyESGDataset(Dataset):
    def __init__(self, firm_data, tokenizer, max_length=128, max_blocks=5):
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


def test_model(model, test_loader):
    model.eval()
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for batch in test_loader:
            input_ids = batch['input_ids'].to(device)  # Move to correct device
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['label'].to(device)

            preds = model(input_ids, attention_mask)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    # Metrics
    mse = mean_squared_error(all_labels, all_preds)
    mae = mean_absolute_error(all_labels, all_preds)
    r2 = r2_score(all_labels, all_preds)

    print(f"Test MSE: {mse:.4f}")
    print(f"Test MAE: {mae:.4f}")
    print(f"Test R²: {r2:.4f}")


model = ESGAggregatorModel().to(device)
model.load_state_dict(torch.load("esg_aggregator_model.pth", map_location=device, weights_only=True))
model.eval()

real_firm_data = []
ml_ready_esg_data_path = "../spg_global_data/ml_ready_esg_data.json"
if os.path.exists(ml_ready_esg_data_path):
    with open(ml_ready_esg_data_path, 'r', encoding='utf-8') as f:
        real_firm_data = json.load(f)

# Init Dataset
dataset = CompanyESGDataset(real_firm_data, tokenizer)

# Split dataset into Train / Validation / Test
total_size = len(dataset)
train_size = int(0.7 * total_size)
val_size = int(0.15 * total_size)
test_size = total_size - train_size - val_size  # Ensure all data is used

train_dataset, val_dataset, test_dataset = random_split(dataset, [train_size, val_size, test_size])

# Create Dataloaders
train_loader = DataLoader(train_dataset, batch_size=2, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=2, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=2, shuffle=False)

# Evaluate on the test set
test_model(model, test_loader)

'''
# Predict or test
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
'''


score = predict_company_score(model, real_firm_data[0]["texts"])
print(f"{real_firm_data[0]["company_id"]} ESG Score: {score:.2f}")


score = predict_company_score(model, real_firm_data[5]["texts"])
print(f"{real_firm_data[5]["company_id"]} ESG Score: {score:.2f}")


score = predict_company_score(model, real_firm_data[10]["texts"])
print(f"{real_firm_data[10]["company_id"]} ESG Score: {score:.2f}")



score = predict_company_score(model, real_firm_data[20]["texts"])
print(f"{real_firm_data[20]["company_id"]} ESG Score: {score:.2f}")