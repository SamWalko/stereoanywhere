1. I forked the repo and cloned it to the GPU servers.
2. Using the venv I've set up for the course, I tried to run pip install -r requirements.txt. However, there were issues with the torch==2.4.0+cu121 requirement. To fix it, I ran pip install torch==2.4.0+cu121 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 (ChatGPT suggestion), then reran pip install -r requirements.txt. I then also tried to run pip install -r requirements_demo.txt (which is newer than my project proposal), but it failed and it wasn't needed for the scripts I was focused on running.
3. I chose to use the ETH3D dataset as it was pretty lightweight compared to the others, just for testing purposes. I downloaded the ETH3D dataset as follows (I was not able to make p7zip work on the gpu servers):
    a) In a browser on my laptop, I visited https://www.eth3d.net/data/two_view_training.7z which automatically downloaded the compressed dataset.
    b) I extracted the file using 7zip (which Rose laptops come with).
    c) I copied the folder over to the GPU server (in the datasets folder).
4. Their GitHub also had a link to a Google Drive folder including their model weights from SceneFlow scenes. I downloaded sceneflow.tar from https://drive.google.com/drive/folders/1uQqNJo2iWoPtXlSsv2koAt2OPYHpuh1x and put it in a folder I called weights. I found the weights folder is already gitignored, so I've left it that way; you will have to repeat this step if you run it from this repo. I did NOT uncompress the .tar file.
5. I downloaded pre-trained model weights for Depth Anything v2 from https://github.com/DepthAnything/Depth-Anything-V2?tab=readme-ov-file#pre-trained-models. I used the Base weights, which downloads as a .pth file. I also put this file in the weights folder, which again is gitignored.
6. I was running into some errors, so I changed line 212 of test.py to:
```
pred_disps,_ = stereonet(data['im2'],data['im3'],data['im2_mono'],data['im3_mono'], args.iters, True)
```
7. I wanted to see the outputs of the program, so I made a outputs folder to include as an argument. Since I was using the ETH3D dataset, I also created a eth3d subfolder of outputs.
8. I ran the program as follows:
```
CUDA_VISIBLE_DEVICES=1,2,3,4 python test.py --datapath /home/walkosj/repos/stereoanywhere/datasets/eth3d/ --dataset eth3d --stereomodel stereoanywhere --loadstereomodel /home/walkosj/repos/stereoanywhere/weights/sceneflow.tar --monomodel DAv2 --loadmonomodel /home/walkosj/repos/stereoanywhere/weights/depth_anything_v2_vitb.pth --iscale 1 --oscale 1 --normalize --iters 32 --vol_n_masks 8 --n_additional_hourglass 0 --use_aggregate_mono_vol --vol_downsample 0 --mirror_conf_th 0.98  --use_truncate_vol --mirror_attenuation 0.9
```