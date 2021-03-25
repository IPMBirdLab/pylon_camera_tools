
##################################################
##  setting up signal controller    ##############
##################################################
import os
import signal

original_sigint = None
# how many time we need to ignore Ctrl+C and continue running
# it is useful if we need to terminate one loop and go to the next one
# somehow a simple flow control mechanism
tolerance = 2

def receiveSignal(signalNumber, frame):
    global run_the_loop, original_sigint, tolerance

    # code snippet is borrowef from:
    # https://stackoverflow.com/questions/18114560/python-catch-ctrl-c-command-prompt-really-want-to-quit-y-n-resume-executi
    # restore the original signal handler as otherwise evil things will happen
    # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
    tolerance -= 1
    if tolerance == 0:
        signal.signal(signal.SIGINT, original_sigint)
    
    # reset run_the_loop before going into your next loop
    run_the_loop = False
    return

##################################################

from pypylon import pylon
from pypylon import genicam
import cv2
from time import sleep
from PylonCameraTools.IO import HuffyuvLosslessReader, HuffyuvLosslessSaver, \
    H264LossLessReader, H264LossLessSaver, \
    RawVideoReader, RawVideoSaver, VideoReader, VideoSaver
from PylonCameraTools.utils.camera_utils import adjust_croped_offset, \
    initialize_camera, set_configurations_for, \
    print_camera_status, enable_metadate_gathering


run_the_loop = True

def main_loop_writer(config):
    global run_the_loop

    saver = VideoSaver(HuffyuvLosslessSaver, config["name"], config["width"], config["height"], config["fps"])

    # conecting to the first available camera
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    camera.Open()

    camera = set_configurations_for(camera, config)
    camera = enable_metadate_gathering(camera)

    # Grabing Continusely (video) with minimal delay
    # pylon.GrabStrategy_OneByOne
    #       The images are processed in the order of their arrival.
    # pylon.GrabStrategy_LatestImageOnly
    #       images are processed in the order of their arrival but only 
    #       the last received image is kept in the output queue.
    #       This strategy can be useful when the acquired images are 
    #       only displayed on the screen. If the processor has been busy
    #       for a while and images could not be displayed automatically
    #       the latest image is displayed when processing time is available again.
    camera.StartGrabbing(pylon.GrabStrategy_OneByOne) 
    
    print_camera_status(camera)
    while run_the_loop and camera.IsGrabbing():
        grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

        # print("Chunk Timestamp ", grabResult.ChunkTimestamp.GetValue())
        # print("Chunk Frame Counter ", grabResult.ChunkFramecounter.GetValue())

        if grabResult.GrabSucceeded():
            frame = saver.save_camera_frame(grabResult)

            # cv2.namedWindow('Live Monitoring', cv2.WINDOW_NORMAL)
            # cv2.imshow('Live Monitoring', frame)
            # k = cv2.waitKey(1)
            # if k == 27: # Esc
            #     break
        grabResult.Release()
        
    
    try:
        if not run_the_loop:
            print('\n\n******Received Signal: INT')
            print('******Terminating the program. press Ctrl+C again to fource quit.\n\n')
        print("******Releasing resources\n\n")
        del saver
        camera.StopGrabbing()
        camera.Close()
        cv2.destroyAllWindows()
    except KeyboardInterrupt:
        print("******Ok Ok, quitting")


def main_loop_reader(config):
    global run_the_loop
    reader = VideoReader(H264LossLessReader, config["name"], (config["width"], config["height"]), config["fps"])

    while True:
        frame, meta_data = reader.read_frame()
        if frame is None:
            print("*******Got None frame")
            break

        cv2.namedWindow('playback', cv2.WINDOW_NORMAL)
        cv2.imshow('playback', frame)
        k = cv2.waitKey(1)
        if k == 27: # Esc
            break

    if not run_the_loop:
        print('\n\n******Received Signal: INT')
        print('******Terminating the program. press Ctrl+C again to fource quit.\n\n')
    print("******Releasing resources\n\n")
    del reader
    cv2.destroyAllWindows()


config = {
    "name": "/home/devuser/Documents/workspace/data/experiment3_400-400.m4v",
    "width": 400,
    "height": 400,
    "fps": 40,
}

if __name__ == "__main__":
    # store the original SIGINT handler
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, receiveSignal)

    print(f"******Running Application with PID: {os.getpid()}")
    print("******press Ctrl+C to terminate.\n\n")

    # main_loop_writer(config)
    # sleep(1)
    run_the_loop = True
    main_loop_reader(config)
