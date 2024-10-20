# -*- coding: utf-8 -*-
"""notebook64dd5f165a

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/#fileId=https%3A//storage.googleapis.com/kaggle-colab-exported-notebooks/notebook64dd5f165a-9feafccf-d2be-4c9d-b0ef-8b95b67d9be0.ipynb%3FX-Goog-Algorithm%3DGOOG4-RSA-SHA256%26X-Goog-Credential%3Dgcp-kaggle-com%2540kaggle-161607.iam.gserviceaccount.com/20240831/auto/storage/goog4_request%26X-Goog-Date%3D20240831T113432Z%26X-Goog-Expires%3D259200%26X-Goog-SignedHeaders%3Dhost%26X-Goog-Signature%3Dc36d9e5f0d15ca343eeaa6213c75d93d3b056aeccc4e2f1de1709e41ff42ffa57474a6dc7e8904697d3fc760f52ad90ab6ccd71be17ad09a02dfd7bb50d4398c78a4f6f23b25e69ec2fea3a697a17be567772c205741c6f87b05d1ee18a603f01583b792c15e0ba097f45be9f1258b3157c22b35ccbff5e7c39c0b5cc77bcd1a4c70b77a2b706e9321f6304972f4c1b654271891d1fef1108fce74bb6de547f337bc774f91f7f840fb0c2b925a6ba016a493522395cbbbc4ca0903898db64944154b3c9f367022bc020a8f7f13ae72c21bf6852315469e466e69b9af1ac8b7b724c914278a9db99d02fed578d519f7fbb86c0faee86217edfed9a4f2bae3f7d1
"""

# 'pip -q install' is used to install Python packages with pip, Python's package installer, in a quiet mode which reduces the output verbosity.
# 'huggingface_hub', 'transformers', 'peft', and 'bitsandbytes' are the packages being installed by the first command.
# These packages are necessary for the fine-tuning and inference of the Phi-3 model.
# 'trl' and 'xformers' are additional packages being installed by the second command.
# 'datasets' is a package for providing access to a vast range of datasets, installed by the third command.
# The last command ensures that 'torch' version is at least 1.10. If it's already installed but the version is lower, it will be upgraded.


# Import necessary modules from the transformers library
# AutoModelForCausalLM: This is a class for causal language models. It's used for tasks like text generation.
# AutoTokenizer: This class is used for tokenizing input data, a necessary step before feeding data into a model.
# TrainingArguments: This class is used for defining the parameters for model training, like learning rate, batch size, etc.
# BitsAndBytesConfig: This class is used for configuring the BitsAndBytes quantization process.
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, BitsAndBytesConfig

# Import necessary modules from the huggingface_hub library
# ModelCard: This class is used for creating a model card, which provides information about a model.
# ModelCardData: This class is used for defining the data of a model card.
# HfApi: This class provides an interface to the Hugging Face API, allowing you to interact with the Hugging Face Model Hub.
from huggingface_hub import ModelCard, ModelCardData, HfApi

# Import the load_dataset function from the datasets library. This function is used for loading datasets.
from datasets import load_dataset

# Import the Template class from the jinja2 library. This class is used for creating dynamic HTML templates.
from jinja2 import Template

# Import the SFTTrainer class from the trl library. This class is used for training models.
from trl import SFTTrainer

# Import the yaml module. This module is used for working with YAML files.
import yaml
import numpy as np
# Import the torch library. This library provides tools for training and running deep learning models.
import torch
from datasets import load_metric
metric = load_metric('accuracy')

def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    return metric.compute(predictions=predictions, references=labels)


# MODEL_ID is a string that specifies the identifier of the pre-trained model that will be fine-tuned.
# In this case, the model is 'Phi-3-mini-4k-instruct' from Microsoft.
MODEL_ID = "microsoft/Phi-3.5-mini-instruct"

# Maximum epocs to train
MAX_TRAIN_EPOCHS=15

# MAX_SEQ_LENGTH is an integer that specifies the maximum length of the sequences that the model will handle.
#MAX_SEQ_LENGTH = 2048
# This is the max sequence lenght that works
MAX_SEQ_LENGTH = 1024


# NEW_MODEL_NAME is a string that specifies the name of the new model after fine-tuning.
# Here, the new model will be named 'opus-samantha-phi-3-mini-4k'.
#NEW_MODEL_NAME = "".join("Epoch_", MAX_TRAIN_EPOCHS,"-", MAX_SEQ_LENGTH, "-phi-3.5-mini-4k")
NEW_MODEL_NAME = "Epoch_" + str(MAX_TRAIN_EPOCHS) + "-" +str(MAX_SEQ_LENGTH) + "-phi-3.5-mini-4k"


# DATASET_NAME is a string that specifies the name of the dataset to be used for fine-tuning.
# Replace "replace with your dataset" with the actual name of your dataset.
#DATASET_NAME = "neil-code/dialogsum-test"
DATASET_NAME = "AlexanderBenady/lecture_summary_translations_english_spanish"
# SPLIT specifies the portion of the dataset to be used. In this case, the 'train' split of the dataset will be used.
SPLIT = "train"

# num_train_epochs is an integer that specifies the number of times the training process will go through the entire dataset.
num_train_epochs = 1


# license is a string that specifies the license under which the model is distributed. In this case, it's Apache License 2.0.
license = "apache-2.0"

# username is a string that specifies the GitHub username of the person who is fine-tuning the model.
username = "GitHubUsername"

# learning_rate is a float that specifies the learning rate to be used during training.
learning_rate = 1.41e-5

# per_device_train_batch_size is an integer that specifies the number of samples to work through before updating the internal model parameters.
per_device_train_batch_size = 4

# gradient_accumulation_steps is an integer that specifies the number of steps to accumulate gradients before performing a backward/update pass.
gradient_accumulation_steps = 1

# This code checks if the current CUDA device supports bfloat16 (Brain Floating Point) computations.
# If bfloat16 is supported, it sets the compute_dtype to torch.bfloat16.
# If not, it sets the compute_dtype to torch.float16.
# bfloat16 and float16 are both half-precision floating-point formats, but bfloat16 provides better performance on some hardware.

# Load the pre-trained model specified by MODEL_ID using the AutoModelForCausalLM class.
# The 'trust_remote_code=True' argument allows the execution of code from the model card (if any).
model = AutoModelForCausalLM.from_pretrained(MODEL_ID, trust_remote_code=True)

# Load the tokenizer associated with the pre-trained model specified by MODEL_ID using the AutoTokenizer class.
# The 'trust_remote_code=True' argument allows the execution of code from the model card (if any).
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)

# Load the dataset specified by DATASET_NAME using the load_dataset function.
# The 'split="train"' argument specifies that we want to load the training split of the dataset.
dataset = load_dataset(DATASET_NAME, split="train")
dataset_test = load_dataset(DATASET_NAME, split="test")

# Get the ID of the end-of-sentence (EOS) token from the tokenizer and store it in EOS_TOKEN.
# This token is used to mark the end of a sentence in the input data.
EOS_TOKEN=tokenizer.eos_token_id

# This line simply prints the contents of the 'dataset' variable.
# 'dataset' is expected to be a Dataset object loaded from the 'datasets' library.
# Printing it will display information about the dataset such as the number of samples, the features, and a few example data points.

def formatting_prompts_func(examples):
    # Extract the conversations from the examples.
    convos = examples["conversations"]
    # Initialize an empty list to store the formatted texts.
    texts = []
    # Define a dictionary to map the 'from' field in the conversation to a prefix.
    mapper = {"system": "system\n", "human": "\nuser\n", "gpt": "\nassistant\n"}
    # Define a dictionary to map the 'from' field in the conversation to a suffix.
    end_mapper = {"system": "", "human": "", "gpt": ""}
    # Iterate over each conversation.
    for convo in convos:
        # Format the conversation by joining each turn with its corresponding prefix and suffix.
        # Append the EOS token to the end of the conversation.
        text = "".join(f"{mapper[(turn := x['from'])]} {x['value']}\n{end_mapper[turn]}" for x in convo)
        texts.append(f"{text}{EOS_TOKEN}")
    # Return the formatted texts.
    return {"text": texts}

def create_prompt_formats(sample):
    """
    Format various fields of the sample ('instruction','output')
    Then concatenate them using two newline characters
    :param sample: Sample dictionnary
    """
    INTRO_BLURB = "Below is an instruction that describes a task. Write a response that appropriately completes the request."
    INSTRUCTION_KEY = "### Instruct: Summarize the below text."
    RESPONSE_KEY = "### Output:"
    END_KEY = "### End"

    blurb = f"\n{INTRO_BLURB}"
    instruction = f"{INSTRUCTION_KEY}"
    input_context = f"{sample['Lecture']}" if sample["Lecture"] else None
    response = f"{RESPONSE_KEY}\n{sample['Summary']}"
    end = f"{END_KEY}"

    parts = [part for part in [blurb, instruction, input_context, response, end] if part]

    formatted_prompt = "\n\n".join(parts)
    sample["text"] = formatted_prompt

    return sample

# Apply the formatting function to the dataset using the map method.
# The 'batched=True' argument means that the function is applied to batches of examples.
dataset = dataset.map(create_prompt_formats)
dataset_test = dataset_test.map(create_prompt_formats)

# Print the 9th example from the 'text' field of the dataset to check the result.



args = TrainingArguments(
    # 'evaluation_strategy' is set to "steps", which means evaluation is done at each logging step.
    evaluation_strategy="steps",

    # 'per_device_train_batch_size' is set to 7, which means each training batch will contain 7 samples per device.
    per_device_train_batch_size=7,

    # 'gradient_accumulation_steps' is set to 4, which means gradients are accumulated for 4 steps before performing a backward/update pass.
    gradient_accumulation_steps=4,

    # 'gradient_checkpointing' is set to True, which means model gradients are stored in memory during training to reduce memory usage.
    gradient_checkpointing=True,

    # 'learning_rate' is set to 1e-4, which is the learning rate for the optimizer.
    learning_rate=1e-4,

    # 'fp16' is set to True if bfloat16 is not supported, which means the model will use 16-bit floating point precision for training if possible.

    # 'bf16' is set to True if bfloat16 is supported, which means the model will use bfloat16 precision for training if possible.

    # 'max_steps' is set to -1, which means there is no maximum number of training steps.
    max_steps=-1,

    # 'num_train_epochs' is set to 3, which means the training process will go through the entire dataset 3 times.
    num_train_epochs=MAX_TRAIN_EPOCHS,

    # 'save_strategy' is set to "epoch", which means the model is saved at the end of each epoch.
    save_strategy="epoch",

    # 'logging_steps' is set to 10, which means logging is done every 10 steps.
    logging_steps=10,

    # 'output_dir' is set to NEW_MODEL_NAME, which is the directory where the model and its configuration will be saved.
    output_dir=NEW_MODEL_NAME,

    # 'optim' is set to "paged_adamw_32bit", which is the optimizer to be used for training.
    optim="paged_adamw_32bit",

    # 'lr_scheduler_type' is set to "linear", which means the learning rate scheduler type is linear.
    lr_scheduler_type="linear",
    
    report_to=None
)

import os
# disable Weights and Biases
os.environ['WANDB_DISABLED']="true"

trainer = SFTTrainer(
    # 'model' is the pre-trained model that will be fine-tuned.
    model=model,

    # 'args' are the training arguments that specify the training parameters.
    args=args,

    # 'train_dataset' is the dataset that will be used for training.
    train_dataset=dataset,
    test_dataset= dataset_test,
    compute_metrics= compute_metrics,

    # 'dataset_text_field' is the key in the dataset that contains the text data.
    dataset_text_field="text",

    # 'max_seq_length' is the maximum length of the sequences that the model will handle.
    max_seq_length=MAX_SEQ_LENGTH,
    #max_seq_length=1024,

    # 'formatting_func' is the function that will be used to format the prompts in the dataset.
    formatting_func=create_prompt_formats
)

# 'device' is set to 'cuda', which means the CUDA device will be used for computations if available.
device = 'cuda'

# Import the 'gc' module, which provides an interface to the garbage collector.
import gc

# Import the 'os' module, which provides a way of using operating system dependent functionality.
import os

# Call the 'collect' method of the 'gc' module to start a garbage collection, which can help free up memory.
gc.collect()

# Call the 'empty_cache' method of 'torch.cuda' to release all unused cached memory from PyTorch so that it can be used by other GPU applications.

# Call the 'train' method of the 'trainer' object to start the training process.
# This method will fine-tune the model on the training dataset according to the parameters specified in the 'args' object.
trainer.train()
