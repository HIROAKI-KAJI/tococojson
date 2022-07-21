import json
import datetime
import os
import re
import cv2
from random import random
import xml.etree.ElementTree as ET

def dicinitalize(dic):
    if dic == None:
        redict = {"images":list(),
                 "anotates":dict()}
    else:
        redict = dic
    return redict
def cocotext(textfolderpath,idpath,dic = None):
    
    idlist = list()
    redic = dicinitalize(dic)
    if(os.path.exists(idpath)):
        with open(idpath) as idf:
            idl = idf.readlines()
            for tag in idl:
                idlist += [tag.strip()]
    
    if(os.path.exists(textfolderpath)):
        tfpl = os.listdir(textfolderpath)
        for tfp in tfpl:
            bace, ext = os.path.splitext(tfp)
            if ext == ".txt":
                with open(textfolderpath+'/' + tfp) as tf:
                    bace, ext = os.path.splitext(tfp)
                    imagepath = bace + ".jpg"
                    imgpath = textfolderpath+"/"+imagepath
                    if(os.path.exists(imgpath)):
                        redic["images"] += [imgpath]
                        img = cv2.imread(imgpath)
                        height,width = img.shape[:2]
                        height,width = float(height),float(width)
                        tl = tf.readlines()
                        tmp_dict = dict()
                        for t in tl:
                            n = str(len(redic["images"]) - 1)
                            anotatelist = re.findall(r'\S+', t)
                            x = "{:.2f}".format(float(anotatelist[1])*width - float(anotatelist[3])*width/2.0)
                            y = "{:.2f}".format(float(anotatelist[2])*height - float(anotatelist[4])*height/2.0)
                            w = "{:.2f}".format(float(anotatelist[3])*width)
                            h = "{:.2f}".format(float(anotatelist[4])*height)
                            tmp_dict.update({idlist[int(anotatelist[0])]:[x,y,w,h]})
                        redic["anotates"].update({n:tmp_dict})
        return redic

def pascalVOC(xmlpath,dic=None):
    
    redic = dicinitalize(dic)
    if(os.path.exists(xmlpath)):
        
        xfpl = os.listdir(xmlpath)
        for xfp in xfpl:
            xfp = os.path.join(xmlpath,xfp)
            if(os.path.exists(xfp)):
                
                anotatedic = pascalxml_load(xfp)
                if anotatedic != None:
                    redic["images"] += [anotatedic["imgpath"]]
                    n = str(len(redic["images"]) - 1)
                    redic["anotates"].update({n:anotatedic["bboxs"]})
    return redic


def pascalxml_load(xpath):
    tree = ET.parse(xpath)
    data = tree.getroot()
    
    redic = {
        "imgname" : "",
        "imgpath":"",
        "bboxs" : dict()
    }
    width = None
    height = None
    
    for filename in data.iter('filename'):
        redic["imgname"] = filename.text
    for filepath in data.iter('path'):
        redic["imgpath"] = filepath.text
        
    for size in data.iter('size'):
        for width in size.iter('width'):
            width = float(width.text)
        for height in size.iter('height'):
            height = float(height.text)
            
    for obj in data.findall('object'):
        dic_tmp = dict()
        for  name in obj.iter('name'):
            tag = name.text
        for bndbox in obj.findall('bndbox'):
            for xmin in bndbox.iter('xmin'):
                xmin = float(xmin.text)
            for ymin in bndbox.iter('ymin'):
                ymin = float(ymin.text)
            for xmax in bndbox.iter('xmax'):
                xmax = float(xmax.text)
            for ymax in bndbox.iter('ymax'):
                ymax = float(ymax.text)
            bw = xmax-xmin
            bh = ymax-ymin
            blx = xmin
            bty = ymin
            #小数点下3桁
            blis = ["{:.3f}".format(blx),
                   "{:.3f}".format(bty),
                   "{:.3f}".format(bw),
                   "{:.3f}".format(bh)]
        redic["bboxs"].update({tag:blis})
        
    if redic["bboxs"] == {}:
        return
    else:
        return redic
        

def tococojson(anotatedic,tagdict,sh=0.5):
    annotation_id = 0
    categories = []
    images_v = []
    annotations_v = []
    images_t = []
    annotations_t = []
    #vimgfolder,timgfolder
    path = os.getcwd()
    print(path)
    trainpath = path +"/"+"train"
    validpath = path +"/"+"valid"
    if not(os.path.exists(trainpath)):
        os.mkdir(trainpath)
    if not(os.path.exists(validpath)):
        os.makedirs(validpath)
    #i is image serial
    supercategory = "Super"
    categories.append({
            "id":0,
            "name":supercategory,
            "supercategory":"none"
        })
    for key in tagdict:
        categories.append({
            "id":tagdict[key],
            "name":key,
            "supercategory":supercategory
        })
    
    for i,imgpath in enumerate(anotatedic["images"]):
        rand = random()
        img = cv2.imread(imgpath)
        height,width = img.shape[:2]
        imgname = imgpath.split('/')[-1]
        if rand > sh:
            images_v.append({
                "id": i,
                "file_name":imgname,
                "height": height,
                "width": width
            })
            cv2.imwrite(validpath+"/"+imgname,img)
        else:
            images_t.append({
                "id": i,
                "file_name":imgname,
                "height": height,
                "width": width
            })
            cv2.imwrite(trainpath+"/"+imgname,img)
        for key in anotatedic["anotates"][str(i)]:
            if rand > sh:
                annotations_v.append({
                    "id": annotation_id,
                    "image_id": i,
                    "category_id": tagdict[key],
                    "bbox": anotatedic["anotates"][str(i)][key],
                    "area": float(anotatedic["anotates"][str(i)][key][2])*float(anotatedic["anotates"][str(i)][key][3]),
                    "segmentation": [],
                    "iscrowd": 0
                })
            else:
                annotations_t.append({
                    "id": annotation_id,
                    "image_id": i,
                    "category_id": tagdict[key],
                    "bbox": anotatedic["anotates"][str(i)][key],
                    "area": float(anotatedic["anotates"][str(i)][key][2])*float(anotatedic["anotates"][str(i)][key][3]),
                    "segmentation": [],
                    "iscrowd": 0
                })
            annotation_id = annotation_id + 1
    json_vdict = {"categories":categories,
                "images":images_v,
                "annotations":annotations_v}
    json_tdict = {"categories":categories,
                "images":images_t,
                "annotations":annotations_t}
    return json_vdict,json_tdict
if __name__=='__main__':
    andic = cocotext("objfolder_path",
     "obj.names_path")
    andic = pascalVOC("xmlpath",dic=andic)
    
    tags = ["tag1","tag2"]
    tagdict = dict()
    for i,tag in enumerate(tags):
        tagdict.update({tag:i+1})
    v,t = tococojson(andic,tagdic,sh=0.7)
    
    with open('valid.json', 'w') as vfile:
        json.dump(v, vfile, indent=4)
    with open('train.json', 'w') as tfile:
        json.dump(t, tfile, indent=4)
      
