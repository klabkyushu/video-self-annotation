import click
import os
import cv2
import shutil

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
@click.option('--images', type=click.Path(), help='Add images from a directory containing a sequence of images.')
@click.option('--video', type=click.Path(), help='Add images from a video file.')
@click.option('--seq-name', type=str, help='Specify another name other than the folder/video name of the new added sequence.')
@click.option('--chunk-size', type=int, default=100, show_default=True, help='Divide the whole sequence into several chunks to reduce the memory usage. 0 for no divisions.')
@click.option('--output', type=click.Path(), help='Output directory.', required=True)
@click.option('--n-iters', type=int, help='The number of iterations', default=4, show_default=True)
@click.option('--evaluation', is_flag=True, help='Evaluation only.')
def run(images, video, seq_name, chunk_size, output, n_iters, evaluation):
    # If the output directory is not empty, abort.
    if os.path.exists(output) and len(os.listdir(output)) != 0:
        print("Output {} is not empty. Aborted.")
        return
    # Avoid existances of --images and --video at the same time.
    if images and video:
        print('Only one of --images and --video should be specified. Aborted.')
        return
    # Copy images from --images to CityScapes/val/Dataset/Images.
    # Chunk the images if needed.
    if images:
        if not seq_name:  # If no --seq-name, make the directory name be seq_name.
            seq_name = os.path.basename(os.path.normpath(images))
            print(seq_name)
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
        if not seq_name:  # If no --seq-name, make the video filename be seq_name.
            seq_name = os.path.splitext(os.path.basename(os.path.normpath(video)))[-2]
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

    # cd to ./annotation and start the annotation main process.
    os.chdir('./annotation')
    if evaluation:
        run_iteration(n_iters - 1, n_iters, eval_only=True)
    else:
        shutil.rmtree('CityScapes/val/Dataset/Entire_dataset')
        init_root_dirs.init_data('Entire_dataset', 0)
        create_dataset.copy_data()
        create_dataset.create_attributes()
        create_dataset.create_dataset_info()
        create_dataset.create_train()
        create_dataset.create_test()
        for i in range(n_iters):
            run_iteration(i, n_iters)

    # Annotation completes. Copy Smooth_label as the result to --output.
    os.chdir('../')
    os.makedirs(output, exist_ok=True)
    shutil.rmtree(output)
    shutil.copytree('annotation/CityScapes/val/Dataset/Entire_dataset/Iter_{}/Smooth_label'.format(n_iters - 1), output)

    print('All done')

def run_iteration(iter_id, n_iters, eval_only=False):
    clear_dir.main()
    rcnn_args = run_rcnn.convert_args()
    if iter_id > 0 and not eval_only:
        rcnn_args.train = True
        run_rcnn.main(rcnn_args)
    rcnn_args.train = False
    rcnn_args.test = True
    run_rcnn.main(rcnn_args)
    init_root_dirs.init_data('Entire_dataset', iter_id)
    generate_raw_ann_from_rcnn_results.main()
    generate_adaptive_detection.generate_ann()
    track_instances.main()
    create_tubelets.init_tracklet()
    create_tubelets.create_tubelet()
    create_tubelets.smoothen_label()
    filter_data.filter_data()
    add_instances.run_trackers()
    convert_tubelet_to_coco_format.create_train()
    convert_tubelet_to_coco_format.create_test()
    ulti.main()

@root_cmd.command()
@click.option('-i', '--input', type=click.Path(), help='The output directory generated by run.', required=True)
def show(input):
    '''show displays the result images sequence generated by run.
    '''
    dir_visualize = os.path.join(input, 'Visualization')
    seqs = os.listdir(dir_visualize)
    seqs.sort()
    for seq in seqs:
        path_seq = os.path.join(dir_visualize, seq)
        img_fnames = os.listdir(path_seq)
        img_fnames.sort()
        for fname in img_fnames:
            path_img = os.path.join(path_seq, fname)
            img = cv2.imread(path_img)
            cv2.imshow('Visualization', img)
            cv2.waitKey(5)
