import numpy as np
import subprocess
import shlex
import os
from .encoder_decoders_base import SaverBackend, ReaderBackend


class HuffyuvLosslessReader(ReaderBackend):
    def __init__(self, *args, **kwargs):
        kwargs["extension"] = ".mkv"
        super().__init__(*args, **kwargs)

        # Open ffmpeg application as sub-process
        # FFmpeg input PIPE: RAW images in BGR color format
        # FFmpeg output MP4 file encoded with HEVC codec.
        # Arguments list:
        # -y                   Overwrite output file without asking
        # -s {width}x{height}  Input resolution width x height (1344x756)
        # -pixel_format bgr24  Input frame color format is BGR with 8 bits per color component
        # -f rawvideo          Input format: raw video
        # -r {fps}             Frame rate: fps (25fps)
        # -i pipe:             ffmpeg input is a PIPE
        # -vcodec libx265      Video codec: H.265 (HEVC)
        # -pix_fmt yuv420p     Output video color space YUV420 (saving space compared to YUV444)
        # -crf 24              Constant quality encoding (lower value for higher quality and larger output file).
        # {input_filename}    Input file name: input_filename (output.mp4)
        command_string = f'ffmpeg -y -codec:v huffyuv -pix_fmt yuv422p -i {self.input_filename} -pix_fmt bgr24 -codec:v rawvideo -f image2pipe pipe:1'

        command = shlex.split(command_string)
        self.process = subprocess.Popen(command, 
                                        stdout=subprocess.PIPE,
                                        bufsize=self.frame_size*2)


class H264LossLessReader(ReaderBackend):
    def __init__(self, *args, **kwargs):
        kwargs["extension"] = ".m4v"
        super().__init__(*args, **kwargs)

        # Open ffmpeg application as sub-process
        # FFmpeg input PIPE: RAW images in BGR color format
        # FFmpeg output MP4 file encoded with HEVC codec.
        # Arguments list:
        # -y                   Overwrite output file without asking
        # -s {width}x{height}  Input resolution width x height (1344x756)
        # -pixel_format bgr24  Input frame color format is BGR with 8 bits per color component
        # -f rawvideo          Input format: raw video
        # -r {fps}             Frame rate: fps (25fps)
        # -i pipe:             ffmpeg input is a PIPE
        # -vcodec libx265      Video codec: H.265 (HEVC)
        # -pix_fmt yuv420p     Output video color space YUV420 (saving space compared to YUV444)
        # -crf 24              Constant quality encoding (lower value for higher quality and larger output file).
        # {input_filename}    Input file name: input_filename (output.mp4)
        command_string = f'ffmpeg -y -codec:v h264 -i {self.input_filename} -pix_fmt bgr24 -codec:v rawvideo -f image2pipe pipe:1'

        command = shlex.split(command_string)
        self.process = subprocess.Popen(command, 
                                        stdout=subprocess.PIPE,
                                        bufsize=self.frame_size*2)


class RawVideoReader(ReaderBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Open ffmpeg application as sub-process
        # FFmpeg input PIPE: RAW images in BGR color format
        # FFmpeg output MP4 file encoded with HEVC codec.
        # Arguments list:
        # -y                   Overwrite output file without asking
        # -s {width}x{height}  Input resolution width x height (1344x756)
        # -pixel_format bgr24  Input frame color format is BGR with 8 bits per color component
        # -f rawvideo          Input format: raw video
        # -r {fps}             Frame rate: fps (25fps)
        # -i pipe:             ffmpeg input is a PIPE
        # -vcodec libx265      Video codec: H.265 (HEVC)
        # -pix_fmt yuv420p     Output video color space YUV420 (saving space compared to YUV444)
        # -crf 24              Constant quality encoding (lower value for higher quality and larger output file).
        # {input_filename}    Input file name: input_filename (output.mp4)
        command_string = f'ffmpeg -y -i {self.input_filename}.raw -pix_fmt bgr24 -codec:v rawvideo -f image2pipe pipe:1'

        command = shlex.split(command_string)
        self.process = subprocess.Popen(command, 
                                        stdout=subprocess.PIPE,
                                        bufsize=self.frame_size*2)


class HuffyuvLosslessSaver(SaverBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Open ffmpeg application as sub-process
        # FFmpeg input PIPE: RAW images in BGR color format
        # FFmpeg output MP4 file encoded with HEVC codec.
        # Arguments list:
        # -y                   Overwrite output file without asking
        # -s {width}x{height}  Input resolution width x height (1344x756)
        # -pixel_format bgr24  Input frame color format is BGR with 8 bits per color component
        # -f rawvideo          Input format: raw video
        # -r {fps}             Frame rate: fps (25fps)
        # -i pipe:             ffmpeg input is a PIPE
        # -vcodec libx265      Video codec: H.265 (HEVC)
        # -pix_fmt yuv420p     Output video color space YUV420 (saving space compared to YUV444)
        # -crf 24              Constant quality encoding (lower value for higher quality and larger output file).
        # {output_filename}    Output file name: output_filename (output.mp4)

        command_string = f'ffmpeg -y -s {self.width}x{self.height} -pixel_format bgr24 -f rawvideo -r {self.fps} -i pipe: -codec:v huffyuv -pix_fmt yuv422p {self.output_filename}.mkv'

        command = shlex.split(command_string)
        self.process = subprocess.Popen(command,
                                        stdin=subprocess.PIPE,
                                        preexec_fn = os.setpgrp)


class H264LossLessSaver(SaverBackend):
    def __init__(self, *args, compression_rate=0, **kwargs):
        super().__init__(*args, **kwargs)
        # Open ffmpeg application as sub-process
        # FFmpeg input PIPE: RAW images in BGR color format
        # FFmpeg output MP4 file encoded with HEVC codec.
        # Arguments list:
        # -y                   Overwrite output file without asking
        # -s {width}x{height}  Input resolution width x height (1344x756)
        # -pixel_format bgr24  Input frame color format is BGR with 8 bits per color component
        # -f rawvideo          Input format: raw video
        # -r {fps}             Frame rate: fps (25fps)
        # -i pipe:             ffmpeg input is a PIPE
        # -vcodec libx265      Video codec: H.265 (HEVC)
        # -pix_fmt yuv420p     Output video color space YUV420 (saving space compared to YUV444)
        # -crf 24              Constant quality encoding (lower value for higher quality and larger output file).
        # {output_filename}    Output file name: output_filename (output.mp4)

        command_string = f'ffmpeg -y -s {self.width}x{self.height} -pixel_format bgr24 -f rawvideo -r {self.fps} -i pipe: -codec:v libx264 -pix_fmt yuv444p -profile:v high444 -crf {compression_rate} -preset:v slow {self.output_filename}.m4v'

        command = shlex.split(command_string)
        self.process = subprocess.Popen(command,
                                        stdin=subprocess.PIPE,
                                        preexec_fn = os.setpgrp)


class RawVideoSaver(SaverBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Open ffmpeg application as sub-process
        # FFmpeg input PIPE: RAW images in BGR color format
        # FFmpeg output MP4 file encoded with HEVC codec.
        # Arguments list:
        # -y                   Overwrite output file without asking
        # -s {width}x{height}  Input resolution width x height (1344x756)
        # -pixel_format bgr24  Input frame color format is BGR with 8 bits per color component
        # -f rawvideo          Input format: raw video
        # -r {fps}             Frame rate: fps (25fps)
        # -i pipe:             ffmpeg input is a PIPE
        # -vcodec libx265      Video codec: H.265 (HEVC)
        # -pix_fmt yuv420p     Output video color space YUV420 (saving space compared to YUV444)
        # -crf 24              Constant quality encoding (lower value for higher quality and larger output file).
        # {output_filename}    Output file name: output_filename (output.mp4)

        command_string = f'ffmpeg -y -s {self.width}x{self.height} -pixel_format bgr24 -f rawvideo -r {self.fps} -i pipe: -codec:v copy {self.output_filename}.raw'

        command = shlex.split(command_string)
        self.process = subprocess.Popen(command,
                                        stdin=subprocess.PIPE,
                                        preexec_fn = os.setpgrp)

