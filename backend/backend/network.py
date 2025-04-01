import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
import torchvision.models as models
from collections import OrderedDict
import numpy as np


class Reccomender(torch.nn.Module):
    def __init__(self, batch_size):
        super(Reccomender, self).__init__()
        self.batch_size = batch_size
        #encoder
        self.conv1 = nn.Sequential(
            nn.Conv1d(
                in_channels=1, out_channels=64, kernel_size=3,
                stride=1, padding=1, bias=False
            ),
            nn.BatchNorm1d(64),
            nn.MaxPool1d(2),
            nn.LeakyReLU(inplace=True)
        )
        self.conv2 = nn.Sequential(
            nn.Conv1d(
                in_channels=64, out_channels=128, kernel_size=3,
                stride=1, padding=1, bias=False
            ),
            nn.MaxPool1d(2),
            nn.Tanh()
        )
        self.conv3 = nn.Sequential(
            nn.Conv1d(
                in_channels=128, out_channels=256, kernel_size=3,
                stride=1, padding=1, bias=False
            ),
            nn.MaxPool1d(2),
            nn.Tanh()
        )
        self.conv4 = nn.Sequential(
            nn.Conv1d(
                in_channels=256, out_channels=512, kernel_size=3,
                stride=1, padding=1, bias=False
            ),
            nn.MaxPool1d(2),
            nn.Tanh()
        )
        #memory
        # self.rnn = nn.GRU(input_size=512, hidden_size=1024, num_layers=3, batch_first=True, dropout=0.3)
        self.out = nn.Sequential(
            nn.Linear(1024, 32),
            nn.Tanh()
        )
    def forward(self, x):
        #encoder
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = self.conv4(x)
        # x = x.permute(0, 2, 1)
        # x, _ = self.rnn(x)
        x = x.reshape(x.size(0), -1)
        x = self.out(x)
        return x