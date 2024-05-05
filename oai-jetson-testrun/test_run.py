import timeit
import_module='''
import tensorflow as tf
from tensorflow import keras
import numpy as np
import tifffile
import os

image_path=['./images/'+i for i in os.listdir('./images')]
mask_path=['./annotations/'+i for i in os.listdir('./annotations')]
val_img_path=image_path
val_msk_path=mask_path

class CustomDataLoader(keras.utils.Sequence):
    def __init__(self, img_path,msk_path, batch_size=8, input_shape=(256,256,4), shuffle=True):
        self.image_paths = img_path
        self.mask_paths =  msk_path
        self.batch_size = batch_size
        self.input_shape = input_shape
        self.shuffle = shuffle
        self.indexes = np.arange(len(self.image_paths))

    def __len__(self):
        return int(np.ceil(len(self.image_paths) / self.batch_size))

    def on_epoch_end(self):
        if self.shuffle:
            np.random.shuffle(self.indexes)

    def __getitem__(self, index):
        batch_image_paths = self.image_paths[index * self.batch_size:(index + 1) * self.batch_size]
        batch_mask_paths = self.mask_paths[index * self.batch_size:(index + 1) * self.batch_size]
        
        X = np.zeros((len(batch_image_paths), *self.input_shape), dtype=float)
        y = np.zeros((len(batch_mask_paths), *self.input_shape[:-1], 1), dtype=float)
        
        for i in range(len(batch_image_paths)):
            image = tifffile.imread(batch_image_paths[i])
            red_band = image[:, :, 0]
            green_band =image[:, :, 1]
            blue_band = image[:, :, 2]
            nir_band = image[:, :, 3]
            ndwi = (green_band - nir_band) / (green_band + nir_band)
            ndwi =ndwi>0.01
            X[i] = np.stack([red_band, green_band, blue_band, ndwi], axis=-1)
            y[i] = np.expand_dims(tifffile.imread(batch_mask_paths[i]), axis=-1)

        return X, y


val_loader=CustomDataLoader(val_img_path,val_msk_path)

idx=0
sample_batch = val_loader[idx]
images, masks = sample_batch

interpreter = tf.lite.Interpreter(model_path='quantized_model_new.tflite')
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

interpreter.set_tensor(input_details[0]['index'], np.expand_dims(images[0],axis=0).astype(np.float32))
interpreter.invoke()
'''

test_code='''
def main(interpreter,output):
    output_data = interpreter.get_tensor(output_details[0]['index'])
    print("Output:", output_data.shape)
'''

print(timeit.repeat(stmt=test_code, setup=import_module,repeat=5))


# plt.imshow(output_data[0])
