from abc import ABC
import numpy as np
import subprocess
import shlex
import re
import os

class SaverBackend(ABC):
    def __init__(self, output_filename, width_height, fps):
        self.width = width_height[0]
        self.height = width_height[1]
        self.fps = fps

        self.output_filename = output_filename

        self.process = None

    def write(self, img):
        self.process.stdin.write(img.tobytes())

    def __del__(self):
        # Close and flush stdin
        self.process.stdin.close()

        # Wait for sub-process to finish
        self.process.wait()

        if self.process.poll():
            print(f"******ffmpeg sub-process finished with exit code {self.process.poll()}")
        else:
            self.process.terminate()
            print("******ffmpeg sub-process didn't finish properly.")
            print(f"******terminated with exit code {self.process.poll()}")


class ReaderBackend(ABC):
    def __init__(self, input_filename, extension, width_height=None, fps=None):
        self.input_filename = input_filename

        ext = os.path.splitext(self.input_filename)[1]
        if not len(ext) > 0:
            raise ValueError("File path has no extention!")

        if ext != extension:
            msg = f"expected file with {extension} format(extension). got file with {ext}"
            raise ValueError(msg)

        meta = None
        if width_height:
            self.width = width_height[0]
            self.height = width_height[1]
        else:
            if meta is None:
                meta = self.get_video_metadata(self.input_filename)
            self.width = meta["width"]
            self.height = meta["height"]

        if fps:
            self.fps = fps
        else:
            if meta is None:
                meta = self.get_video_metadata(self.input_filename)
            self.fps = meta["fps"]

        self.frame_size = self.width * self.height * 3
        
        self.process = None

    def get_video_metadata(self, file_path):
        command_string = f"ffprobe -v error -show_entries stream=width,height,r_frame_rate -of csv=p=0:s=, {file_path}"
        command = shlex.split(command_string)

        process = subprocess.Popen(command,
                                    stdout=subprocess.PIPE)

        results = process.stdout.read()

        process.stdout.close()
        process.wait()
        if not process.poll():
            process.terminate()

        raw_meta = results.decode('utf-8').replace('\n', '').split(',')

        if len(raw_meta) < 3:
            raise ValueError("Error: unexpected results from ffprobe")

        meta = [int(re.findall("^[0-9]*", st)[0]) for st in raw_meta]

        return {"width": meta[0],
                "height": meta[1],
                "fps": meta[2]}

    def convert_frame(self, read_raw_fram):
        image = np.frombuffer(read_raw_fram, dtype=np.uint8)
        # Notice how height is specified first and then width
        image = image.reshape( (self.height,self.width,3) )

        return image

    def read(self):
        # None if the process is still running
        # exit code otherwise
        if self.process.poll() is not None:
            return None
            
        frame_bytes = self.process.stdout.read(self.frame_size)

        if frame_bytes is None:
            print("******frame bytes were none")
            return None
        if len(frame_bytes) != self.frame_size:
            print(f"******frame bytes len is incorrect expected size {self.frame_size} but got {len(frame_bytes)}")
            return None

        frame = self.convert_frame(frame_bytes)
        return frame

    def __del__(self):
        # Close and flush stdin
        self.process.stdout.close()

        # Wait for sub-process to finish
        self.process.wait()

        if self.process.poll():
            print(f"******ffmpeg sub-process finished with exit code {self.process.poll()}")
        else:
            self.process.terminate()
            print("******ffmpeg sub-process didn't finish properly.")
            print(f"******terminated with exit code {self.process.poll()}")