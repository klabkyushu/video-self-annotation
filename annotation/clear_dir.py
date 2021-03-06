import os
import ulti
import shutil

def main(model_path=''):
    ulti.copy_model(model_path=model_path)

    info = ulti.load_json()
    training_dir = info['training_dir']
    dataset_name = info['annotated_video']

    dir_input = os.path.join(training_dir, dataset_name)
    if os.path.exists(dir_input):
        shutil.rmtree(dir_input, ignore_errors=True)

    src = os.path.join(info['dataset_dir'], '../Initial_model/e2e_faster_rcnn_R_50_FPN_Xconv1fc_1x_gn.yaml')
    dst = os.path.join(info['training_dir'], 'e2e_faster_rcnn_R_50_FPN_Xconv1fc_1x_gn.yaml')
    shutil.copyfile(src, dst)

if __name__ == "__main__":
    main()
