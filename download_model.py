python - <<'EOF'
from transformers import AutoTokenizer, AutoModelForSequenceClassification
model = AutoModelForSequenceClassification.from_pretrained("./distilbert-sst2")
tokenizer = AutoTokenizer.from_pretrained("./distilbert-sst2")
print("Model loaded:", model.config.id2label)
EOF
