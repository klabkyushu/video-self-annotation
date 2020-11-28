#!/bin/bash

project_root=$(pwd)

pip install -r requirements.txt

# cocoapi
cd $project_root/vendors/cocoapi/PythonAPI
python setup.py build_ext install

# apex
cd $project_root/vendors/apex
pip install -v --no-cache-dir --global-option="--cpp_ext" --global-option="--cuda_ext" .

# video-maskrcnn
cd $project_root/vendors/video-maskrcnn
python setup.py build develop

# Download pre-trained models
# https://drive.google.com/file/d/10bqv7fUeUEdT1Q9T617QTcttit5EJi76/view
mkdir -p $project_root/annotation/CityScapes/val/Dataset/Images
mkdir -p $project_root/annotation/CityScapes/val/Raw
cd $project_root/annotation/CityScapes/val/
fileid="10bqv7fUeUEdT1Q9T617QTcttit5EJi76"
filename="Initial_model.zip"
curl -c ./cookie -s -L "https://drive.google.com/uc?export=download&id=${fileid}" > /dev/null
curl -Lb ./cookie "https://drive.google.com/uc?export=download&confirm=`awk '/download/ {print $NF}' ./cookie`&id=${fileid}" -o ${filename}
rm ./cookie
unzip Initial_model.zip
rm Initial_model.zip

# CIResNet22_RPN.pth: https://drive.google.com/file/d/1tBllNtv-90Ih2EP_lnRCBzxnZeFPRnPx/view?usp=sharing
mkdir -p $project_root/vendors/video-maskrcnn/maskrcnn_benchmark/external/tracking/SOT/SiamDW/snapshot
cd $project_root/vendors/video-maskrcnn/maskrcnn_benchmark/external/tracking/SOT/SiamDW/snapshot
fileid="1tBllNtv-90Ih2EP_lnRCBzxnZeFPRnPx"
filename="CIResNet22_RPN.pth"
curl -c ./cookie -s -L "https://drive.google.com/uc?export=download&id=${fileid}" > /dev/null
curl -Lb ./cookie "https://drive.google.com/uc?export=download&confirm=`awk '/download/ {print $NF}' ./cookie`&id=${fileid}" -o ${filename}
rm ./cookie

cd $project_root
