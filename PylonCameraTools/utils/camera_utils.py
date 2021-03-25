
def adjust_croped_offset(camera):
    if genicam.IsWritable(camera.OffsetX):
        offx = (camera.Width.GetMax() - camera.Width.GetValue()) // 2
        while(offx % camera.Width.GetInc() != 0):
            offx -= 1
        camera.OffsetX.SetValue(offx)
    if genicam.IsWritable(camera.OffsetY):
        offy = (camera.Height.GetMax() - camera.Height.GetValue()) // 2
        while(offy % camera.Height.GetInc() != 0):
            offy -= 1
        camera.OffsetY.SetValue(offy)
    return camera


def initialize_camera(camera):
    camera.OffsetX.SetValue(8)
    camera.OffsetY.SetValue(8)


def set_configurations_for(camera, config):
    initialize_camera(camera)

    camera.Width.SetValue(config.get("width", 400))
    camera.Height.SetValue(config.get("height", 400))

    # Adjust the Image AOI.
    camera = adjust_croped_offset(camera)

    camera.StreamGrabber.FrameRetention.SetValue(config.get("fps", 60))

    return camera


def print_camera_status(camera):
    print("Using device ", camera.GetDeviceInfo().GetModelName())
    print("Frame Width ", camera.Width.GetValue())
    print("Frame Height ", camera.Height.GetValue())
    print("Frame Rate ", camera.StreamGrabber.FrameRetention.GetValue())

    print("Frame Width max available :", camera.Width.GetMax())
    print("Frame Height max available :", camera.Height.GetMax())

    print("Exposure Time (ms) ", camera.ExposureTimeAbs.GetValue())
    print("Gain (Raw) ", camera.GainRaw.GetValue())

    print("Board Temperature ", camera.TemperatureAbs.GetValue())
    print("isCritical Temperature ", camera.CriticalTemperature.GetValue())
    print("isOver Temperature ", camera.OverTemperature.GetValue())


def enable_metadate_gathering(camera):
    # Enable chunks in general.
    if genicam.IsWritable(camera.ChunkModeActive):
        camera.ChunkModeActive = True
    else:
        raise pylon.RuntimeException("The camera doesn't support chunk features")

    # Enable time stamp chunks.
    camera.ChunkSelector = "Timestamp"
    camera.ChunkEnable = True

    if not camera.IsUsb():
        # Enable frame counter chunks.
        camera.ChunkSelector = "Framecounter"
        camera.ChunkEnable = True

    return camera
