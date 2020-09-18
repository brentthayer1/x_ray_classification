import os
import sys


from flask import Flask, redirect, url_for, request, render_template, Response, jsonify, redirect
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer

import tensorflow as tf
from tensorflow import keras

from tensorflow.keras.applications.imagenet_utils import preprocess_input, decode_predictions
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image


import numpy as np
from util import base64_to_pil


app = Flask(__name__)

MODEL_PATH = 'models/cov_pneum_9_6.h5'
model = load_model(MODEL_PATH)

print('Model loaded. Start serving...')


def model_predict(img, model):
    img = img.resize((300, 300))
    input_arr = image.img_to_array(image)
    # input_arr = np.array([input_arr])
    input_arr = input_arr / 255
    probs = model.predict(input_arr)
    return probs
    # img = img.resize((300, 300))

    # # Preprocessing the image
    # x = image.img_to_array(img)
    # # x = np.true_divide(x, 255)
    # x = np.expand_dims(x, axis=0)

    # # Be careful how your trained model deals with the input
    # # otherwise, it won't make correct prediction!
    # # x = preprocess_input(x, mode='tf')

    # probs = model.predict(x)
    # return probs


@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    
    if request.method == 'POST':
        # Get the image from post request
        img = base64_to_pil(request.json)

        # Save the image to ./uploads
        # img.save("./uploads/image.png")

        # Make prediction
        preds = model_predict(img, model)

        # Process your result for human
        # pred_proba = "{:.3f}".format(np.amax(preds))    # Max probability
        # pred_class = decode_predictions(preds, top=1)   # ImageNet Decode

        # result = str(pred_class[0][0][1])               # Convert to string
        # result = result.replace('_', ' ').capitalize()
        pred_class = np.argmax(preds)

        class_dict = {0 : 'COVID-19',
              1 : 'Normal',
              2 : 'Pneumonia'}

        result = class_dict[pred_class]
        
        # Serialize the result, you can add additional fields
        # return jsonify(result=result)#, probability=pred_proba)
        return result
    return None


if __name__ == '__main__':
    # app.run(port=5002, threaded=False)

    # Serve the app with gevent
    http_server = WSGIServer(('0.0.0.0', 5000), app)
    http_server.serve_forever()
