""" Various utilities for cloning the AAA repository. """


import os
import shutil
import requests
import zipfile
import math
import tqdm
from . import utils


def detect_if_contents_present(working_directory, import_files):
    """
    Detect if the specified files are present in a directory.
    :param working_directory: the working directory to which the contents should be cloned.
    :param import_files: the files that are checked for.
    :return: whether the repository should be cloned.
    """
    if not os.path.exists(working_directory):
        return True
    do_clone = False
    for file in import_files:
        if file not in os.listdir(working_directory):
            do_clone = True
    return do_clone


def clone_contents(aaa_path, contents_zip, origin, disable_stdout_progress=False, block_size=1024):
    """
    Clone the AAA repository.
    :param block_size:
    :param aaa_path: the path to the AAA directory.
    :param contents_zip: the path to the downloaded zip file.
    :param origin: the origin URL.
    :param disable_stdout_progress: disable stdout progress bar/tqdm (TODO)
    """
    with open(os.path.join(aaa_path, contents_zip), "wb") as f:
        response = requests.get(origin, stream=True)
        total_length = response.headers.get('content-length')
        if disable_stdout_progress or total_length is None:
            f.write(response.content)
        else:
            total_length = int(total_length) // block_size
            for data in tqdm.tqdm(response.iter_content(block_size), total=math.ceil(total_length), unit='KB'):
                f.write(data)


def extract_contents(aaa_path, contents_zip, repo_path, tmp_output_directory, output_directory):
    """
    Extracts the contents of the .zip file to a path.
    :param aaa_path: the path to the AAA directory.
    :param contents_zip: the path to the downloaded zip file.
    :param repo_path: the name of the branch/directory to extract.
    :param tmp_output_directory: the temporary output directory.
    :param output_directory: the directory to extract the contents to.
    """
    with zipfile.ZipFile(os.path.join(aaa_path, contents_zip), 'r') as origin_zip:
        origin_zip.extractall(os.path.join(aaa_path, tmp_output_directory))
    try:
        shutil.move(os.path.join(aaa_path, tmp_output_directory, repo_path),
                    os.path.join(aaa_path, output_directory))
    except shutil.Error:
        pass


def move_from_contents(aaa_path, repo_directory, import_files):
    """
    Moves files from a specified directory.
    :param aaa_path: the path to the AAA directory.
    :param repo_directory: the repository contents directory.
    :param import_files: the files to import.
    """
    utils.create_dir_if_not_exists(os.path.join(aaa_path, repo_directory))
    for file, name in import_files.items():
        print(os.path.join(aaa_path, repo_directory, file))
        shutil.move(os.path.join(aaa_path, repo_directory, file), os.path.join(aaa_path, name))
