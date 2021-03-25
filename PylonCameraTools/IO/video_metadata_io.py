from pypylon import pylon
from pypylon import genicam
import os


class VideoSaver:
    def __init__(self, saver_class, name, width_height, fps):
        self.converter = pylon.ImageFormatConverter()

        # converting to opencv bgr format
        self.converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
        
        self.video_writer = saver_class(output_filename=name,
                                                width_height=width_height,
                                                fps=fps)

        
        self.meta_data_file = open(os.path.splitext(name)[0] + ".csv", 'w', encoding='utf-8')

    def convert_frame(self, camera_grabbed_frame):
        # Access the image data
        image = self.converter.Convert(camera_grabbed_frame)
        img = image.GetArray()
        return img

    def save_camera_frame(self, camera_grabbed_frame):
        frame = self.convert_frame(camera_grabbed_frame)
        self.video_writer.write(frame)
        self.save_frame_metadate(camera_grabbed_frame)
        return frame

    def save_frame_metadate(self, grabResult):
        timestamp = -1
        frame_counter = -1

        # Todo: move camera related operations outside this class

        # Access the chunk data attached to the result.
        # Before accessing the chunk data, you should check to see
        # if the chunk is readable. When it is readable, the buffer
        # contains the requested chunk data.
        if genicam.IsReadable(grabResult.ChunkTimestamp):
            timestamp = grabResult.ChunkTimestamp.Value
            print("TimeStamp (Result): ", timestamp)

        if genicam.IsReadable(grabResult.ChunkFramecounter):
            frame_counter = grabResult.ChunkFramecounter.Value
            print("FrameCounter (Result): ", frame_counter)

        self.meta_data_file.write(f"{frame_counter},{timestamp}\n")

    def __del__(self):
        self.meta_data_file.close()


class VideoReader:
    def __init__(self, loader_class, name, width_height=None, fps=None):      
        self.video_reader = loader_class(input_filename=name,
                                        width_height=width_height,
                                        fps=fps)

        self.meta_data_file = open(os.path.splitext(name)[0] + ".csv", 'r', encoding='utf-8')

    def read_frame(self):
        frame = self.video_reader.read()
        meta_data = self.read_frame_metadate()

        return frame, meta_data

    def read_frame_metadate(self):
        line = self.meta_data_file.readline()
        if line is None or len(line) <= 0:
            return None
        
        columns = line.split(',')
        # Todo: move camera related operations outside this class
        timestamp = int(columns[1])
        print("TimeStamp (Result): ", timestamp)

        frame_counter = int(columns[0])
        print("FrameCounter (Result): ", frame_counter)

        return {"timestamp": timestamp,
                "frame_counter": frame_counter}

    def __del__(self):
        self.meta_data_file.close()
