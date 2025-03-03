from .base_dataset import BaseDataset
from glob import glob
import os.path as osp
from .frame_utils import *
import numpy as np
import os
import cv2
import torch

class Middlebury2021Dataset(BaseDataset):
    def load_data(self, datapath):
        image_list = sorted(glob(osp.join(datapath, '*/im0.png')))
        for i in range(len(image_list)):
            if (not self.is_test and ('ArtL' not in image_list[i] and 'Teddy' not in image_list[i])) or self.is_test:
                _tmp = [image_list[i].replace('im0.png','disp0.pfm'), image_list[i], image_list[i].replace('im0', 'im1'), image_list[i].replace('im0.png', 'mask0nocc.png')]

                if self.mono is not None:        
                    _tmp += [image_list[i].replace('im0.png', f'im0_{self.mono}.png'), image_list[i].replace('im0.png', f'im1_{self.mono}.png')]

                self.image_list += [ _tmp ]
                self.extra_info += [ image_list[i].split('/')[-1] ] # scene and frame_id
    
    def load_sample(self, index):
        data = {}

        data['im2'] = read_gen(self.image_list[index][1])
        data['im3'] = read_gen(self.image_list[index][2])
        
        data['im2'] = np.array(data['im2']).astype(np.uint8)
        data['im3'] = np.array(data['im3']).astype(np.uint8)

        if self.mono is not None:
            data['im2_mono'] = read_mono(self.image_list[index][4])
            data['im3_mono'] = read_mono(self.image_list[index][5])

            data['im2_mono'] = np.expand_dims( data['im2_mono'].astype(np.float32), -1)
            data['im3_mono'] = np.expand_dims( data['im3_mono'].astype(np.float32), -1)

        if self.is_test:
            data['im2'] = data['im2'] / 255.0
            data['im3'] = data['im3'] / 255.0

        # grayscale images
        if len(data['im2'].shape) == 2:
            data['im2'] = np.tile(data['im2'][...,None], (1, 1, 3))
        else:
            data['im2'] = data['im2'][..., :3]                

        if len(data['im3'].shape) == 2:
            data['im3'] = np.tile(data['im3'][...,None], (1, 1, 3))
        else:
            data['im3'] = data['im3'][..., :3]

        data['gt'] = np.expand_dims( readPFM(self.image_list[index][0]), -1)
        data['validgt'] = (data['gt'] < 5000) & (data['gt'] > 0)

        data['gt'] = np.array(data['gt']).astype(np.float32)
        data['validgt'] = np.array(data['validgt']).astype(np.uint8)
        
        data['maskocc'] = np.expand_dims( np.array(read_gen(self.image_list[index][3])).astype(np.uint8), -1)
        data['maskocc'] = (data['maskocc'] == 128) # 1 if occluded, 0 otherwise
        data['maskocc'] = np.array(data['maskocc']).astype(np.uint8)

        for k in data:
            if data[k] is not None:
                if k not in ['gt', 'gt_right', 'validgt', 'validgt_right', 'maskocc']:
                    data[k] = cv2.resize(data[k], (int(data[k].shape[1]/self.scale_factor), int(data[k].shape[0]/self.scale_factor)), interpolation=cv2.INTER_LINEAR)
                else:
                    data[k] = cv2.resize(data[k], (int(data[k].shape[1]/self.scale_factor), int(data[k].shape[0]/self.scale_factor)), interpolation=cv2.INTER_NEAREST)

                if len(data[k].shape) == 2:
                    data[k] = np.expand_dims(data[k], -1)
                
                if k in ['gt', 'gt_right']:
                    data[k] = data[k] / self.scale_factor
        
        if self.is_test or self.augmentor is None:
            data['im2_aug'] = data['im2']
            data['im3_aug'] = data['im3']
        else:
            im2_mono = data['im2_mono'] if self.mono is not None else None
            im3_mono = data['im3_mono'] if self.mono is not None else None
            augm_data = self.augmentor(data['im2'], data['im3'], im2_mono, im3_mono, gt2=data['gt'], validgt2=data['validgt'], maskocc=data['maskocc'])

            for key in augm_data:
                data[key] = augm_data[key]

        for k in data:
            if data[k] is not None:
                data[k] = torch.from_numpy(data[k]).permute(2, 0, 1).float() 
        
        data['extra_info'] = self.extra_info[index]

        return data