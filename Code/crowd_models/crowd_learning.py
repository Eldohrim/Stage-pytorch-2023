#%% 
import torch
from setup_datasets import *
from torch.nn.functional import softmax
from peerannot.helpers.networks import networks
import torch.optim as optim
import torch.nn as nn
from models import worker_pred, get_workers
import gc

# %%
obj_train = load_crowd(cifar10h, 'train')
lab = label_dist(obj_train, 10)
classe = ["plane","cat","dog","car","deer", "horse","ship",
          "truck","frog", "bird"]
n_classe = len(classe)

# %%
t = worker_json(obj_train, get_nb=False)
n_worker = len(t)

#%% Création dataset avec les distribution
n = len(obj_train)
dataset = []
for i in range(n):
    dataset.append(dl_link(lab[i], i, classe))

# %%
from torch.utils.data import DataLoader
batch_size = 16
trainset = DataLoader(dataset, batch_size=batch_size,
                      shuffle=True, num_workers=2)

#%%
# On a au plus 63 personnes qui ont voté sur une image et 
# une personne a voté au moins sur 181 images.

#%%
tot_worker = list(t.keys())
w = torch.ones(n_worker, dtype=torch.float, requires_grad=True) / n_worker
param = nn.Parameter(w)
optimizer = optim.SGD([param], lr=0.01, momentum=0.9)
loss = nn.CrossEntropyLoss()

for batch, (X, lab) in enumerate(trainset):
    optimizer.zero_grad()
    pred = torch.zeros((batch_size, n_classe)).to("cuda")
    model = networks('resnet18', n_classes=10, pretrained=False).to("cuda")
    for i in range(batch_size):
        work_t = get_workers(X[i], dataset, obj_train, tot_worker)
        p = torch.zeros((n_worker, n_classe))
        sel_w = torch.zeros((n_worker, 1))
        for k in work_t:
            p[int(k)] = worker_pred(model, X, int(k))[i].detach()
            sel_w[int(k)] = 1
        pred[i] = (1/sel_w.t().matmul(param))*p.t().matmul(param)
    del model
    gc.collect()
    torch.cuda.empty_cache()
    lossRes = loss(pred, lab.to("cuda"))
    lossRes.backward()
    optimizer.step()

# l'article ne précise pas si il faut softmax les poids 
# pendant la boucle ou à la fin.
