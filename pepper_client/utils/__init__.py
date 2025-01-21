import json
import numpy as np
from .speech_processor import SpeechProcessor

def is_zero_list(box):
    for i in box:
        if i == 0:
            return True
    return False


def get_vh_axis(box, img_shape, stop_threshold=0.5, vertical_offset=0.5):
    box_center = np.array([box[2] / 2 + box[0] / 2, box[1] * (1 - vertical_offset) + box[3] * vertical_offset])
    frame_center = np.array((img_shape[1] / 2, img_shape[0] / 2))
    diff = frame_center - box_center
    horizontal_ratio = diff[0] / img_shape[1]
    vertical_ratio = diff[1] / img_shape[0]

    if abs(horizontal_ratio) <= stop_threshold and abs(vertical_ratio) <= vertical_offset:
        return (-vertical_ratio * 0.4, horizontal_ratio * 0.6)
    else:
        return (0, 0)

