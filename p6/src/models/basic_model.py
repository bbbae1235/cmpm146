# from models.model import Model
# from keras import Sequential, layers
# # from keras.layers.experimental.preprocessing import Rescaling
# from keras.optimizers import RMSprop, Adam

# class BasicModel(Model):
#     def _define_model(self, input_shape, categories_count):
#         # Your code goes here
#         # you have to initialize self.model to a keras model
#         # before dense, flatten everything
#         self.model = Sequential()
#         # rescale to 0-1 range
#         self.model.add(layers.Rescaling(1./255, input_shape=input_shape))
#         # convolution layer
#         self.model.add(layers.Conv2D(16, (3, 3), activation='relu'))
#         self.model.add(layers.MaxPooling2D((4, 4)))
#         self.model.add(layers.Conv2D(26, (3, 3), activation='relu'))
#         self.model.add(layers.MaxPooling2D((4, 4)))
#         # flatten layer
#         self.model.add(layers.Flatten())
#         # dense layers
#         self.model.add(layers.Dense(84, activation='relu'))
#         self.model.add(layers.Dense(categories_count, activation='softmax'))
       
#     def _compile_model(self):
#         # Your code goes here
#         # you have to compile the keras model, similar to the example in the writeup
#         self.model.compile(
#             optimizer=Adam(learning_rate=0.001),
#             loss='categorical_crossentropy',
#             metrics=['accuracy'],
#         )

from models.model import Model
from keras import Sequential, layers
from keras.optimizers import Adam
from keras.layers import Dropout

class BasicModel(Model):
    def __init__(self, input_shape, categories_count, learning_rate=0.001, conv_layers=2, dense_units=84, dropout_rate=0.0):
        self.learning_rate = learning_rate
        self.conv_layers = conv_layers
        self.dense_units = dense_units
        self.dropout_rate = dropout_rate
        super().__init__(input_shape, categories_count)

    def _define_model(self, input_shape, categories_count):
        self.model = Sequential()
        self.model.add(layers.Rescaling(1./255, input_shape=input_shape))
        
        for _ in range(self.conv_layers):
            self.model.add(layers.Conv2D(16, (3, 3), activation='relu'))
            self.model.add(layers.MaxPooling2D((4, 4)))
            if self.dropout_rate > 0.0:
                self.model.add(Dropout(self.dropout_rate))

        self.model.add(layers.Flatten())
        self.model.add(layers.Dense(self.dense_units, activation='relu'))
        
        if self.dropout_rate > 0.0:
            self.model.add(Dropout(self.dropout_rate))
        
        self.model.add(layers.Dense(categories_count, activation='softmax'))

    def _compile_model(self):
        self.model.compile(
            optimizer=Adam(learning_rate=self.learning_rate),
            loss='categorical_crossentropy',
            metrics=['accuracy'],
        )