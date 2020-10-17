Video Object Self-Supervised Learning
=====================================================================================

[![Alt text](https://img.youtube.com/vi/R9dj6N_YDJU/0.jpg)](https://www.youtube.com/watch?v=R9dj6N_YDJU)

Visit our [Project Page](https://sites.google.com/view/ltnghia/research/video-self-annotation) for accessing the paper, and the pre-computed results.

We tested the code on python 3.7, PyTorch 1.2.0 and CUDA 10.1

## Installation

Use the following command to clone this repository recursively.

```bash
$ git clone --recursive https://github.com/klabkyushu/video-self-annotation.git
```

### Virtual Environment

For this system, it is recommanded to create a python virtual envrionment with virtualenv or conda.

In the case of virtualenv, use the following command to create a virtual environment,

```bash
$ virtualenv -p python3.7 .venv
```

and enter the environment by

```bash
$ source .venv/bin/activate
```

### Dependencies

Important dependencies:

- Python 3.7
- CUDA 10.1
- PyTorch 1.2.0
- opencv-python
- cocoapi/PythonAPI
- apex
- video-maskrcnn

**Please following the official instructions to install CUDA and corresponding PyTorch.**

After CUDA and PyTorch are installed, run the script `install.sh` to install other dependencies.

```bash
$ chmod +x install.sh
$ ./install.sh
```

## Docker

If you prefer docker container, you can build the image from docker/Dockerfile with the following command

```bash
$ docker build -t video-self-annotation -f docker/Dockerfile .
```

Since the image requires CUDA support, make sure NVIDIA container runtime is enabled before running the container. Also, please set your UID, GID and ssh-key (optional) before running the container in `docker/entrypoint.sh` because all codes are mounted instead of copying to the image for fast changes.

Run the container with

```bash
$ docker run -d --rm --gpus all \
  -v $(pwd):/home/user/video-self-annotation \
  -p 8022:22 \
  -p 8000:5901 \
  video-self-annotation
```

Then you can ssh to the container by

```bash
$ ssh user@localhost -p 8022
```

To enable VNC, run the following after SSH to the container as `user`,

```bash
$ chmod +x docker/vnc.sh
$ docker/vnc.sh
```

Then you can use TurboVNC viewer to view visual results by connecting to `localhost:8000`.

## Quick Start

TODO: Prepare an example.

## Prepare Data

```
mkdir -p -- CityScapes
cd CityScapes
mkdir -p -- val
cd val
mkdir -p -- Raw
cd Raw
```

Download [leftImg8bit_sequence_trainvaltest.zip (324GB)](https://www.cityscapes-dataset.com/downloads) and extract all sequences of val-set to CityScapes/val/Raw. 
For example, ./CityScapes/val/Raw/frankfurt/frankfurt_000000_000275_leftImg8bit.jpg

Download and extract [our pre-trained model](https://drive.google.com/file/d/10bqv7fUeUEdT1Q9T617QTcttit5EJi76/view?usp=sharing) to CityScapes/val/Initial_model

## Citations
Please consider citing this project in your publications if it helps your research:

```
@Inproceedings{ltnghia-WACV2020,
  Title          = {Toward Interactive Self-Annotation For Video Object Bounding Box: Recurrent Self-Learning And Hierarchical Annotation Based Framework},
  Author         = {Trung-Nghia Le and Akihiro Sugimoto and Shintaro Ono and Hiroshi Kawasaki},
  BookTitle      = {IEEE Winter Conference on Applications of Computer Vision},
  Year           = {2020},
}
```

## License

The code is released under the [Creative Commons Attribution-NonCommercial-ShareAlike 3.0 License](https://creativecommons.org/licenses/by-nc-sa/3.0/), and used for academic purpose only.

## Contact

[Trung-Nghia Le](https://sites.google.com/view/ltnghia).

