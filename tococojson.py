import json
import collections as cl
import datetime

def info():
  tmp = cl.OrderedDict()
  tmp["description"] = "Test"
  tmp["url"] = "https://test"
  tmp["version"] = "0.01"
  tmp["year"] = 2019
  tmp["contributor"] = "xxxx"
  tmp["data_created"] = "2019/09/10"
  return tmp

def licenses():
  tmp = cl.OrderedDict()
  tmp["id"] = 1
  tmp["url"] = dummy_words
  tmp["name"] = "administrater"
  return tmp

def images():
  tmps = []
  for i in range(10):
    tmp = cl.OrderedDict()
    tmp["license"] = 0
    tmp["id"] = i
    tmp["file_name"] = str(i) + ".png"
    tmp["width"] = "640"
    tmp["height"] = "480"
    tmp["date_captured"] = "2019-09-01 12:34:56"
    tmp["coco_url"] = dummy_words
    tmp["flickr_url"] = dummy_words
    tmps.append(tmp)
  return tmps


def main():
    query_list = ["info", "licenses", "images", "annotations", "categories", "segment_info"]
    js = cl.OrderedDict()
    for i in range(len(query_list)):
      tmp = ""
      # Info
      if query_list[i] == "info":
        tmp = info()

      # save it
      js[query_list[i]] = tmp

    # write
    fw = open('datasets.json','w')
    json.dump(js,fw,indent=2)

if __name__=='__main__':
    main()
