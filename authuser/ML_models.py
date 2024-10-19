from tensorflow.keras.models import load_model
import os
from django.conf import settings

def load_1day_model():
    model_path = os.path.join(settings.MODEL_DIR, 'improved_model.keras')
    model = load_model(model_path)
    return model