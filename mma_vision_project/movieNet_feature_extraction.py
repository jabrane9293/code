# Step 4 & 5: Use MoViNet for Feature Extraction and Classification
import tensorflow as tf
from tf_video.models import MoViNet
from tf_video.utils import load_pretrained_weights

# Load the pre-trained MoViNet model
model_id = 'a2'  # You can use other versions like 'a0', 'a1', etc. depending on your needs
model = MoViNet(model_id=model_id, causal=False, conv_type='2plus1d')
model.build([1, None, 224, 224, 3])
load_pretrained_weights(model, model_id=model_id, pretrained=True)

# MoViNet expects a sequence of frames as input, reshape accordingly
batch_size = len(preprocessed_frames)
input_frames = preprocessed_frames.reshape((1, batch_size, 224, 224, 3))

# Classify the video segment
predictions = model.predict(input_frames)

# Convert predictions to readable labels (assuming a predefined label set)
labels = ['background', 'fighting', 'sparring', 'talking', 'eating']

# Get the predicted label for each frame
predicted_labels = [labels[np.argmax(pred)] for pred in predictions]

