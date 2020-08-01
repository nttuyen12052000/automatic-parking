import os
from model_FD.new_user.train import train_new
data = "model_FD/new_user/dataset/"
count = 0
while(True):
    flag = len(list(os.walk(data)))-1
    if count != flag:
        if count >0:
            train()
        print("Trained")
        count = flag
    # print("No training")