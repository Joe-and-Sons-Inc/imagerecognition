import time
import torch
import numpy as np
from torchvision import models, transforms
import cv2
from PIL import Image
import json

def image_recog_one_frame():
    final_output = []
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 224)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 224)
    cap.set(cv2.CAP_PROP_FPS, 36)

    preprocess = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225]),
    ])

    net = models.mobilenet_v2(weights='DEFAULT')
    # jit model to take it from ~20fps to ~30fps
    net = torch.jit.script(net)

    started = time.time()
    last_logged = time.time()
    frame_count = 0

    classes = None
    with open('classes.json') as json_file:
        classes = json.load(json_file)

    with torch.no_grad():
        while True:
            # read frame
            ret, image = cap.read()
            if not ret:
                raise RuntimeError("failed to read frame")

            # convert opencv output from BGR to RGB
            image = image[:, :, [2, 1, 0]]
            permuted = image

            # preprocess
            input_tensor = preprocess(image)

            # create a mini-batch as expected by the model
            input_batch = input_tensor.unsqueeze(0)

            # run model
            output = net(input_batch)
            # do something with output ...

            # log model performance
            frame_count += 1
            now = time.time()
            if now - last_logged > 1:
                last_logged = now
                frame_count = 0

            top = list(enumerate(output[0].softmax(dim=0)))
            top.sort(key=lambda x: x[1], reverse=True)
            for idx, val in top[:10]:
                if (val.item() * 100):
                    if (val.item() * 100 > 30):
                        final_output.append(classes[str(idx)])
            break
    return final_output