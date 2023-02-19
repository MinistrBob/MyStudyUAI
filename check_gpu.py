# import tensorflow as tf
# # print('CUDA available' if tf.config.list_physical_devices('GPU') else 'CUDA not available')"
# gpu = tf.config.list_physical_devices('GPU')
# print(gpu)

for VOCAB_SIZE in [5000, 10000, 20000, 40000]:
  for WIN_SIZE in [50, 500, 1000]:
    for WIN_HOP in [100, 200, 2000]:
      print(f"VOCAB_SIZE={VOCAB_SIZE}; WIN_SIZE={WIN_SIZE}; WIN_HOP={WIN_HOP}")