import cv2, os
import numpy as np
from PySide6.QtGui import QImage, QPixmap
import mrcnn
from mrcnn.config import Config
import mrcnn.model
import mrcnn.visualize

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_XLA_FLAGS'] = '--tf_xla_enable_xla_devices'

def modelRun(image='', subject=str):
    subject = subject.lower()
    with open(image, 'rb') as frame:
        frame = frame.read()


    frame = np.frombuffer(frame, np.uint8)
    img = cv2.imdecode(frame, cv2.IMREAD_COLOR)

    # net = cv2.dnn.readNet('data/pothole.weights', 'data/julnun.cfg')
    net = cv2.dnn.readNet(f'data/{subject}.weights', f'data/{subject}.cfg')

    with open(f"data/{subject}.names", "r") as f:
    # with open("data/pothole.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]
    layer_name = net.getLayerNames()
    output_layers = [layer_name[i - 1] for i in net.getUnconnectedOutLayers()]

    colors = np.random.uniform(0, 255, size=(len(classes), 3))

    img = cv2.imread(image)
    img = cv2.resize(img, None, fx=0.4, fy=0.4)
    height, width, channels = img.shape

    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

    # 전처리된 blob 네트워크에 입력
    net.setInput(blob)

    # 결과 받아오기
    outs = net.forward(output_layers)

    # 각각의 데이터를 저장할 빈 리스트
    class_ids = []
    confidences = []
    boxes = []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > 0.1:
                # 객체의 너비, 높이, 중앙 좌표값
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                # 객체의 좌상단 좌표값
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # 겹치는 박스 제거
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, score_threshold=0.5, nms_threshold=0.6)



    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            class_name = classes[class_ids[i]]
            label = f"{class_name} {round(confidences[i],2)}%"
            color = colors[class_ids[i]]

            cv2.rectangle(img, (x,y), (x+w, y+h), color, 2)
            cv2.rectangle(img, (x+10,y), (x+len(class_name)*13*2-20, y-25), color, -1)
            cv2.putText(img, label, (x+25,y-8), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.6, (0,0,0), 1)

    img_copy = img.copy()
    img_copy = cv2.cvtColor(img_copy, cv2.COLOR_BGR2RGB)
    img_copy = QImage(img_copy, img_copy.shape[1], img_copy.shape[0], img_copy.shape[1] * 3, QImage.Format_RGB888)

    pix = QPixmap(img_copy)

    return pix


class InferenceConfig(Config):
    # inference시에는 batch size를 1로 설정. 그리고 IMAGES_PER_GPU도 1로 설정.
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1  # BATCH_SIZE=1 과 같은 효과
    BATCH_SIZE = 1
    # NAME은 반드시 주어야 한다.
    NAME = 'crack'  # NAME을 꼭 주어야 한다.
    NUM_CLASSES = 2  # Background 0번 + class n개



def mmodelRun(image=''):
    CLASS_NAMES = ["bg", "crack"]
    config = InferenceConfig()

    ROOT_DIR = os.path.abspath('.')
    MODEL_DIR = os.path.join(ROOT_DIR, 'logs')


    model = mrcnn.model.MaskRCNN(mode="inference",
                                 config=config,
                                 model_dir=MODEL_DIR)

    model.load_weights('data/mask_rcnn_crack.h5', by_name=True)

    with open(image, 'rb') as frame:
        frame = frame.read()

    frame = np.frombuffer(frame, np.uint8)
    image = cv2.imdecode(frame, cv2.IMREAD_COLOR)
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    r = model.detect([image], verbose=0)

    r = r[0]

    img = mrcnn.visualize.display_instances(image=image,
                                      boxes=r['rois'],
                                      masks=r['masks'],
                                      class_ids=r['class_ids'],
                                      class_names=CLASS_NAMES,
                                      scores=r['scores'])
    img_copy = img.copy()
    img_copy = cv2.cvtColor(img_copy, cv2.COLOR_BGR2RGB)
    img_copy = QImage(img_copy, img_copy.shape[1], img_copy.shape[0], img_copy.shape[1] * 3, QImage.Format_RGB888)

    pix = QPixmap(img_copy)
    return pix

