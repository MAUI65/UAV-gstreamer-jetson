import cv2
import os
import argparse

def create_video(input_folder, output_file, start, end, framerate):
    images = []
    for i in range(int(start), int(end)+1):
        img_path = os.path.join(input_folder, f"{i:05d}.jpg")
        if os.path.isfile(img_path):
            images.append(cv2.imread(img_path))

    height, width, _ = images[0].shape
    video = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*'mp4v'), framerate, (width, height))

    for image in images:
        video.write(image)

    video.release()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a video from a sequence of images.')
    parser.add_argument('input_folder', type=str, help='The folder containing the images.')
    parser.add_argument('output_file', type=str, help='The output video file.')
    parser.add_argument('start', type=int, help='The start of the range of images to include.')
    parser.add_argument('end', type=int, help='The end of the range of images to include.')
    parser.add_argument('framerate', type=int, help='The framerate of the output video.')
    args = parser.parse_args()

    create_video(args.input_folder, args.output_file, args.start, args.end, args.framerate)