#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This script provides an example for timing CPU-GPU transfers.

Usage: -

Author: Andres J. Sanchez-Fernandez
Email: sfandres@unex.es
Date: 2023-04-03
"""


import torch
from torch.utils.data import DataLoader, random_split
from torchvision.datasets import CIFAR10
from torchvision import transforms
import numpy as np


# Set the random seed for PyTorch and NumPy
torch.manual_seed(0)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
np.random.seed(0)

# Define transform for data preprocessing.
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

# Load CIFAR10 dataset.
print('---------------------------------------------')
dataset = CIFAR10(root='./data/',
                  train=True,
                  download=True,
                  transform=transform)

# Split dataset into train and validation sets.
print('---------------------------------------------')
print(f'Number of samples in dataset: {len(dataset)}')
train_dataset, val_dataset = random_split(dataset, [47500, 2500])
print(f'Number of samples in train set: {len(train_dataset)}')

# Create dataloaders for train set.
batch_size = 64
train_dataloader = DataLoader(train_dataset,
                              batch_size=batch_size,
                              shuffle=True,
                              num_workers=1)
print(f'Batch size: {batch_size}')

# Select the GPU for training.
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'Device: {device}')
print('---------------------------------------------')

# Define a model and move it to GPU.
# model = torch.nn.Sequential(
#     torch.nn.Conv2d(3, 6, kernel_size=5),
#     torch.nn.ReLU(),
#     torch.nn.MaxPool2d(kernel_size=2),
#     torch.nn.Conv2d(6, 16, kernel_size=5),
#     torch.nn.ReLU(),
#     torch.nn.MaxPool2d(kernel_size=2),
#     torch.nn.Flatten(),
#     torch.nn.Linear(16 * 5 * 5, 120),
#     torch.nn.ReLU(),
#     torch.nn.Linear(120, 84),
#     torch.nn.ReLU(),
#     torch.nn.Linear(84, 10)
# )
# model.to(device)

# Time the CPU-GPU transfers of the train dataloader.
start_event = torch.cuda.Event(enable_timing=True)
end_event = torch.cuda.Event(enable_timing=True)
transfer_times = []
start_event.record()
for i, (images, labels) in enumerate(train_dataloader):
    images = images.to(device)
    labels = labels.to(device)
    end_event.record()
    torch.cuda.synchronize()  # synchronize CPU and GPU execution.
    transfer_time = start_event.elapsed_time(end_event)
    transfer_times.append(transfer_time)
    start_event.record()

# Compute average and show results.
total_transfer_time = sum(transfer_times)
total_batches = len(transfer_times)
avg_transfer_time = total_transfer_time / total_batches
print(f'Average time for transferring one batch from CPU to GPU:'
      f' {avg_transfer_time:.4f} ms')
print(f'Total time for transferring {total_batches} batches from CPU to GPU:'
      f' {(total_transfer_time/1000.0):.4f} s')
print('---------------------------------------------')
