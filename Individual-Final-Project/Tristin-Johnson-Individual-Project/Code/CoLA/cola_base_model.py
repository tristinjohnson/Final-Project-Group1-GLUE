"""
Tristin Johnson
GLUE Dataset - Corpus of Linguistic Acceptability (CoLA)
DATS 6450 - NLP
December 9th, 2021
"""

# import various packages
from datasets import load_dataset, load_metric
from transformers import (ElectraTokenizerFast, ElectraForSequenceClassification,
                          AlbertTokenizerFast, AlbertForSequenceClassification)
from transformers import Trainer, TrainingArguments, DataCollatorWithPadding
import numpy as np
import argparse


# define task
task = "cola"
sst = load_dataset("glue", name=task)

# arg parser
parser = argparse.ArgumentParser()
parser.add_argument('--model', default='electra', type=str, help="select a pretrained model: ['electra', 'albert']")
args = parser.parse_args()

# get model from flag
if args.model == 'electra':
    checkpoint = 'google/electra-small-discriminator'
    tokenizer = ElectraTokenizerFast.from_pretrained(checkpoint)
    model = ElectraForSequenceClassification.from_pretrained(checkpoint, num_labels=2)

elif args.model == 'albert':
    checkpoint = 'albert-base-v2'
    tokenizer = AlbertTokenizerFast.from_pretrained(checkpoint)
    model = AlbertForSequenceClassification.from_pretrained(checkpoint)


# tokenize the sentences
def pretrained_tokenizer(data):
    return tokenizer(data['sentence'], truncation=True)


# tokenize dataset and implement data collator
sst = sst.map(pretrained_tokenizer, batched=True)
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# define training args
training_args = TrainingArguments(
    output_dir='cola_results',
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=2,
    evaluation_strategy='epoch'
)


# define metrics from task
def compute_metrics(pred):
    metric = load_metric("glue", task)
    logits, labels = pred
    predictions = np.argmax(logits, axis=-1)

    return metric.compute(predictions=predictions, references=labels)


# train the model
trainer = Trainer(
    model,
    training_args,
    train_dataset=sst['train'],
    eval_dataset=sst['validation'],
    data_collator=data_collator,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics
)

# electra  ->   val_mcc = 0.5508, :33 per epoch
# albert    ->   val_mcc = 0.4187, 1:29 per epoch
trainer.train()