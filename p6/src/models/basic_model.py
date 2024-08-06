from models.model import Model
from keras import Sequential, layers
# from keras.layers.experimental.preprocessing import Rescaling
from keras.optimizers import RMSprop, Adam

class BasicModel(Model):
    def _define_model(self, input_shape, categories_count):
        # Your code goes here
        # you have to initialize self.model to a keras model
        # before dense, flatten everything
        self.model = Sequential()
        # rescale to 0-1 range
        self.model.add(layers.Rescaling(1./255, input_shape=input_shape))
        # convolution layer
        self.model.add(layers.Conv2D(16, (3, 3), activation='relu'))
        self.model.add(layers.MaxPooling2D((3, 3)))
        self.model.add(layers.Conv2D(48, (3, 3), activation='relu'))
        self.model.add(layers.MaxPooling2D((3, 3)))
        self.model.add(layers.Conv2D(72, (3, 3), activation='relu'))
        self.model.add(layers.MaxPooling2D((3, 3)))
        # flatten layer
        self.model.add(layers.Flatten())
        # dense layers
        self.model.add(layers.Dense(96, activation='relu'))
        self.model.add(layers.Dense(categories_count, activation='softmax'))
       
    def _compile_model(self):
        # Your code goes here
        # you have to compile the keras model, similar to the example in the writeup
        self.model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy'],
        )