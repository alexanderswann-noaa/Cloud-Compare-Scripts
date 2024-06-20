#!/usr/bin/env python3

##########################################################################
#                                                                        #
#                              CloudComPy                                #
#                                                                        #
#  This program is free software; you can redistribute it and/or modify  #
#  it under the terms of the GNU General Public License as published by  #
#  the Free Software Foundation; either version 3 of the License, or     #
#  any later version.                                                    #
#                                                                        #
#  This program is distributed in the hope that it will be useful,       #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the          #
#  GNU General Public License for more details.                          #
#                                                                        #
#  You should have received a copy of the GNU General Public License     #
#  along with this program. If not, see <https://www.gnu.org/licenses/>. #
#                                                                        #
#          Copyright 2020-2021 Paul RASCLE www.openfields.fr             #
#                                                                        #
##########################################################################

import os
import sys
import math
import cv2
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import colors

# os.environ["_CCTRACE_"]="ON" # only if you want C++ debug traces

from gendata import getSampleCloud, getSampleCloud2, dataDir, dataExtDir, isCoordEqual
import cloudComPy as cc

cloud1 = cc.loadPointCloud("smallsection-processed_LLS_2024-03-15T051615.010100_0_3.las")

res = cloud1.exportCoordToSF(True, True, True)
sfx = cloud1.getScalarField(3)
sfy = cloud1.getScalarField(4)
sfz = cloud1.getScalarField(5)

dic = cloud1.getScalarFieldDic()
print(dic)
sf = cloud1.getScalarField(dic['Intensity'])

# filter out lowest intensity values---begin
cloud1.setCurrentScalarField(0)

cloud2 = cc.filterBySFValue(100, sf.getMax(), cloud1)
# filter out lowest intensity values---end


# remove-statisitcal-outliers---begin

cloudRef = cc.CloudSamplingTools.sorFilter(knn=6, nSigma=10, cloud=cloud2)
(cloud3, res) = cloud2.partialClone(cloudRef)
cloud3.setName("cloud3")

# remove-statisitcal-outliers---end

#---extractCC02-begin

res1 = cc.ExtractConnectedComponents(clouds=[cloud3],minComponentSize = 10, randomColors=True)
print(res1)

cloud01 = cc.MergeEntities(res1[1], createSFcloudIndex=True)
cloud01.setName("pump_Extract_Components")
cloud02 = cc.MergeEntities(res1[2], createSFcloudIndex=True)
cloud02.setName("pump_residual_Components")
res2 = res1[1] + res1[2] # connected components plus regrouped residual components
cloud2 = cc.MergeEntities(res2, createSFcloudIndex=True)
cloud2.setName("pump_extract_Residual_Components")
cloud3 = cc.MergeEntities(res2, deleteOriginalClouds=True)
cloud3.setName("pump_extract_Residual_Components")
res1 = None
#---extractCC02-end


final_cloud = cloud02

# ---export-files-begin
res = cc.SavePointCloud(final_cloud,"myModifiedCloud1.las")

#--- export-files-end

# ---render-display-begin

colorScalesManager = cc.ccColorScalesManager.GetUniqueInstance()
scale = colorScalesManager.getDefaultScale(cc.DEFAULT_SCALES.HSV_360_DEG)

dic = final_cloud.getScalarFieldDic()
print(dic)

final_cloud.setCurrentScalarField(0)
final_cloud.setCurrentDisplayedScalarField(0)

final_cloud.getScalarField(0).setColorScale(scale)

cc.addToRenderScene(final_cloud)


cc.setIsoView1()
# cc.setCameraPos((-53.7, 57.8, 27.7))
cc.render(os.path.join(dataDir, "render1.png"), 1280, 720)

img_1 = cv2.imread(os.path.join(dataDir, "render1.png"))

cv2.imshow('image', img_1)
cv2.waitKey(0)

# ---render-display-end


