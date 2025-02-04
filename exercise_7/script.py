#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 15:34:06 2022

@author: ghiggi
"""
# %gui qt5   # this required in jupyter notebook for napari
import os 
import glob 
import napari
import rioxarray
import rasterio 
import sklearn 
import colorcet
import matplotlib
import pandas as pd
import numpy as np
import xarray as xr
import seaborn as sns
import matplotlib.pyplot as plt 

# ---------------------------------------------------------------------.
# Define directory and filepaths
data_dir = "/home/ghiggi/Courses/RS2022/exercice_6/Data/Australia_2019"

bands_fpattern =  "*(Raw).tiff"
true_color_fname = "2019-05-15-00_00_2019-05-15-23_59_Sentinel-2_L2A_True_color.tiff"
labels_fname = "2019-05-15-00_00_2019-05-15-23_59_Sentinel-2_L2A_Scene_classification_map.tiff" 

band_fpaths = sorted(glob.glob(os.path.join(data_dir, bands_fpattern)))
labels_fpath = os.path.join(data_dir, labels_fname)
true_color_fpath = os.path.join(data_dir, true_color_fname)

# ---------------------------------------------------------------------.
# Load true color 
da_true_color = xr.open_dataset(true_color_fpath, engine="rasterio", default_name="true_color")['true_color']
da_true_color = da_true_color.compute()
da_true_color.plot.imshow()

# Load all bands
bands = [os.path.basename(fpath).split("_")[6] for fpath in band_fpaths]
da_bands = xr.open_mfdataset(band_fpaths, engine="rasterio", concat_dim="band", combine="nested")['band_data']
da_bands = da_bands.assign_coords({'band': bands})
da_bands.plot.imshow(col="band", col_wrap=3, cmap="gray")

# ---------------------------------------------------------------------.
# Load labels RGB
da_labels_RGB = xr.open_dataset(labels_fpath, engine="rasterio", default_name="labels")['labels']
da_labels_RGB.plot.imshow()

# Retrieve labels id 
da_stack = da_labels_RGB.stack(id=(['x','y'])).transpose(...,"band").astype(object).sum("band").astype(float)
da_stack.data = np.digitize(da_stack.data, np.unique(da_stack.data))
da_labels = da_stack.unstack('id').transpose('y','x')
da_labels.plot.imshow()

np.unique(da_labels.data, return_counts=True) # 11 values 
plt.hist(da_labels.data.flatten())

# Establish label clases 
viewer = napari.view_image(da_labels,name="labels_id", colormap="gist_earth")
viewer.add_image(da_true_color.transpose(...,"band"), rgb=True, name="true_color")
viewer.add_image(da_labels_RGB.transpose(...,"band"), rgb=True, name="labels_RGB")

# TODO: REASSIGN 
labels_dict = {'No Data': 1,
               "Saturated or defective pixels": 5,
               'Dark features / Shadows': 2, 
               'Cloud shadows': 3, 
               'Vegetation': 4,
               'Not vegetated': 8, 
               'Water': 5, 
               'Unclassified': 6, 
               'Cloud medium probability': 9,
               'Cloud high probability': 11,
               'Thin Cirrus': 7,
               'Snow or Ice': 10,
}
labels_id_dict = {v: k for k,v in labels_dict.items()}

# ---------------------------------------------------------------------.
### Data preprocessing 
# Merge all data into xr.Dataset
ds_bands = da_bands.to_dataset("band")
ds_full = ds_bands.copy()
ds_full['labels_id'] = da_labels

# Conversion to pandas.DataFrame 
df_full = ds_full.to_dataframe()
df_full = df_full.drop(columns="spatial_ref")
df_full['labels'] = df_full['labels_id'].apply(lambda x: labels_id_dict[x])
print(df_full)

# Reshape to long format 
df_long = df_full.melt(value_vars=bands, id_vars="labels", var_name="channel", value_name="value")
print(df_long)

#-----------------------------------------------------------------------------.
#### Channels EDA 
# Distribution per class
df_subset = df_full[df_full['labels'].isin(["Vegetation", "Not vegetated", "Water","Cloud high probability"])]
sns.violinplot(x='labels', y='B01', data=df_subset)

df_long_subset = df_long[df_long['labels'].isin(["Vegetation", "Not vegetated","Water","Cloud high probability"])]
sns.violinplot(x='labels', y='value', hue="channel", data=df_long_subset)

# g = sns.FacetGrid(df_long_subset, col="channel")
# g.map(sns.violinplot, x='labels', y='value')


# g = sns.FacetGrid(df_subset, col="channel")
# g.map(sns.scatterplot, 'B01', 'B02')

#-----------------------------------------------------------------------------.
#### Compute correlation matrix 
corrMatrix = df_full[bands].corr()
print (corrMatrix)

# Display correlation matrix
f, ax = plt.subplots(figsize =(9, 8)) 
ax = sns.heatmap(
    corrMatrix, 
    # vmin=-1, vmax=1, center=0,
    cmap=sns.diverging_palette(20, 220, n=200),
    # linewidths = 0.1, # for white border of each cell 
    square=True,
    annot=False)
ax.set_xticklabels(
    ax.get_xticklabels(),
    rotation=45,
    horizontalalignment='right')
plt.show()

# Hiearchical clustering of correlation matrix  
cg = sns.clustermap(corrMatrix, 
                    cmap = sns.diverging_palette(20, 220, n=200),
                    linewidths = 0.1); 
ax = plt.setp(cg.ax_heatmap.yaxis.get_majorticklabels(), rotation = 0) 
plt.show()


#-----------------------------------------------------------------------------.
#### Scale data (Normalize to 0-1)
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
scaler = scaler.fit(df_full[bands])

X_norm = scaler.transform(df_full[bands])

#-----------------------------------------------------------------------------.
#### Apply PCA 
from sklearn.decomposition import PCA 
pca = PCA(n_components=len(bands))
pca.fit(X_norm)

# ---------------------------------------------------------------------.
# Printing some parameters
components_ = pca.components_
explained_variance_ = pca.explained_variance_
print(components_.shape)
print(explained_variance_)

# ---------------------------------------------------------------------.
# Plotting variance explained by each component
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 4))
ax.grid(ls=':', c='gray', alpha=0.4)
ax.plot(explained_variance_, ls='--', marker='o', c='tab:blue')
ax.set_xlabel('Component number')
ax.set_ylabel('Explained variance')
ax.set_title('Explained variance per PCA component')
plt.tight_layout()

# ---------------------------------------------------------------------.
# Retrieve PCA latent componenents
X_latent = pca.transform(X_norm)
df_latent = pd.DataFrame(X_latent, index = df_full.index)
ds_latent = df_latent.to_xarray()

# ---------------------------------------------------------------------.
# Visualize latent components 
ds_latent.to_array(dim="PC").plot.imshow(col="PC", col_wrap=3, cmap="gray")

# ---------------------------------------------------------------------.
# Select first 3 components and plot the RGB PCA composite
ds_PCA_RGB = ds_latent[[0,1,2]].to_array(dim="RGB")
ds_PCA_RGB.plot.imshow()

# ---------------------------------------------------------------------.
# Reconstruct multispectral image with 3 PC
import copy
pca_3 = copy.copy(pca)
pca_3.components_ = pca_3.components_[0:3,:]
X_rec = scaler.inverse_transform(pca_3.inverse_transform(X_latent[:, 0:3]))
df_rec = pd.DataFrame(X_rec, index = df_full.index)
df_rec.columns = bands
ds_rec = df_rec.to_xarray()

# Visualize reconstructed channels 
ds_rec.to_array(dim="bands").plot.imshow(col="bands", col_wrap=3, cmap="gray")

# Difference between original and reconstructed 
ds_difference = ds_bands - ds_rec 
ds_difference.to_array(dim="bands").plot.imshow(col="bands", col_wrap=3)

#-----------------------------------------------------------------------------.
#### Running k-means
from sklearn.cluster import KMeans

n_clusters = 5
kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(X_norm)
print(kmeans)

# Retrieve clusters
X_cluster = kmeans.predict(X_norm)
df_cluster = pd.DataFrame({'cluster': X_cluster}, index = df_full.index)
ds_cluster = df_cluster.to_xarray()
ds_cluster['cluster'].plot.imshow()

np.unique(ds_cluster['cluster'].data, return_counts=True)

# ---------------------------------------------------------------------.
# Define categorical colormap 
bounds = np.arange(0, n_clusters+1, dtype='int')
norm =  matplotlib.colors.BoundaryNorm(boundaries=bounds, ncolors=n_clusters)
cmap = cmap = plt.get_cmap("Set1", n_clusters)

cbar_ticks = np.arange(0, n_clusters) + 0.5 
cbar_ticklabels = ['class :%d' % i for i in range(n_clusters)] 
cbar_kwargs = {'ticks': cbar_ticks}

p = ds_cluster['cluster'].plot.imshow(norm=norm, cmap=cmap, cbar_kwargs=cbar_kwargs)
p.colorbar.set_ticklabels(cbar_ticklabels)

# ---------------------------------------------------------------------.
# Visualize clusters in napari 
viewer = napari.view_image(ds_cluster['cluster'], name="clusters_id", colormap="gist_earth")
viewer.add_image(da_true_color.transpose(...,"band"), rgb=True, name="true_color")
viewer.add_image(da_labels_RGB.transpose(...,"band"), rgb=True, name="labels_RGB")

# ---------------------------------------------------------------------.
# Compute number pixels forest 
np.sum(ds_cluster['cluster'].data == 0)
np.unique(ds_cluster['cluster'].data, return_counts=True)

#-----------------------------------------------------------------------------.
################
#### Part 2 ####
################
# Define directory and filepaths
data_dir = "/home/ghiggi/Courses/RS2022/exercice_6/Data/Lake_Lucerne"

bands_fpattern =  "Landsat_sub_[0-9].tif"
true_color_fname = "Landsat_sub_RGB.tif"
region_bands_fname = "Landstat_4cantons.tif"
labels_fid_fname = "Rasterized_fid.tif" 
labels_mcid_fname = "Rasterized_mcid.tif" 

band_fpaths = sorted(glob.glob(os.path.join(data_dir, bands_fpattern)))
true_color_fpath = os.path.join(data_dir, true_color_fname)
region_bands_fpath = os.path.join(data_dir, region_bands_fname)
labels_fid_fpath = os.path.join(data_dir, labels_fid_fname)
labels_mcid_fpath = os.path.join(data_dir, labels_mcid_fname)

# ---------------------------------------------------------------------.
# Load true color 
da_true_color = xr.open_dataset(true_color_fpath, engine="rasterio", default_name="true_color")['true_color']
da_true_color = da_true_color/255
da_true_color.plot.imshow()

# Load bands
bands = ['C' + str(i) for i in range(1,8)]
da_bands = xr.open_mfdataset(band_fpaths, engine="rasterio", concat_dim="band", combine="nested")['band_data']
da_bands = da_bands.assign_coords({'band': bands})
da_bands.attrs={}
da_bands.plot.imshow(col="band", col_wrap=3, cmap="gray")

ds_bands = da_bands.to_dataset(dim="band")
ds_bands['C1'].plot.imshow()

da_bands_region = xr.open_dataset(region_bands_fpath, engine="rasterio", default_name="bands")['bands']
da_bands_region = da_bands_region.assign_coords({'band':  ['C' + str(i) for i in range(1,8)]})
da_bands_region.plot.imshow(col="band", col_wrap=3, cmap="gray")
ds_bands_region = da_bands_region.to_dataset(dim="band")

# ---------------------------------------------------------------------.
#### Load labels  
da_labels_fid = xr.open_dataset(labels_fid_fpath, engine="rasterio", default_name="labels_fid")['labels_fid'] 
da_labels_mcid = xr.open_dataset(labels_mcid_fpath, engine="rasterio", default_name="labels_mcid")['labels_mcid']
da_labels_fid = da_labels_fid.drop('band').squeeze()
da_labels_mcid = da_labels_mcid.drop('band').squeeze()
da_labels_fid = da_labels_fid.assign_coords({'x': da_bands['x'], 'y': da_bands['y']})
da_labels_mcid = da_labels_mcid.assign_coords({'x': da_bands['x'], 'y': da_bands['y']})

da_labels_mcid.data = np.digitize(da_labels_mcid.data, np.unique(da_labels_mcid.data))
da_labels_fid.data = np.digitize(da_labels_fid.data, np.unique(da_labels_fid.data))

np.unique(da_labels_fid.data, return_counts=True)
np.unique(da_labels_mcid.data, return_counts=True)

da_labels_fid.plot.imshow()
da_labels_mcid.plot.imshow()

# Define class labels 
# TODO ASSIGN and improve 
labels_mcid_dict = {"Urban": 6, 
            "Agriculture": 2,
            "Forest": 3, 
            "Water": 4,
            "Bare soil": 5, 
            "Unknown": 1, 
}
  
labels_fid_dict = {"Urban": 7, 
             "Agriculture": 2,
             "Forest 1": 3, 
             "Forest 2": 6, 
             "Water": 4,
             "Bare soil": 5, 
             "Unknown": 1, 
}

labels_dict = labels_fid_dict
labels_id_dict = {v: k for k,v in labels_dict.items()}


# ---------------------------------------------------------------------.
### Look at dataset 
ds_bands
da_labels_fid
da_labels_mcid


# ---------------------------------------------------------------------.
### Data preprocessing 
# Merge all data into xr.Dataset
ds_img = ds_bands.copy()
ds_img['labels_id'] = da_labels_fid

# Conversion to pandas.DataFrame 
df_img = ds_img.to_dataframe()
df_img = df_img.drop(columns="spatial_ref")
df_img['labels'] = df_img['labels_id'].apply(lambda x: labels_id_dict[x])
print(df_img)

# Remove unknown labels 
df_labelled = df_img[~df_img['labels'].isin(["Unknown"])]

####-------------------------------------------------------------------------.
#### Define data scaling (Normalize to 0-1)
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
scaler = scaler.fit(df_img[bands])

####-------------------------------------------------------------------------.
#### Define training and test set 
from sklearn.model_selection import train_test_split

# - Define predictor and target array
X = df_labelled[bands]
Y = df_labelled['labels_id'].to_numpy()

# - Random sample pixels 
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.33, random_state=42)
X_train.shape
X_test.shape
Y_train.shape

X_norm = scaler.transform(X)
X_train_norm = scaler.transform(X_train)
X_test_norm = scaler.transform(X_test)

# - Define img predictor 
X_img = df_img[bands]
X_img_norm = scaler.transform(X_img)

# ---------------------------------------------------------------------.
#### Train SVM (SLOW)
# # https://scikit-learn.org/stable/modules/svm.html#multi-class-classification 
# from sklearn import svm
# # “one-versus-one” approach  --> 'ovo'
# # “one-vs-the-rest” multi-class strategy --> 'ovr'
# svm_model = svm.SVC(decision_function_shape='ovo') # 'ovr'
# svm_model.fit(X_norm, Y)

#### Train Multinomial Logistic Regression  (DO NOT CONVERGE WELL)
from sklearn.linear_model import LogisticRegression
# if multinomial --> cross-entropy loss 
# if ovr --> “one-vs-the-rest” multi-class approach

logistic_model = LogisticRegression(random_state=0,
                                    multi_class="ovr")
logistic_model.fit(X_train_norm, Y_train)

# This do not converge 
# logistic_model = LogisticRegression(random_state=0,
#                                     multi_class="multinomial",
#                                     solver ='newton-cg') 
# logistic_model.fit(X_train_norm, Y_train)

#### Train Gaussian Naive Bayes
from sklearn.naive_bayes import GaussianNB
nb_model = GaussianNB()    
nb_model.fit(X_train_norm, Y_train)

#### Train KNN Classifier
from sklearn.neighbors import KNeighborsClassifier
n_neighbors=5
knn_model = KNeighborsClassifier(n_neighbors=n_neighbors)
knn_model.fit(X_train_norm, Y_train)

#### Train Random Forest 
from sklearn.ensemble import RandomForestClassifier
n_trees = 10 # increase to improve accuracy (but increase training time)
rf_model = RandomForestClassifier(n_estimators=n_trees, 
                                  criterion='gini',
                                  max_depth=30, 
                                  min_samples_split=2, 
                                  min_samples_leaf=1,
                                  random_state=0)
rf_model.fit(X_train_norm, Y_train)

# ---------------------------------------------------------------------.
#### Define dictionary of trained models 
dict_models = {'LG': logistic_model,
               'NB': nb_model, 
               'RF': rf_model, 
               'KNN': knn_model
               }

# ---------------------------------------------------------------------.
### Predict class 
dict_pred = {model_acronym: model.predict(X_img_norm) for model_acronym, model in  dict_models.items()}
df_pred = pd.DataFrame(dict_pred, index = df_img.index)
ds_pred = df_pred.to_xarray()

ds_pred.to_array(dim="classifier").plot.imshow(col="classifier", col_wrap=2)
plt.show()

# ---------------------------------------------------------------------.
### Predict class probability
dict_prob = {model_acronym: model.predict_proba(X_img_norm) for model_acronym, model in  dict_models.items()}
list_da = []
for key, prob in dict_prob.items(): 
    df_prob = pd.DataFrame(prob, index = df_full.index)
    df_prob.columns = np.arange(1, df_prob.columns.stop+1)
    ds_prob = df_prob.to_xarray().to_array('class')
    ds_prob.name = key
    list_da.append(ds_prob)
ds_prob = xr.merge(list_da)

# - Plot prob for each class (and single model)
ds_prob['RF'].plot.imshow(col="class", col_wrap=2)
plt.show()

# - Plot probs for each classifier 
ds_prob.to_array("classifier").plot.imshow(row="classifier", col="class")
plt.show()

# ---------------------------------------------------------------------.
#### Mean accuracy on test set 
lg_accuracy = logistic_model.score(X_test_norm, Y_test)
knn_accuracy = knn_model.score(X_test_norm, Y_test)
nb_accuracy = nb_model.score(X_test_norm, Y_test)
rf_accuracy = rf_model.score(X_test_norm, Y_test)
dict_accuracy = {'RF': rf_accuracy, 
                 'NB': nb_accuracy, 
                 'LG': lg_accuracy, 
                 'KNN': knn_accuracy}
print(dict_accuracy)

# ---------------------------------------------------------------------.
### Test set predictions 
dict_pred_test_class = {model_acronym: model.predict(X_test_norm) for model_acronym, model in  dict_models.items()}
 
# ---------------------------------------------------------------------.
### Confusion matrix 
from sklearn.metrics import confusion_matrix
from sklearn.metrics import ConfusionMatrixDisplay

dict_cm =  {model_acronym: confusion_matrix(Y_test, Y_pred) for model_acronym, Y_pred in  dict_pred_test_class.items()}
 
for model_acronym, cm in dict_cm.items():
    disp = ConfusionMatrixDisplay(confusion_matrix=cm) # display_labels=clf.classes_)
    disp.plot()
    plt.show()

# ---------------------------------------------------------------------.
### Classify large region 
df_region = ds_bands_region.to_dataframe()
df_region = df_region.drop(columns="spatial_ref")

X_region_norm = scaler.transform(df_region)

pred_region = dict_models['RF'].predict(X_region_norm)
df_region_pred = pd.DataFrame({'Predicted_Class': pred_region}, index = df_region.index)
ds_region_pred = df_region_pred.to_xarray()
ds_region_pred["Predicted_Class"].plot.imshow()

# ---------------------------------------------------------------------.
### Visualize with NAPARI 
viewer = napari.view_image(ds_region_pred["Predicted_Class"], name="Predicted Class", colormap="gist_earth")
for band, da in ds_bands_region.items():
    viewer.add_image(da, name=band, visible=False)
 
