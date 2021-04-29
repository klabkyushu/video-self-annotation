import click
import os
import cv2
import shutil
import re

import init_root_dirs
import create_dataset
import clear_dir
import run_rcnn
import generate_raw_ann_from_rcnn_results
import generate_adaptive_detection
import track_instances
import create_tubelets
import filter_data
import add_instances
import convert_tubelet_to_coco_format
import ulti

PATH_IMAGES = 'annotation/CityScapes/val/Dataset/Images'

@click.group()
def root_cmd():
    pass

@root_cmd.command()
def stat():
    '''Show the current status of the workspace.
    '''
    dir_names = os.listdir(PATH_IMAGES)
    dir_names.sort()
    header = ['Sequence Name', 'Number of Images', 'Chunked?', 'Number of Chunks', 'Size of Chunks']
    status = {}
    chunk_reg = re.compile('^.*-[0-9]{3}$')
    for dir_name in dir_names:
        n_imgs = len(os.listdir(os.path.join(PATH_IMAGES, dir_name)))
        seq_name = dir_name
        chunked = False
        if chunk_reg.match(dir_name):
            seq_name = dir_name[0:len(dir_name)-4]
            chunked = True
        if not (seq_name in status):
            status[seq_name] = {
                'chunked': chunked,
                'n_chunks': 1,
                'n_images': n_imgs,
                'chunk_size': n_imgs
            }
        else:
            status[seq_name]['n_chunks'] += 1
            status[seq_name]['n_images'] += n_imgs
    format_str = '{:<30}{:<20}{:<10}{:<20}{:<20}'
    print(format_str.format(*header))
    for seq_name in status:
        print(format_str.format(seq_name,
            status[seq_name]['n_images'],
            str(status[seq_name]['chunked']),
            status[seq_name]['n_chunks'],
            status[seq_name]['chunk_size']))

@root_cmd.command()
@click.option('--images', type=click.Path(), help='Add images from a directory containing a sequence of images.')
@click.option('--video', type=click.Path(), help='Add images from a video file.')
@click.argument('seq-name', type=str, required=True)
@click.option('--chunk-size', type=int, default=0, show_default=True, help='Divide the whole sequence into several chunks to reduce the memory usage during training. 0 for no divisions.')
def add(images, video, seq_name, chunk_size):
    '''Add a new image sequence to the workspace.
    '''
    # Avoid existances of --images and --video at the same time.
    if images and video:
        print('Only one of --images and --video should be specified. Aborted.')
        return
    # Copy images from --images to CityScapes/val/Dataset/Images.
    # Chunk the images if needed.
    if images:
        if not chunk_size:  # If chunk_size is 0, copy to only one directory.
            dir_seq = os.path.join(PATH_IMAGES, seq_name)
            os.makedirs(dir_seq, exist_ok=True)
        img_fnames = os.listdir(images)
        img_fnames.sort()
        for frame_idx, fname in enumerate(img_fnames):
            if chunk_size and (frame_idx % chunk_size == 0):  # A new chunk.
                dir_seq = os.path.join(PATH_IMAGES, '{}-{:03d}'.format(seq_name, frame_idx // chunk_size))
                os.makedirs(dir_seq, exist_ok=True)
            fname_noext = os.path.splitext(fname)[0]
            img = cv2.imread(os.path.join(images, fname))
            # The images in CityScapes/val/Dataset/Images must be .jpg.
            cv2.imwrite(os.path.join(dir_seq, '{}.{}'.format(fname_noext, 'jpg')), img)
            print('\rLoading image {}'.format(fname), sep=' ', end='', flush=True)
    # Extract frames from --video to CityScapes/val/Dataset/Images.
    # Chunk the frames if needed.
    if video:
        if not chunk_size:  # If chunk_size is 0, copy to only one directory.
            dir_seq = os.path.join(PATH_IMAGES, seq_name)
            os.makedirs(os.path.join(PATH_IMAGES, seq_name), exist_ok=True)
        cap = cv2.VideoCapture(video)
        n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_idx = 0
        while (cap.isOpened()):
            ret, frame = cap.read()
            if not ret:
                break
            if chunk_size and (frame_idx % chunk_size == 0):
                dir_seq = os.path.join(PATH_IMAGES, '{}-{:03d}'.format(seq_name, frame_idx // chunk_size))
                os.makedirs(dir_seq, exist_ok=True)
            cv2.imwrite(os.path.join(dir_seq, '{:06d}.jpg'.format(frame_idx)), frame)
            print('\rLoading frame {}/{}'.format(frame_idx, n_frames - 1), sep=' ', end='', flush=True)
    print('Loading {} complete.'.format(seq_name))

@root_cmd.command()
@click.argument('seq-name', type=str, required=True)
def remove(seq_name):
    '''Remove a image sequence from the workspace.
    '''
    dir_name_reg = re.compile('^' + seq_name + '(-[0-9]{3})?$')
    n_delete = 0
    for dir_name in os.listdir(PATH_IMAGES):
        if dir_name_reg.match(dir_name):
            shutil.rmtree(os.path.join(PATH_IMAGES, dir_name))
            n_delete += 1
    if not n_delete:
        print('No sequences removed. Check if the sequence name is correct ({}).'.format(seq_name))
    else:
        print('Successfully remove the sequence {}'.format(seq_name))

@root_cmd.command()
@click.argument('seqs', nargs=-1)
@click.option('--all', is_flag=True, help='Run all sequences.')
@click.option('--output', type=click.Path(), help='Output directory.', default='', required=True)
@click.option('--model', type=click.Path(), help='Specify another model.')
@click.option('--n-iters', type=int, help='The number of training iterations. (Only works when --training is specified)', default=3, show_default=True)
@click.option('--training', is_flag=True, help='Peform training at the same time.')
@click.option('--interactive', is_flag=True, help='Perform interactive correction.')
def run(seqs, all, output, model, n_iters, training, interactive):
    '''Run annotation on a set of image sequences. To train a new model with the
    image sequences, please specify the --training option.
    '''
    # If the output directory is not empty, abort.
    if output == '':
        print('Output directory is required. Aborted.')
        return
    if os.path.exists(output) and len(os.listdir(output)) != 0:
        print("Output {} is not empty. Aborted.")
        return
    if not training:
        n_iters = 1
    if all and seqs:
        print('Attempt to run all sequences but seqs is specified. Aborted.')
        return

    # Convert seq names to dir names
    dir_names_all = os.listdir(PATH_IMAGES)
    dir_names = []
    for seq_name in seqs:
        regex = re.compile('^' + seq_name + '(-[0-9]{3})?$')
        for dir_name in dir_names_all:
            if regex.match(dir_name):
                dir_names.append(dir_name)

    if model:
        model = os.path.join(os.getcwd(), model)
    else:
        model = ''
    # cd to ./annotation and start the annotation main process.
    os.chdir('./annotation')
    try:
        shutil.rmtree('CityScapes/val/Dataset/Annotations')
        shutil.rmtree('CityScapes/val/Dataset/Categories')
        shutil.rmtree('CityScapes/val/Dataset/Entire_dataset')
        shutil.rmtree('CityScapes/val/Dataset/Info')
        shutil.rmtree('CityScapes/val/Dataset/RCNN_data')
    except:
        pass
    init_root_dirs.init_data('Entire_dataset', 0)
    create_dataset.copy_data()
    create_dataset.create_attributes()
    create_dataset.create_dataset_info(folders=dir_names)
    create_dataset.create_train()
    create_dataset.create_test()
    if not training:
        run_iteration(0, 1, model_path=model, dir_names=dir_names, eval_only=True)
    else:
        for i in range(n_iters):
            run_iteration(i, n_iters, model_path=model, dir_names=dir_names, interactive=interactive)
            if interactive:
                shutil.rmtree('CityScapes/val/Dataset/Annotations/Road_Objects')
                shutil.copytree('CityScapes/val/Dataset/Entire_dataset/Iter_{}/Detection/Json'.format(i),
                    'CityScapes/val/Dataset/Annotations/Road_Objects')
                input('Frame Distance = {}\nPlease correct the labels and press any key to continue.'.format(int(233 / 24 / 2 ** i)))
                shutil.rmtree('CityScapes/val/Dataset/Entire_dataset/Iter_{}/Detection/Json'.format(i))
                shutil.copytree('CityScapes/val/Dataset/Annotations/Road_Objects',
                    'CityScapes/val/Dataset/Entire_dataset/Iter_{}/Detection/Json'.format(i))

    # Annotation completes. Copy Smooth_label as the result to --output.
    os.chdir('../')
    os.makedirs(output, exist_ok=True)
    shutil.rmtree(output)
    shutil.copytree('annotation/CityScapes/val/Dataset/Entire_dataset/Iter_{}/Smooth_label'.format(n_iters - 1), output)
    if training:
        shutil.copy('annotation/CityScapes/val/Dataset/Entire_dataset/Iter_{}/Detector/Iter{}.pth'.format(n_iters - 1, n_iters - 1), os.path.join(output, 'model.pth'))

    print('All done')

def run_iteration(iter_id, n_iters, model_path='', dir_names=[], eval_only=False, interactive=False):
    clear_dir.main(model_path=model_path)
    rcnn_args = run_rcnn.convert_args()
    if iter_id > 0 and not eval_only:
        rcnn_args.train = True
        rcnn_args.test = False
        run_rcnn.main(rcnn_args)
    rcnn_args.train = False
    rcnn_args.test = True
    run_rcnn.main(rcnn_args)
    init_root_dirs.init_data('Entire_dataset', iter_id)
    generate_raw_ann_from_rcnn_results.main(model_path=model_path)
    generate_adaptive_detection.generate_ann()
    track_instances.main(videonames=dir_names)
    create_tubelets.init_tracklet(videonames=dir_names)
    create_tubelets.create_tubelet(videonames=dir_names)
    create_tubelets.smoothen_label(videonames=dir_names)
    filter_data.filter_data(videonames=dir_names)
    add_instances.run_trackers(videonames=dir_names)
    if iter_id > 0 and interactive:
        convert_tubelet_to_coco_format.create_train(only_use_true_gt=True)
    else:
        convert_tubelet_to_coco_format.create_train()
    convert_tubelet_to_coco_format.create_test()
    ulti.main(videonames=dir_names)

@root_cmd.command()
@click.option('-s', '--seq-name', type=str)
@click.option('-r', '--result-path', type=click.Path(), help='Play a result directory instead of a sequence.')
def play(seq_name, result_path):
    '''Play images sequences.
    '''
    if not seq_name and not result_path:
        print('Must specify one of seq_name or --result-path. Aborted')
        return

    path_seqs = []
    window_name = ''
    if seq_name:
        dir_name_reg = re.compile('^' + seq_name + '(-[0-9]{3})?$')
        for dir_name in os.listdir(PATH_IMAGES):
            if dir_name_reg.match(dir_name):
                path_seqs.append(os.path.join(PATH_IMAGES, dir_name))
        window_name = seq_name
    else:
        dir_visualize = os.path.join(result_path, 'Visualization')
        for dir_name in os.listdir(dir_visualize):
            path_seqs.append(os.path.join(dir_visualize, dir_name))
        window_name = result_path
    path_seqs.sort()
    for path_seq in path_seqs:
        img_fnames = os.listdir(path_seq)
        img_fnames.sort()
        for fname in img_fnames:
            path_img = os.path.join(path_seq, fname)
            img = cv2.imread(path_img)
            cv2.imshow(window_name, img)
            cv2.moveWindow(window_name, 0, 0)
            cv2.waitKey(33)
