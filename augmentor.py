#flip, hori, verti, zoom, rotate, combination of these
#python augmentor.py sorted.tags.csv new_csv /Users/sara/Downloads/forensic/all_imgs/
from PIL import Image
import csv
import sys
import json
import random
import cv2

random.seed(10)

def flip_img(im_name, image, flip_flag, tag_coordinate, width, height):
    flipped = cv2.flip(image, flip_flag)
    x1, y1, x2, y2 = tag_coordinate
    w = x2 - x1
    h = y2 - y1 
    if flip_flag == 0:
        flipped_img = cv2.rectangle(flipped,(int(x1), int(height - y1 -1 - h)), (int(x2), int(height - y2 - 1 + h)), (0, 0, 255), 3)
        x1 = int(x1)
        y1 = int(height - y1 -1 - h)
        x2 = int(x2)
        y2 = int(height - y2 - 1 + h)
        new_name = im_name + "fliped_y.JPG"
    elif flip_flag == 1:
        flipped_img = cv2.rectangle(flipped,(int(width - x1 - 1 - w), int(y1)), (int(width - x2 - 1 + w), int(y2)), (0, 0, 255), 3)
        x1 = int(width - x1 - 1 - w)
        y1 = int(y1)
        x2 = int(width - x2 - 1 + w)
        y2 = int(y2)
        new_name = im_name + "fliped_x.JPG"
    
    elif flip_flag == -1:
        flipped_img = cv2.rectangle(flipped,(int(width - x1 - 1 - w),  int(height - y1 -1 - h)), (int(width - x2 - 1 + w), int(height - y2 -1 + h)), (0, 0, 255), 3)
        x1 = int(width - x1 - w -1)
        y1 = int(height - y1 -1 - h)
        x2 = int(width - x2 - 1 + w)
        y2 = int(height - y2 - 1 + h)
        new_name = im_name + "fliped_xy.JPG"

    cv2.imwrite(new_name, flipped_img)
    return update_row(row, new_name, width, height, x1, y1, x2- x1, y2 - y1)


def extract_coor_percentage(loc): #loc = row[3] = the column in csv that has the coordinate
    loc1 = json.loads(loc)
    loc = loc1[0]['geometry']
    location = []
    location.append(loc['x'])
    location.append(loc['y'])
    location.append(loc['width'])
    location.append(loc['height'])
    return location

def update_row(row, new_name, width, height, tag_x, tag_y, tag_w, tag_h):
    print("in function update: \n", row)
    loc = row[3]
    loc1 = json.loads(loc)
    loc1[0]['geometry']['x'] = tag_x/float(width)
    loc1[0]['geometry']['y'] = tag_y/float(height)
    loc1[0]['geometry']['width'] = tag_w/float(width)
    loc1[0]['geometry']['height'] = tag_h/float(height)
    loc_str = json.dumps(loc1)
    row[3] = loc_str
    row[8] = new_name
    return row[:]
    

#def scale_img(im_name, image, scales, coordinate):
def scale_img(tags_info, image, scales, img_rows):
    height, width = image.shape[:2]
    row_num = 0
    new_rows = []
    for img_row in img_rows:
        print("img_row_for:", img_row)
        x1, y1, x2, y2 = tags_info[row_num][0:4] #the last one is not included. that means this is indices 0, 1, 2, 3
        im = cv2.rectangle(image,(x1, y1), (x2, y2), (0, 0, 255), 3)
        cv2.imwrite("bla.jpg", im)
        print(x1, y1, x2, y2)
        row_num += 1
        new_im_x1 = random.randint(0, x1)
        new_im_y1 = random.randint(0, y1)
        for scale in scales:
            new_im_h = int(scale * height) 
            new_im_w = int(scale * width) 
            if x2 - x1 > new_im_w or y2 - y1 > new_im_h: #if the tags itself is bigger than this cut/scaled part of the image, ignore it
                print("scale: ", scale)
                continue
            while new_im_y1 + new_im_h < y2 or new_im_x1 + new_im_w < x2:
                new_im_x1 = random.randint(0, x1)
                new_im_y1 = random.randint(0, y1)
                #print(new_im_x1, new_im_y1)
            new_im_y2 = new_im_y1 + new_im_h
            new_im_x2 = new_im_x1 + new_im_w
            scaled_im = image[new_im_y1 : new_im_y2, new_im_x1 : new_im_x2]
            scaled_im = cv2.resize(scaled_im, (width, height), interpolation = cv2.INTER_AREA)
            tag_x = (x1 - new_im_x1)* width/float(new_im_w)
            tag_y = (y1 - new_im_y1)* height/float(new_im_h)
            tag_w = w * width/float(new_im_w)
            tag_h = h * height/float(new_im_h)

            scaled_im = cv2.rectangle(scaled_im,(int(tag_x), int(tag_y)), (int(tag_x + tag_w), int(tag_y + tag_h)), (0, 0, 255), 3)
            new_name = im_name + str(scale) + ".JPG"
            cv2.imwrite(new_name, scaled_im)
            print("img_row: \n", img_row)
            new_rows.append(update_row(img_row[:], new_name, width, height, tag_x, tag_y, tag_w, tag_h))
        return new_rows


def append_rows(rows):
    for i in range(len(rows)):
        new_rows.append(rows[i])


def get_coordinate(width, height,location):#this location is the percentage
    x1 = int(float(location[0])*width)
    y1 = int(float(location[1])*height)
    w = int(float(location[2])*width)
    x2 = x1 + w  
    h =  int(float(location[3])*height)
    y2 = y1 + h 
    return [x1, y1, x2, y2]


def img_tags_coor(width, height, lines):
    tags = []
    for l in lines:
        coor = []
        coor = get_coordinate(width, height, extract_coor_percentage(l[3]))
        coor.append(l[5])
        tags.append(coor)
    return tags #this is a list of lists [[x1, y1, x2, y2, tag1],[x1, y1, x2, y2, tag2]...]

#################### main ################
f = open(sys.argv[1])
res_csv = sys.argv[2]
imgs_dir = sys.argv[3]

data = csv.reader(f)
new_rows = []
first_row = 1
scales = [0.3, 0.5, 0.8]

next_img = 0

img_rows = []
img_name = ""

for row in data:
    new_rows.append(row[:])
    print("regular row: \n", row)
    if first_row == 1:
        first_row = 0
        continue

    else:
        name = row[8][ : row[8].find('JPG')]
        location = extract_coor_percentage(row[3])
        image = cv2.imread(imgs_dir + row[8], cv2.IMREAD_IGNORE_ORIENTATION | cv2.IMREAD_COLOR)
        height, width = image.shape[:2]
        coor = get_coordinate(width, height, location) # coor = [x1, y1, x2, y2]
        ''' 
        new_rows.append(flip_img(name, image, 1, coor, width, height))
        new_rows.append(flip_img(name, image, 0, coor, width, height))
        new_rows.append(flip_img(name , image, -1, coor, width, height))
        '''
        if img_name == name:
            img_rows.append(row[:])
        elif img_name == "":
            img_name = name
            img_rows.append(row[:])
            img_h, img_w = image.shape[:2]
            im_obj = image
        else:
            next_img +=1
            tags_info = img_tags_coor(img_w, img_h,img_rows)
            rows = scale_img(tags_info, im_obj, scales, img_rows)
            #rows = scale_img(img_name, image, scales, coor)
            #append_rows(rows)
            img_name = name
            img_rows = []
            img_rows.append(row[:])
            img_h, img_w = image.shape[:2]
            if next_img == 2:
                exit()

with open(res_csv, 'w') as output:
    writer = csv.writer(output, lineterminator = '\n')
    writer.writerows(new_rows)
