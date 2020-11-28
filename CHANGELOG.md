# CHANGELOG

## 0.1.0

- Change the directory structure. All codes are put into `annotation` as a python package.

- Modify several orignal scripts in `annotation`.
    - Create a main function in `clear_dir.py`, `generate_raw_ann_from_rcnn_results.py`, `track_instances.py` and `ulti.py`.

    - `init_root_dirs.py` and `run_rcnn.py` receive arguments, which may have conflicts with the CLI. Modify them to accept non-existing arguments.

    - Modify `ulti.py` to draw images with `track_id`s.

- Add `cli.py` and `setup.py` to `annotation`.

    - `cli.py` is the main CLI interface implementation using `Click`.

        Now only two commands are avaliable, `run` and `show`.

- Add `.dockerignore`, `.gitignore`, `CHANGELOG.md`, `requirements.txt`.

- Add a directory `vendors` to place dependencies as submodules. Add `install.sh` to install dependencies.

- Remove the script `run.sh`. Now the annotation is run by a command line interface instead.

- Update files in `docker`.

    - VNC and SSH are both configured in the docker container.

    - Update `entrypoint.sh` to set up the environment after the container is fired.

    - Add `vnc.sh` to activate a vnc desktop.
