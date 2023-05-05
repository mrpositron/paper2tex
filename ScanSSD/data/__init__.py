#from .gtdb import GTDB_CLASSES, GTDB_ROOT, GTDBAnnotationTransform, GTDBDetection
from .gtdb_new import GTDB_CLASSES, GTDB_ROOT, GTDBAnnotationTransform, GTDBDetection
from .config import *
import torch
import cv2
import numpy as np

def detection_collate(batch):
    """Custom collate fn for dealing with batches of images that have a different
    number of associated object annotations (bounding boxes).

    Arguments:
        batch: (tuple) A tuple of tensor images and lists of annotations

    Return:
        A tuple containing:
            1) (tensor) batch of images stacked on their 0 dim
            2) (list of tensors) annotations for a given image are stacked on
                                 0 dim
    """
    targets = []
    imgs = []
    ids = []

    for sample in batch:
        imgs.append(sample[0])
        targets.append(torch.FloatTensor(sample[1]))
        ids.append(sample[2])

    return torch.stack(imgs, 0), targets, ids


def base_transform(image, size, mean):
    #print('Image size ', image.shape)
    image = image.astype(np.float32)
    x = cv2.resize(image, (size, size), interpolation=cv2.INTER_AREA).astype(np.float32)
    x -= mean
    return x


class BaseTransform:
    def __init__(self, size, mean):
        self.size = size
        self.mean = np.array(mean, dtype=np.float32)

    def __call__(self, image, boxes=None, labels=None):
        return base_transform(image, self.size, self.mean), boxes, labels
