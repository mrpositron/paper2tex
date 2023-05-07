# Fix relative import issues
import sys, os
sys.path.insert(0, os.path.join('ScanSSD'))
sys.path.insert(0, os.path.join('ScanSSD', 'layers'))
sys.path.insert(0, os.path.join('ScanSSD', 'gtdb'))


from collections import OrderedDict
import cv2
import math
import numpy as np
import argparse
import torch
import torch.nn as nn
from torchvision import transforms
from ScanSSD.ssd import build_ssd
from ScanSSD.data import config

# From https://github.com/jjdredd/ScanSSD/blob/lowmem/detect.py (Thanks jjdredd)


# def draw_box (image, boxes):
#     for b in boxes:
#         cv2.rectangle(image, (b[0], b[1]), (b[2], b[3]), (0, 255, 0), 2)


def _img_to_tensor (image):
    rimg = cv2.resize(image, (512, 512),
                      interpolation = cv2.INTER_AREA).astype(np.float32)
    rimg -= np.array((246, 246, 246), dtype=np.float32)
    rimg = rimg[:, :, (2, 1, 0)]
    return torch.from_numpy(rimg).permute(2, 0, 1)


def FixImgCoordinates (images, boxes):
    new_boxes = []
    if isinstance(images, list):
            for i in range(len(images)):
                # print(images[i].shape)
                bbs = []
                for o_box in boxes[i] :
                    b = [None] * 4
                    b[0] = int(o_box[0] * images[i].shape[0])
                    b[1] = int(o_box[1] * images[i].shape[1])
                    b[2] = int(o_box[2] * images[i].shape[0])
                    b[3] = int(o_box[3] * images[i].shape[1])
                    bbs.append(b)

                new_boxes.append(bbs)
    else:
        bbs = []
        for o_box in boxes[0] :
            b = [None] * 4
            b[0] = int(o_box[0] * images.shape[0])
            b[1] = int(o_box[1] * images.shape[1])
            b[2] = int(o_box[2] * images.shape[0])
            b[3] = int(o_box[3] * images.shape[1])
            bbs.append(b)

            # this could be
            # b[0] = int(o_box[0] * images.shape[0]) ==> b[0] = int(o_box[0] * images.shape[1])
            # b[1] = int(o_box[1] * images.shape[1]) ==> b[1] = int(o_box[1] * images.shape[0])
            # b[2] = int(o_box[2] * images.shape[0]) ==> b[2] = int(o_box[2] * images.shape[1])
            # b[3] = int(o_box[3] * images.shape[1]) ==> b[3] = int(o_box[3] * images.shape[0])

        new_boxes.append(bbs)

    return new_boxes


class MathDetector():

    def __init__(self, weight_path, args):
        net = build_ssd(args, 'test', config.exp_cfg[args.cfg], 0, args.model_type, num_classes = 2)
        self._net = net # nn.DataParallel(net)
        weights = torch.load(weight_path, map_location = torch.device('cpu'))

        new_weights = OrderedDict()
        for k, v in weights.items():
            name = k[7:] # remove `module.`
            new_weights[name] = v

        self._net.load_state_dict(new_weights)

        if args.cuda and torch.cuda.is_available():
            self._net = self._net.cuda()

        self._net.eval()

    @torch.no_grad()
    def Detect (self, thres, images):
        cls = 1                 # math class
        boxes = []
        scores = []

        if args.cuda and torch.cuda.is_available():
            images = images.cuda()
        y, debug_boxes, debug_scores = self._net(images)  # forward pass

        y, debug_boxes, debug_scores = y.cpu(), debug_boxes.cpu(), debug_scores.cpu()
        detections = y.data

        for k in range(len(images)):

            img_boxes = []
            img_scores = []
            for j in range(detections.size(2)):

                if ( detections[k, cls, j, 0] < thres ):
                    continue

                pt = detections[k, cls, j, 1:]
                coords = (pt[0], pt[1], pt[2], pt[3])
                img_boxes.append(coords)
                img_scores.append(detections[k, cls, j, 0])

            boxes.append(img_boxes)
            scores.append(img_scores)

        return boxes, scores

    def ShowNetwork (self):
        print(self._net)

    @torch.no_grad()
    def DetectAny(self, image, thres):
        if isinstance(image, list):
            t_list = [_img_to_tensor(img) for img in image]
            t = torch.stack(t_list, dim = 0)
        else:
            t = _img_to_tensor(image).unsqueeze(0)
        # fix box coordinates to image pixel coordinates
        boxes, scores = self.Detect(thres, t)
        return FixImgCoordinates(image, boxes), scores



if __name__ == '__main__':
    print ("Loading model...")
    md = MathDetector('./saved_models/AMATH512_e1GTDB.pth', ArgStub())
    print ("Model loaded")


