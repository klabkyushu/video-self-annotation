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
- pyqt5-dev-tools

**Please following the official instructions to install CUDA and PyTorch.**

Install `pyqt5` by

```bash
$ sudo apt update
$ sudo apt install pyqt5-dev-tools
```

After CUDA and PyTorch are installed, run the script `install.sh` to install other dependencies.

```bash
$ chmod +x install.sh
$ ./install.sh
```

Finally, install `video-self-annotation` by

```bash
$ pip install -e annotation
$ annotate --help
```

## Docker

If you prefer a docker container, you can build the image from docker/Dockerfile with the following command

```bash
$ docker build -t video-self-annotation -f docker/Dockerfile .
```

Since the image requires CUDA support, make sure [NVIDIA container runtime](https://github.com/NVIDIA/nvidia-docker) is enabled before running the container. Also, please set your UID, GID and ssh-key (optional) before running the container in `docker/entrypoint.sh` because all codes are mounted instead of copying to the image for fast changes.

Run the container with

```bash
$ docker run -d --rm --gpus all --name annotation \
  -v $(pwd):/home/user/video-self-annotation \
  -p 8022:22 \
  -p 8901:5901 \
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

Then you can use TurboVNC viewer to view visual results by connecting to `localhost:8901`.

Make sure to use `docker logs annotation` to check whether the container is ready before executing any annotation.

## Quick Start

First, download the example data `aachen` in `data`.

```bash
$ cd data
$ chmod +x scripts/dl_aachen.sh
$ scripts/dl_aachen.sh
$ cd ..
```

Then, under the root directory, add `aachen` to the workspace.

```bash
$ annotate add aachen --images data/aachen
```

Use `annotate stat` to show the information of all image sequences in the workspace.

Then, use the following to perform an annotation task and to output the result.

```bash
$ annotate run aachen --output results/aachen
```

Finally, use the following to view the result.

```bash
$ annotate play -r results/aachen
```

To utilize other functionalities, feel free to explore the commands with `--help`.

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
