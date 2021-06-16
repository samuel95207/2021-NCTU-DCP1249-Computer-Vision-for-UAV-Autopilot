# video to frames
import cv2
import os


def get_images_from_video(video_name, output_path, scale = 1, sample_frequency=1):
    cap = cv2.VideoCapture(video_name)
    c = 1

    rv, video_frame = cap.read()
    if not rv:
        print(f'ERROR: fail to read {video_name}')
        input('exit...')
        exit(1)

    idx = 1
    while rv:
        if (c % sample_frequency == 0):
            size = video_frame.shape
            video_frame = cv2.resize(video_frame, (int(size[1]*scale), int(size[0]*scale)), interpolation=cv2.INTER_AREA)
            filename = f'{idx:04d}.jpg'
            print(filename)
            cv2.imwrite(os.path.join(output_path, filename), video_frame)
            idx = idx + 1

        c = c + 1
        rv, video_frame = cap.read()

    cap.release()
    return idx-1

def create_rgb_txt(output_path, image_count, period):
    if not os.path.isfile(output_path):
        file = open(output_path,"a")
    else:
        file = open(output_path,"w")

    for idx in range(1, image_count+1):
        file.write(f'{((idx-1)*period):.6f} rgb/{(idx):04d}.jpg\n')
    file.close()


dataset_path = './dataset/desk_0611'
video_path = f'{dataset_path}/video.mp4'
img_path = f'{dataset_path}/rgb/'
rgbtxt_path = f'{dataset_path}/rgb.txt'
sample_frequency = 1

colmap_path = f'{dataset_path}/colmap/'
colmap_sample_frequency = 50

if not os.path.isdir(img_path):
    os.mkdir(img_path)

if not os.path.isdir(colmap_path):
    os.mkdir(colmap_path)

# Create rgb data
image_count = get_images_from_video(video_path, img_path, 0.25, sample_frequency)
create_rgb_txt(rgbtxt_path, image_count, 1/(30/sample_frequency))

# create colmat training data
get_images_from_video(video_path, colmap_path, 0.25,  colmap_sample_frequency)



cv2.destroyAllWindows()
