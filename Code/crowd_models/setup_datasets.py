import torch
import os 
from torchvision.io import read_image

cifar10h = "../../peerannot/datasets/cifar10H/"

def worker_json(answer, get_nb=False):
    """
    Generates a JSON object that organizes workers responses for each task. 

    Args:
        answer (dict): A dictionary containing tasks responses for each worker.
        get_nb (bool, optional): If True, also returns the total number of responses. 
            Defaults to False.

    Returns:
        dict: A JSON object that organizes worker responses for each task.
        int: The total number of responses, if `get_nb` is True.
    """
    w_answer = {}
    b = 0
    for task, dict in answer.items():
        b+=len(dict)
        for worker, classes in dict.items():
            if worker in w_answer:
                w_answer[worker][task]=classes 
            else:
                w_answer[worker] = {}
                w_answer[worker][task]=classes
    if get_nb:
        return w_answer, b
    return w_answer

def count(list, target):
    """
	Counts the number of occurrences of a target value in a given list.

	Parameters:
	- list (list): The list in which to search for the target value.
	- target: The value to count occurrences of in the list.

	Returns:
	- int: The number of occurrences of the target value in the list.
	"""
    n = len(list)
    res = 0
    for i in range(n):
        if list[i]==target:
            res+=1
    return res

# %%
def get_prob(list, n_class):
    """
	Calculates the probability distribution of classes in a given list.
    
    Parameters:
	- list (list): The input list of class labels.
	- n_class: The number of distinct classes.

	Returns: 
    - torch.Tensor: The probability distribution of classes.
	"""
    prob = torch.zeros(n_class)
    for i in range(n_class):
        prob[i] = count(list, i)
    return prob/len(list)
# %%
def label_dist(dict, n_class, which='tensor'):
    """
    Calculate the label distributioof a task given by workers responses in a dictionary.

    Parameters:
        dict (dict): A dictionary containing tasks as keys and workers responses as values.
        n_class (int): The number of classes.
        which (str, optional): The type of output to be returned. Defaults to 'tensor'.

    Returns:
        torch.Tensor or dict: The label distribution for each task as either a tensor or a dictionary,
                              depending on the value of 'which' parameter.
    """
    n = len(dict)
    keys = list(dict.keys())
    if which=='tensor':
        res = torch.zeros(n,n_class)
        for i in range(n):
            res[i] = get_prob(list(dict[keys[i]].values()), n_class)
        return res
    elif which=='dict':
        res = {}
        for i in range(n):
            res[keys[i]]=get_prob(list(dict[keys[i]].values()), n_class)
        return res

#%%
def dl_link(lab, num, classe, type='train', root=cifar10h):
    """
    Return the image and its label.

    Parameters:
        lab (int): The label of the image.
        num (int): The number of the image.
        classe (list): A list of classes to search for the image.
        type (str, optional): The type of the dataset where is the image (default is 'train').
        root (str, optional): The root directory to search for the image (default is cifar10h).

    Returns:
        tuple or None: A tuple containing the image and its label.
"""
    for cl in classe:
        if os.path.exists(root+type+f"/{cl}/{cl}-{num}.png"):
            return (read_image(root+type+f"/{cl}/{cl}-{num}.png"), lab)