#  -*- coding:utf-8 -*- 
import cv2
import time
import json


class VideoTool(object):

    def __init__(self, casc_path):
        self._face_cascade = cv2.CascadeClassifier(casc_path)

    @classmethod
    def convert_video_2_frame(cls, video=0, width=None, height=None):
        """
        :param video: 0-open Video device, str-video path
        :return: ndarray
        """

        cap = cv2.VideoCapture(video)
        if width is not None:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        if height is not None:
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        try_times = 3
        while try_times > 0:
            try_times -= 1
            if not cap.isOpened():
                print('video can not open')
                time.sleep(1)
                ret = False
            else:
                ret = True
                break

        while ret:
            ret, frame = cap.read()
            if frame is None:
                break
            yield frame

        if hasattr(cap, "release"):
            # 关闭摄像头设备
            cap.release()
            # 关闭所有窗口
            cv2.destroyAllWindows()

    def frame_face_rectangles_detect(self, frame):
        """
        :param frame: ndarray
        :return: list
        """
        # 转为灰度图像
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 调用分类器进行检测
        faces = self._face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
            # flags=cv2.cv.CV_HAAR_SCALE_IMAGE
        )
        return faces

    def get_face_img_from_frame(self, frame):
        for (x, y, w, h) in self.frame_face_rectangles_detect(frame):
            crop_face = frame[y:y+h, x:x+w]
            zoom_rate = w * h * 1.0 / (640 * 360) if w * h > (640 * 360) else 1
            yield cv2.resize(crop_face, dsize=(int(w / zoom_rate), int(h / zoom_rate)), interpolation=cv2.INTER_AREA)

    def get_face_img_from_video(self, video=0):
        frames = self.convert_video_2_frame(video)
        i = 0
        for frame in frames:
            face_rectangles = self.frame_face_rectangles_detect(frame)
            for (x, y, w, h) in face_rectangles:
                # print (x, y, w, h), frame.shape
                crop_face = frame[y:y+h, x:x+w]
                zoom_rate = w*h*1.0/(640*360) if w*h > (640*360) else 1
                yield cv2.resize(crop_face, dsize=(int(w/zoom_rate), int(h/zoom_rate)), interpolation=cv2.INTER_AREA)

    def show(self, frame, windows_name='Video'):
        cv2.imshow(windows_name, frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return


if __name__ == "__main__":
    video_tool = VideoTool("../models/haarcascades/haarcascade_frontalcatface.xml")
    i = 0

    for face_img in video_tool.convert_video_2_frame(8):
        i += 1
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 85]
        result, encimg = cv2.imencode('.jpg', face_img, encode_param)
        print(encimg.tobytes())
        # print(type(json.dumps(encimg)))
        # cv2.imshow("face", cv2.imdecode(encimg, cv2.IMREAD_COLOR))





