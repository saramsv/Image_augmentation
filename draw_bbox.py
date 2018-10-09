#!/usr/bin/env python3
#./draw_bbox.py total_replaced_tags.csv all_imgs all_imgs_bbox/
import sys
import os.path
import cv2
import csv
import json
import pandas as pd


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("usage: csv_file  src_img_dir dest_img_dir")
        exit()
    csv_file = sys.argv[1]#normalized512by512_tags.csv
    src_dir = sys.argv[2]
    dest_dir = sys.argv[3]

    df = pd.read_csv(csv_file)
    for i in range(df['image1'].unique().shape[0]):
        all_sub_imgs = df.loc[df['image1'] == df['image1'].unique()[i]]
        all_sub_imgs = all_sub_imgs.reset_index(drop = True)
        #print(all_sub_imgs)
        images_dir = src_dir + '/'  + df['image1'].unique()[i]
        print(images_dir)
        '''
        import bpython
        bpython.embed(locals())
        exit()
        '''

        if os.path.isfile(images_dir):
            im = cv2.imread(images_dir, cv2.IMREAD_IGNORE_ORIENTATION | cv2.IMREAD_COLOR)
            #im = cv2.imread(images_dir)
            hei, wi = im.shape[:2] 
            #print(hei, wi)
            for j in range(all_sub_imgs.shape[0]):
                #if all_sub_imgs['tag'][j] == "scavenging":
                sub_info = all_sub_imgs['location'][j]
                sub_info = json.loads(sub_info)[0]
                geometry = sub_info['geometry']
                x = int(float(geometry['x']) * wi)
                y = int(float(geometry['y']) * hei)
                w = int(float(geometry['width']) * wi)
                h = int(float(geometry['height']) * hei)
                new_img = cv2.rectangle(im, (x, y), (x+w,y+h), (0, 0, 255), 3)
                #print(df['image1'].unique()[i])
                cv2.imwrite(dest_dir + '/' + df['image1'].unique()[i], new_img)
