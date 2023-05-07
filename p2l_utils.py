import math
import numpy as np

def get_rolling_crops(image, stride = [128, 128], window_size = 512):
    # as of now stride is not implemented
    image_height, image_width, channels = image.shape


    # Compute the number of rolling windows
    # nwindows_vertical = math.ceil(image_height / window_size)
    # nwindows_horizontal = math.ceil(image_width / window_size)
    nwindows_vertical = math.ceil((image_height - window_size) / stride[0]) + 1
    nwindows_horizontal = math.ceil((image_width - window_size) / stride[1]) + 1

    print(f"Number of windows: {nwindows_vertical} x {nwindows_horizontal}")
    crops_list = []
    padded_crops_list = []
    crops_info_list = []

    for i in range(nwindows_vertical):
        for j in range(nwindows_horizontal):
            # window_x_start = j * window_size
            window_x_start = j * stride[1]
            window_x_end = min(window_x_start + window_size, image_width)
            # window_y_start = i * window_size
            window_y_start = i * stride[0]
            window_y_end = min(window_y_start + window_size, image_height)
            window_width = window_x_end - window_x_start
            window_height = window_y_end - window_y_start

            rolling_window = image[window_y_start:window_y_end, window_x_start:window_x_end]

            # create new image of desired size with white background
            color = (255,255,255)
            padded_window = np.full((window_size,window_size, channels), color, dtype=np.uint8)

            # compute center offset
            x_center = (window_size - window_width) // 2
            y_center = (window_size - window_height) // 2

            # Copy the window to the center of the white square
            padded_window[y_center:y_center+window_height, x_center:x_center+window_width] = rolling_window

            crops_list.append(rolling_window)
            padded_crops_list.append(padded_window)
            
            crops_info_list.append((window_x_start, window_y_start, window_width, window_height))
    return crops_list, padded_crops_list, crops_info_list


def postprocess(window_borders, scores, crops_info_list, window_size=512):
    bb_list = []
    scores_list = []

    for i in range(len(window_borders)):
        window_border = window_borders[i]
        score = scores[i]
        window_x_start, window_y_start, window_width, window_height = crops_info_list[i]
        for k in range(len(window_border)):

            x0 = window_x_start+(window_border[k][0]-(window_size-window_width)//2)
            y0 = window_y_start+(window_border[k][1]-(window_size-window_height)//2)
            x1 = window_x_start+(window_border[k][2]-(window_size-window_width)//2)
            y1 = window_y_start+(window_border[k][3]-(window_size-window_height)//2)
            
            bb_list.append([x0, y0, x1, y1])
            scores_list.append(score[k])
    return bb_list, scores_list

if __name__ == "__main__":
    print("hello world")