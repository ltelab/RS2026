# EXERCISE for Remote Sensing Course

This repository contains the exercices for the EPFL Remote Sensing Course.

The exercises can be executed directly on the EPFL VMware Horizon platform. 
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
   And now ... happy coding :-)


----------------

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
   And now ... happy coding :-)


----------------


Note that the installation of the dependencies on your laptop might cause conflicts; in case you encounter such issues and cannot fix them, please contact the TA team.

The latest version of the required packages can be installed using the following command:

```sh
conda install numpy pandas xarray dask rasterio rioxarray scikit-learn matplotlib-base seaborn colorcet pywavelets pillow jupyter
```
>>>>>>> bd4c3c1 (Update README.md)
