from label_image import load_graph, read_tensor_from_image_file, load_labels
import numpy as np
import tensorflow as tf
import requests
import os


class Classifier:
    """
    Wraps the Tensorflow label_image script:
    https://github.com/tensorflow/tensorflow/blob/master/tensorflow/examples/label_image/label_image.py

    Loads the Mobile Soup classifier
    """

    input_name = "import/" + "Placeholder"
    output_name = "import/" + "final_result"
    # size = 299  # size for ImageNet classifier
    size = 224  # size for Mobile Soup

    def __init__(self, graph_name="resources/output_graph_mobile.pb"):
        """
        Initializes the tensorflow session and loads the classifier graph.
        :param graph_name: the graph name can be overridden to use a different model
        """

        self.graph = load_graph(graph_name)
        self.input_operation = self.graph.get_operation_by_name(self.input_name)
        self.output_operation = self.graph.get_operation_by_name(self.output_name)
        self.session = tf.Session(graph=self.graph)
        self.labels = load_labels("resources/output_labels.txt")

        if not os.path.exists("/tmp/photos"):
            os.makedirs("/tmp/photos")

    def __enter__(self):
        """
        Provided to allow using the classifier in a with statement.
        """

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Provided to allow using the classifier in a with statement. Insures session is closed.
        """

        self.session.close()

    def classify(self, image):
        """
        Downloads the image from the scraped url if it has not been cached yet (eg lambda functions being closed).

        Reads the image file and runs the classifier.

        :param image: The image to classify
        :return: the images classification
        """
        print(f"\tclassifying image {image.file_name()}")

        if not os.path.exists(image.file_name()):
            print(f"\tImage not saved, downloading. {image.file_name()}")
            r = requests.get(image.url, timeout=2.0)
            if r.status_code == 200:
                with open(image.file_name(), 'wb') as f:
                    f.write(r.content)

        t = read_tensor_from_image_file(
            image.file_name(),
            input_height=self.size,
            input_width=self.size,
            input_mean=0,
            input_std=255)

        results = self.session.run(self.output_operation.outputs[0], {
            self.input_operation.outputs[0]: t
        })

        results = np.squeeze(results)

        soup_confidence = results[self.labels.index("soup")].astype(float)
        print(f"\tfinished classifying image with soup confidence {soup_confidence}: {image}")
        image.soup_confidence = soup_confidence
