# Submission Tutorial (Singularity)
This page will assist you in submitting a Singularity container for the BraTS-Reg challenge.
<!-- TOC -->
- [1. Build your model](#1-build-your-model)
  - [Input files](#input-files)
  - [Output files](#output-files)
  - [Sample script (python)](#sample-script-python)
  - [Example usage](#example-usage)
- [2. Set up singularity](#2-set-up-singularity)
- [3. Create a Singularity Definition File](#3-create-a-singularity-definition-file)
  - [`Bootstrap` and `From`](#bootstrap-and-from)
  - [`%files`](#%files)
  - [`%post`](#%post)
  - [`%runscript`](#%runscript)
- [4. Build a singularity container](#4-build-a-singularity-container)
  - [Set up your working directory](#set-up-your-working-directory)
  - [Build the container from definition file](#build-the-container-from-definition-file)
- [5. Locally test your singularity container](#5-locally-test-your-singularity-container)
  - [For CPU](#for-cpu)
  - [For GPU](#for-gpu)
- [6. Upload your singularity container](#6-upload-your-singularity-container)
  - [Verify the container image was successfully pushed and make it accessible](#verify-the-container-image-was-successfully-pushed-and-make-it-accessible)

<!-- /TOC -->

## 1. Build your model
This section will describe how to create your model and how it must take an input and output directory as parameters.
### Input files
- All input files will be mounted in a directory called `/input` in the working directory of the container.
- Arrange the `input` folder as follows:

  ```
  input/
  ├── BraTSReg_001
  │   ├── BraTSReg_001_00_0000_flair.nii.gz
  │   ├── BraTSReg_001_00_0000_t1ce.nii.gz
  │   ├── BraTSReg_001_00_0000_t1.nii.gz
  │   ├── BraTSReg_001_00_0000_t2.nii.gz
  │   ├── BraTSReg_001_01_0106_flair.nii.gz
  │   ├── BraTSReg_001_01_0106_landmarks.csv
  │   ├── BraTSReg_001_01_0106_t1ce.nii.gz
  │   ├── BraTSReg_001_01_0106_t1.nii.gz
  │   └── BraTSReg_001_01_0106_t2.nii.gz
  └── BraTSReg_002
      ├── BraTSReg_002_00_0000_flair.nii.gz
      ├── ...
  ```
  i.e. the `input` folder should contain the individual folders for the subjects named as `BraTSReg_xxx`, where `xxx` is a three-digit ID (eg., 150, 151, etc.). Each subject folder will contain: t1, t1ce, flair, t2 scans for the baseline, follow-up and the follow-up landmarks.

### Output files
- All output files should be written into a directory called `/output` in the working directory of the container.
- Your models will be writing your output files with the following names:
  - landmark output - should be called `BraTSReg_xxx.csv` where `BraTSReg_xxx` is the subject id
  - determinant of jacobian of deformation field - should be called `BraTSReg_xxx.nii.gz`

 where `BraTSReg_xxx` is the subject id.
- So, for the above example `input/` structure, your `output/` folder should be like:
```
output/
├── BraTSReg_001.csv
├── BraTSReg_001.nii.gz
├── BraTSReg_002.csv
├── BraTSReg_002.nii.gz
├── ...
```

### Sample script (python)
Here is an example of what a python script `my_script.py` might look like:
```
import argparse
import os
import nibabel as nib
import glob
import tensorflow as tf
from tensorflow.python.client import device_lib

# You can first check what devices are available to the singularity
# if you are using a GPU, then it should show up in the available devices
print("* Listing available devices using tensorflow.python.client.device_lib.list_local_devices():")
print(device_lib.list_local_devices())


# Parse the input arguments
parser = argparse.ArgumentParser(description='Code for running Registration for BraTS_Reg challenge')
parser.add_argument('-i', '--input', type=str, default="/input", help='Provide full path to directory that contains input data')
parser.add_argument('-o', '--output', type=str, default="/output", help='Provide full path to directory where output will be written')

args = vars(parser.parse_args())

print("* Received the following arguments =", args) # {'input': '/input', 'output': '/output'}

input_path = os.path.abspath(args["input"])
output_path = os.path.abspath(args["output"])

print(f"* Found following data in the input path {input_path}=", os.listdir(input_path)) # Found following data in the input path /input= ['BraTSReg_001', 'BraTSReg_002']
print("* Output will be written to=", output_path) # Output will be written to= /output

# Now we iterate through each subject folder under input_path
for subj_path in glob.glob(os.path.join(input_path, "BraTS_Reg*")):
	subj = os.path.basename(subj_path)
	print(f"Now performing registration on {subj}") # Now performing registration on BraTSReg_001

	# Read in your data
	input_df = nib.load(os.path.join(subj_path, f"{subj}_00_0000_t1ce.nii.gz")).get_fdata()

	print(input_df.shape) # (240, 240, 155)

	# # Disclaimer: Note that following functions -- loadmodel, calculate_landmark, calculate_jacobian, write -- are not real python functions, but are examples here.

	# # Read in your trained model
	# model = loadmodel("/usr/local/bin/model.hdf5")

	# # Make your prediction segmentation file for case BraTSReg_001

	# ## 1. calculate the output landmark points
	# output_landmark = calculate_landmark(model, input_df)

	# ## write your output_landmark to the output folder as BraTSReg_001.csv
	# write(output_landmark, os.path.join(args["output"], f"{subj}.csv"))

	# ## 2. calculate the determinant of jacobian of the deformation field
	# output_detj = calculate_jacobian(model, input_df)

	# ## write your output_detj to the output folder as BraTSReg_001.nii.gz
	# write(output_detj, os.path.join(args["output"], f"{subj}.nii.gz"))
  ```
### Example usage
Here is an example of how to use the above script to adhere to the stipulated input and output folder structures described above:
```
python my_script.py --input /input --output /output
```
## 2. Set up singularity
For setting up singularity, check out: https://sylabs.io/guides/3.0/user-guide/installation.html .
Note that singularity runs on Linux natively and can be run on Windows and Mac through virtual machines (VMs).

## 3. Create a Singularity Definition File
This section will describe how to write your [Definition file](https://sylabs.io/guides/3.7/user-guide/definition_files.html). A Singularity Definition File (or “def file” for short) is like a set of blueprints explaining how to build a custom container. It includes specifics about the base OS to build or the base container to start from, software to install, environment variables to set at runtime, files to add from the host system, and container metadata. As such, the singularity container is a self-contained execution environment that will allow the Challenge organizers to run and reproduce your results.

Here is an example Definition File file using the `my_script.py` created above:
```
# Start from this Docker image
# Start from this Docker image
Bootstrap: docker
From: nvidia/cuda:10.0-cudnn7-devel-ubuntu16.04

%post
  # Install general dependencies
  apt-get update && apt-get install -y --no-install-recommends build-essential cmake git unzip zip gcc pylint curl wget tar \
      openjdk-8-jdk zlib1g-dev bash-completion libcurl4-openssl-dev libreadline-gplv2-dev libncursesw5-dev \
      libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libhdf5-serial-dev libhdf5-dev liblzma-dev libffi-dev
  apt-get clean

  # Install Python 3.7.4
  cd /usr/src
  wget https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tar.xz
  tar xJf Python-3.7.4.tar.xz
  cd Python-3.7.4
  ./configure --enable-shared LDFLAGS="-Wl,-rpath /usr/local/lib"
  make
  make install

  # Install python packages
  pip3 install --no-cache-dir --upgrade pip
  pip3 install --no-cache-dir --upgrade numpy nibabel tensorflow-gpu==1.15.0

  # Set up environment
  echo "export PATH=/usr/local/cuda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" >> /environment
  echo "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib:/usr/local/cuda/lib64:/usr/local/cuda/lib64/stubs:/usr/local/cuda/extras/CUPTI/lib64" >> /environment
  cd /usr/local/cuda/lib64/stubs
  ln -s libcuda.so libcuda.so.1

  # Clean up
  rm -rf /usr/src/*

# Copy your files into Singularity container (model+script)

%files
  # place your python script inside the container
  my_script.py /usr/local/bin/my_script.py

  # place your model file inside the container
  my_model.hdf5 /usr/local/bin/my_model.hdf5

%runscript

    exec python3 /usr/local/bin/my_script.py
```
The rest of this documentation will go through each line in the Definition File example and explain its purpose.

### `Bootstrap` and `From`
The `Bootstrap` keyword is required for every type of build. It determines the _bootstrap agent_ that will be used to create the base operating system you want to use. For example, the `docker` bootstrap agent will pull docker layers from Docker Hub as a base OS to start your image.
The `From` keyword specifies which docker image will be used as the base image for the singularity container. To read more, check out the following link from singularity's source documentation: https://sylabs.io/guides/3.7/user-guide/definition_files.html#header

### `%files`
The `%files` section allows you to copy files into the container. Its general form is:
```
%files [from <stage>]
    <source> [<destination>]
    ...
```
Each line is a `<source>` and `<destination>` pair. The `<source>` is either:
1. A valid path on your host system
2. A valid path in a previous stage of the build

while the `<destination>` is always a path into the current container. If the `<destination>` path is omitted it will be assumed to be the same as `<source>`. To read more, check out the following link from singularity's source documentation: https://sylabs.io/guides/3.7/user-guide/definition_files.html#files

### `%post`
This section is where you can download files from the internet with tools like `git` and `wget`, install new software and libraries, write configuration files, create new directories, etc.

In our example definition file above, we use this section to:
1. Install general dependencies using `apt-get`
2. Install python and python packages
3. Configure environment variables

To read more, check out the following link from singularity's source documentation: https://sylabs.io/guides/3.7/user-guide/definition_files.html#post

### `%runscript`
The `%runscript` section specifies what gets executed when your singularity container is run. In
this example, we want to run `my_script.py` that we copied into `/usr/local/bin/`.
To read more, check out the following link from singularity's source documentation: https://sylabs.io/guides/3.7/user-guide/definition_files.html#runscript

## 4. Build a singularity container
This section describes how to create your singularity container. You will need:
1. your BraTS_Reg team name
2. Definition file for the container

### Set up your working directory
- Move your Definition file and all files you are copying into your Singularity container (e.g., your script, model) into the same directory.
- Make the above directory your current working directory.

### Build the container from definition file
The basic syntax for [building a singularity container from a definition file](https://sylabs.io/guides/3.7/user-guide/build_a_container.html#building-containers-from-singularity-definition-files) is:
```
sudo singularity build BraTS_Reg_<team_name>.sif <path to definition file>
```
where:
- `<team_name>`: Your BraTS_Reg team name (please replace any special character with underscore  `_`)
- `<path to definition file>`: Specify the path to your definition file. This should be `./<your_def_file.def>` since the definition file should be in your current working directory.

## 5. Locally test your singularity container
This section describes how to test and run your singularity container locally to test your model.
After you [build your singularity container](#4-build-a-singularity-container), you can run your container locally to check that your model will correctly run as a singularity container.

### For CPU
```
singularity run -B "/your/input/folder/":"/input" -B "/your/output/folder/":"/output" BraTS_Reg_<team_name>.sif
```
### For GPU
First, ensure that you have access to a NVIDIA GPU. For example, if you are running it on a High Performance Cluster (HPC), make sure you are logged into a GPU node. Then run:
```
singularity run --nv -B "/your/input/folder/":"/input" -B "/your/output/folder/":"/output" BraTS_Reg_<team_name>.sif
```
where the `--nv` flag will setup the container’s environment to use an NVIDIA GPU and the basic CUDA libraries to run a CUDA enabled application. For further details on requirements for the `--nv` flag and examples, please check out the source documentation: https://sylabs.io/guides/3.5/user-guide/gpu.html

If you have a job submission script on HPC, it should look something like (following example is for a SLURM scheduler):
```
#!/bin/bash
#SBATCH --mail-type=BEGIN,END
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --gres=gpu:1
#SBATCH --mem=8gb
#SBATCH --time=2:00:00
#SBATCH --error=joblogs/%j.err
#SBATCH --output=joblogs/%j.out

module load singularity
singularity run --nv -B "/your/input/folder":"/input" -B "/your/output/folder":"/output" BraTS_Reg_<team_name>.sif
```

## 6. Upload your singularity container
This section describes how to[ push your locally built singularity container](https://sylabs.io/guides/3.7/user-guide/cloud_library.html) up into the "Sylabs Cloud Library".
1. [Make an account on sylabs](https://sylabs.io/guides/3.7/user-guide/cloud_library.html#make-an-account). Keep a note of your username (`your_sylab_username`), you will need this in step 3 below to push the container.
2. You will need an access token to login into your account and push the container. To create an access token, [follow these steps](https://sylabs.io/guides/3.7/user-guide/cloud_library.html#creating-a-access-token). Once you have the access token, run `singularity remote login` in your terminal and paste the access token at the prompt:
```
vagrant@vagrant:~$ singularity remote login
Generate an access token at https://cloud.sylabs.io/auth/tokens, and paste it here.
Token entered will be hidden for security.
Access Token:
INFO:    Access Token Verified!
INFO:    Token stored in /home/vagrant/.singularity/remote.yaml
```
3. Once your access token is verified, you can push the container image as follows:
```
 singularity push -U BraTS_Reg_<team_name>.sif library://<your_sylab_username>/BraTS_Reg/BraTS_Reg_<team_name>[:<tag>]
```
where,

  `BraTS_Reg_<team_name>.sif`: the locally built singularity container image <br/>
  `<your_sylab_username>`: your username created in step 1 <br/>
  `<tag>`: Optional. If no tag is specified, a `:latest` tag is added to your image. In general, taggin the file as latest is fine. However, let’s assume you have a newer version of your container (v0.1), and you want to push that container without deleting your `:latest` container, then you can add a version tag to that container, like so:
  ```
   singularity push -U BraTS_Reg_<team_name>.sif library://<your_sylab_username>/BraTS_Reg/BraTS_Reg_<team_name>:0.1
  ```
  When your container is being pushed you should see a progress-bar like this:

  ```
  vagrant@vagrant:~$ singularity push -U BraTS_Reg_<team_name>.sif library://<your_sylab_username>/BraTS_Reg/BraTS_Reg_<team_name>
  WARNING: Skipping container verification
  1.2MiB / 1.1GiB [========----------------------------------------------------------------] 1 % 372.8 KiB/s 51m41s
  ```
  When it's over, you should see that its 100% complete:
  ```
  vagrant@vagrant:~$ singularity push -U BraTS_Reg_<team_name>.sif library://<your_sylab_username>/BraTS_Reg/BraTS_Reg_<team_name>
  WARNING: Skipping container verification
  1.1GiB / 1.1GiB [==============================================================================] 100 % 1.1 MiB/s 0s
  ```

### Verify the container image was successfully pushed and make it accessible
If the singularity container was successfully pushed, it should show up under: `https://cloud.sylabs.io/library/<your_sylab_username>`. **Make sure your container is set to Public on the sylab website. If it is Private, the organizers will not be able to access it.**
