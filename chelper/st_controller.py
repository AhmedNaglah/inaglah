import pandas as pd
import json
import numpy as np

slide_name = "V10S15-103_XY01_IU-21-015F"
st_directory_tree = [ "./static/st/spotCoordinates", "./static/st/geneCnt", "./static/st/cellType"]

df_spotCoordinates = pd.read_csv(f"{st_directory_tree[0]}/{slide_name}.csv", header= 0)
df_geneCnt = pd.read_csv(f"{st_directory_tree[1]}/{slide_name}.csv", header= 0)
df_cellType = pd.read_csv(f"{st_directory_tree[2]}/{slide_name}.csv", header= 0)
df_spotCoordinates.rename(columns={ df_spotCoordinates.columns[0]: "idx" }, inplace = True)
df_geneCnt.rename(columns={ df_geneCnt.columns[0]: "idx" }, inplace = True)
df_cellType.rename(columns={ df_cellType.columns[0]: "idx" }, inplace = True)

h1 = df_spotCoordinates.head() 
h2 = df_geneCnt.head() 
h3 = df_cellType.head() 

with open("./static/anno.json", "r") as f:
    anno = json.load(f)

def getPolygonJSON(i):
    global anno
    polygon = anno[i]['target']['selector'][0]['value'].replace("<svg><polygon points=' ", "").replace("'></polygon></svg>", "").split(" ")
    polygon = [ tuple(map(int, k.split(",")))   for k in polygon]
    return polygon

#print(h1)
#print(h2)
#print(h3)

""" for i in range(10):
    print(getPolygonJSON(i))
 """
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

def spotInsidePolygon(spot, i):
    global df_spotCoordinates
    row = df_spotCoordinates.loc[df_spotCoordinates['idx'] == spot]
    pnt = row[["imagerow", "imagecol"]].values[0]
    point = Point(pnt[0], pnt[1])
    polygon = Polygon(getPolygonJSON(i))
    return polygon.contains(point)

spot = "AAACCACTACACAGAT-1"

""" for i in range(10):
    print(spotInsidePolygon(spot, i)) """

def getAllSpotsInsidePolygon(i):
    global df_spotCoordinates
    polygon = Polygon(getPolygonJSON(i))
    spots = []
    for index, row in df_spotCoordinates.iterrows():
        pnt = (row["imagerow"], row["imagecol"])
        point = Point(pnt[0], pnt[1])
        if polygon.contains(point):
            spots.append((index, row["idx"], (pnt[0], pnt[1])))
    return spots

def getAllSpotsInsidePolygonGiven(polygon):
    global df_spotCoordinates
    polygon = Polygon(polygon)
    spots = []
    for index, row in df_spotCoordinates.iterrows():
        pnt = (row["imagerow"], row["imagecol"])
        point = Point(pnt[0], pnt[1])
        if polygon.contains(point):
            spots.append((index, row["idx"], (pnt[0], pnt[1])))
    return spots

def getNearestSpotsOutsidePolygonGiven(polygon):
    global df_spotCoordinates
    polygon = Polygon(polygon)
    spot = None
    dist = None
    for index, row in df_spotCoordinates.iterrows():
        pnt = (row["imagerow"], row["imagecol"])
        point = Point(pnt[0], pnt[1])
        if not polygon.contains(point):
            if spot == None:
                spot = (index, row["idx"], (pnt[0], pnt[1]))
                dist = polygon.exterior.distance(point)
            else:
                if polygon.exterior.distance(point)<dist:
                    spot = (index, row["idx"], (pnt[0], pnt[1]))
                    dist = polygon.exterior.distance(point)
    return spot

def getNearestSpotsOutsidePolygon(i):
    global df_spotCoordinates
    polygon = Polygon(getPolygonJSON(i))
    spot = None
    dist = None
    for index, row in df_spotCoordinates.iterrows():
        pnt = (row["imagerow"], row["imagecol"])
        point = Point(pnt[0], pnt[1])
        if not polygon.contains(point):
            if spot == None:
                spot = (index, row["idx"], (pnt[0], pnt[1]))
                dist = polygon.exterior.distance(point)
            else:
                if polygon.exterior.distance(point)<dist:
                    spot = (index, row["idx"], (pnt[0], pnt[1]))
                    dist = polygon.exterior.distance(point)
    return spot

def aggregateGene(spots):
    global df_geneCnt
    types = df_geneCnt['idx'].values.tolist()
    spots_id = [k[1] for k in spots]
    
    if len(spots_id)>1:
        val = df_geneCnt[spots_id[0]].values
        for i in range(len(spots_id)-1):
            val += df_geneCnt[spots_id[i+1]].values
        aggre_df = [types, val, 'success']
    elif len(spots_id)==1:
        val = df_geneCnt[spots_id[0]].values
        aggre_df = [types, val, 'success']
    else:
        aggre_df = [types, None,'error or no spots']
    return aggre_df

def aggregateCellType(spots):
    global df_cellType
    types = df_cellType['idx'].values.tolist()
    spots_id = [k[1] for k in spots]
    
    if len(spots_id)>1:
        val = df_cellType[spots_id[0]].values
        for i in range(len(spots_id)-1):
            val += df_cellType[spots_id[i+1]].values
        aggre_df = [types, val/len(spots_id), 'success']
    elif len(spots_id)==1:
        val = df_cellType[spots_id[0]].values
        aggre_df = [types, val, 'success']
    else:
        aggre_df = [None, None,'error or no spots']
    return aggre_df

compartment_genes = []
compartment_cells = []

def getCompartmentInfo(i):
    global anno
    id = anno[i]['id']
    compartment = anno[i]['body'][0]['value']
    polygon  = getPolygonJSON(i)
    return {'id': id, 'compartment': compartment, 'polygon': polygon}

def topKTypes(all, k):
    types, val, _ = all
    indxs = np.argsort(val)
    val_ = val[indxs[-k:]]
    types_ = [types[k] for k in indxs[-k:].tolist()]
    return types_, val_

""" for i in range(20):
    spots = getAllSpotsInsidePolygon(i)
    if len(spots)==0:
        spots = [getNearestSpotsOutsidePolygon(i)]
    compartment_cells = aggregateCellType(spots)
    compartment_genes = aggregateGene(spots)
    info = getCompartmentInfo(i)
    compartment_genes_ = topKTypes(compartment_genes, 10)
    compartment_cells_ = topKTypes(compartment_cells, 5)

    info['compartment_genes'] = compartment_genes_
    info['compartment_cells'] = compartment_cells_

    print(info)
    print('') """

def getTopGenes(i, k):
    spots = getAllSpotsInsidePolygon(i)
    if len(spots)==0:
        spots = [getNearestSpotsOutsidePolygon(i)]
    compartment_genes = aggregateGene(spots)
    compartment_genes_ = topKTypes(compartment_genes, k)
    return compartment_genes_

def getTopGenesGiven(polygon, k):
    spots = getAllSpotsInsidePolygonGiven(polygon)
    if len(spots)==0:
        spots = [getNearestSpotsOutsidePolygonGiven(polygon)]
    compartment_genes = aggregateGene(spots)
    compartment_genes_ = topKTypes(compartment_genes, k)
    return compartment_genes_

def getTopCells(i, k):
    spots = getAllSpotsInsidePolygon(i)
    if len(spots)==0:
        spots = [getNearestSpotsOutsidePolygon(i)]
    compartment_genes = aggregateCellType(spots)
    compartment_genes_ = topKTypes(compartment_genes, k)
    return compartment_genes_

def getTopCellsGiven(polygon, k):
    spots = getAllSpotsInsidePolygonGiven(polygon)
    if len(spots)==0:
        spots = [getNearestSpotsOutsidePolygonGiven(polygon)]
    compartment_genes = aggregateCellType(spots)
    compartment_genes_ = topKTypes(compartment_genes, k)
    return compartment_genes_

