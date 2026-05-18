# EXERCISE for Remote Sensing Course

This repository contains the exercices for the EPFL Remote Sensing Course. There are three options for executing the code:
1. On EPFL's virtual machines, available in the exercise classroom;
2. On your personal laptops;
3. Via a Noto link.

We recommend using options 1 or 2 for pedagogic purposes (see section 3 for more details on why).

## 1. Instructions for using EPFL's VM
Please select the `ENAC-SSIE-Ubuntu-20-04` Virtual Desktop Infrastructure (VDI) and then follow these steps:

1. [Download the RS2026 GitHub repository](https://github.com/ltelab/RS2026/archive/refs/heads/main.zip)

2. Unzip the `RS2026-main.zip` file and move the `RS2026` directory within the `/home/<your_username>/Desktop/myfiles/` directory.
   If your data are saved within the `/myfiles` directory, they will be available the next time you reconnect to the VDI. 

3. Open a terminal and activate the `lte` environment with:

```sh
micromamba activate lte
```
  
4. Then create the `lte` ipykernel for Jupyter Notebook with:

```sh
python -m ipykernel install --user --name=lte
```

5. Launch the Jupyter Notebook interface with `jupyter notebook` and open the
   `Exercise_6.ipynb` or `Exercise_7.ipynb` file within the `RS2026` directory.

6. To execute correctly the Jupyter Notebook, in the top menu bar select `Kernel` >  `Change Kernel... ` and switch the kernel from `Python 3 (ipykernel)` to `lte`.   

## 2. Instructions for using your own computer

Alternatively, you can clone the [RS2026 repository](https://github.com/ltelab/RS202) on your laptop and install the required environment using conda/mamba or micromamba:  

1. Go to the directory where you want to clone the repository. As an example:

```sh
cd /home/ghiggi/courses
```

2. Clone this repository:

```sh
git clone git@github.com:ltelab/RS2026.git
cd RS2026
```

3. Install the dependencies using conda:

```sh
micromamba env create -f environment.yml
```

4. Activate the `lte` conda environment:

```sh
micromamba activate lte
```

4. Create the `lte` Jupyter Notebook environment with:

```sh
python -m ipykernel install --user --name=lte
```

5. Launch the Jupyter Notebook interface with `jupyter notebook` and open the
   `Exercise_6.ipynb` or `Exercise_7.ipynb` file within the `RS2026` directory. 

6. To execute correctly the Jupyter Notebook, in the top menu bar select `Kernel` >  `Change Kernel... ` and switch the kernel from `Python 3 (ipykernel)` to `lte`.   

If you want to use the VScode interface for executing the Jupyter notebook, execute steps 1 to 5, then install Python and Jupyter extensions in VScode. Navigate to the repository using VScode's terminal, then open the .ipynb files. Click the kernel selector on the top-right corner of the notebook and select the `lte` environment. 

Note that the installation of the dependencies on your laptop might cause conflicts; the latest version of the required packages can be installed using the following command:

```sh
conda install numpy pandas xarray dask rasterio rioxarray scikit-learn matplotlib-base seaborn colorcet pywavelets pillow jupyter
```

In case you encounter such issues and cannot fix them, please contact the TA team.


## 3. Instructions for using Noto

To run the exercise, you can also use **noto.epfl.ch** JuypterLab service (more details [here](https://www.epfl.ch/education/educational-initiatives/cede/teaching-interactively/jupyter-notebooks-for-education/one-click-access-to-jupyter-notebooks-online-with-noto/)). This allows you to run the code directly without having to do any environment setup. We do not recommend this option, as we think that setting up an environment is a good thing to learn; but we provide this option as a backup if you encounter issues with option 1 and 2.

1. Click on the following links to access the Noto environements:
   -  [Exercise 6](https://noto.epfl.ch/hub/user-redirect/git-pull?repo=https%3A%2F%2Fgithub.com%2Fltelab%2FRS2026&urlpath=lab%2Ftree%2FRS2026%2Fexercise_6%2FExercise_6.ipynb&branch=main&depth=1)

2. Once you have access to the EPFL Noto platform, click on the `Exercise_6.ipynb` to start the notebook.

----------------
And now ... happy coding :-)
