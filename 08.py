# -*- coding: utf-8 -*-
"""Копия блокнота "Базовый блок | Рекуррентные и одномерные сверточные нейронные сети | ДЗ Lite | УИИ"

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/11lIzphctkd4ZbDIcaR85fsQOIAfLoP50

1. Из ноутбуков по практике "Рекуррентные и одномерные сверточные нейронные сети" выберите лучшую сеть, либо создайте свою. 
2. Запустите раздел "Подготовка"
3. Подготовьте датасет с параметрами `VOCAB_SIZE=20'000`, `WIN_SIZE=1000`, `WIN_HOP=100`, как в ноутбуке занятия, и обучите выбранную сеть. Параметры обучения можно взять из практического занятия. Для  всех обучаемых сетей в данной работе они должны быть одни и теже.
4. Поменяйте размер словаря tokenaizera (`VOCAB_SIZE`) на `5000`, `10000`, `40000`.  Пересоздайте датасеты, при этом оставьте `WIN_SIZE=1000`, `WIN_HOP=100`.
Обучите выбранную нейронку на этих датасетах.  Сделайте выводы об  изменении  точности распознавания авторов текстов. Результаты сведите в таблицу
5. Поменяйте длину отрезка текста и шаг окна разбиения текста на векторы  (`WIN_SIZE`, `WIN_HOP`) используя значения (`500`,`50`) и (`2000`,`200`). Пересоздайте датасеты, при этом оставьте `VOCAB_SIZE=20000`. Обучите выбранную нейронку на этих датасетах. Сделайте выводы об  изменении точности распознавания авторов текстов. 

Результаты всей работы сведите в таблицу.

## Подготовка
"""

# Commented out IPython magic to ensure Python compatibility.
# Работа с массивами данных
import numpy as np 

# Функции-утилиты для работы с категориальными данными
from tensorflow.keras import utils

# Класс для конструирования последовательной модели нейронной сети
from tensorflow.keras.models import Sequential

# Основные слои
from tensorflow.keras.layers import Dense, Dropout, SpatialDropout1D, BatchNormalization, Embedding, Flatten, Activation
from tensorflow.keras.layers import SimpleRNN, GRU, LSTM, Bidirectional, Conv1D, MaxPooling1D, GlobalMaxPooling1D

# Токенизатор для преобразование текстов в последовательности
from tensorflow.keras.preprocessing.text import Tokenizer

# Рисование схемы модели
from tensorflow.keras.utils import plot_model

# Матрица ошибок классификатора
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

# Загрузка датасетов из облака google
import gdown

# Функции операционной системы
import os

# Работа со временем
import time

# Регулярные выражения
import re

# Отрисовка графиков
import matplotlib.pyplot as plt

# Вывод объектов в ячейке colab
from IPython.display import display

# %matplotlib inline

# Загрузим датасет из облака
gdown.download('https://storage.yandexcloud.net/aiueducation/Content/base/l7/writers.zip', None, quiet=True)

# Распакуем архив в папку writers
!unzip -o writers.zip -d writers/

# Настройка констант для загрузки данных
FILE_DIR  = 'writers'                     # Папка с текстовыми файлами
SIG_TRAIN = 'обучающая'                   # Признак обучающей выборки в имени файла
SIG_TEST  = 'тестовая'                    # Признак тестовой выборки в имени файла

# Подготовим пустые списки

CLASS_LIST = []  # Список классов 
text_train = []  # Список для обучающей выборки
text_test = []   # Список для тестовой выборки

# Получим списка файлов в папке
file_list = os.listdir(FILE_DIR)

for file_name in file_list:
    # Выделяем имя класса и типа выборки из имени файла
    m = re.match('\((.+)\) (\S+)_', file_name)
    # Если выделение получилось, то файл обрабатываем
    if m:

        # Получим имя класса
        class_name = m[1]

        # Получим имя выборки
        subset_name = m[2].lower()

        # Проверим тип выборки 
        is_train = SIG_TRAIN in subset_name
        is_test = SIG_TEST in subset_name

        # Если тип выборки обучающая либо тестовая - файл обрабатываем
        if is_train or is_test:

            # Добавляем новый класс, если его еще нет в списке
            if class_name not in CLASS_LIST:
                print(f'Добавление класса "{class_name}"')
                CLASS_LIST.append(class_name)

                # Инициализируем соответствующих классу строки текста
                text_train.append('')
                text_test.append('')

            # Найдем индекс класса для добавления содержимого файла в выборку
            cls = CLASS_LIST.index(class_name)
            print(f'Добавление файла "{file_name}" в класс "{CLASS_LIST[cls]}", {subset_name} выборка.')

            # Откроем файл на чтение  
            with open(f'{FILE_DIR}/{file_name}', 'r') as f:  

                # Загрузим содержимого файла в строку
                text = f.read()
            # Определим выборку, куда будет добавлено содержимое
            subset = text_train if is_train else text_test

            # Добавим текста к соответствующей выборке класса. Концы строк заменяются на пробел
            subset[cls] += ' ' + text.replace('\n', ' ')

# Определим количество классов
CLASS_COUNT = len(CLASS_LIST)
print(CLASS_COUNT)

# Выведем прочитанные классы текстов
print(CLASS_LIST)

# Посчитаем количество текстов в обучающей выборке
print(len(text_train))

# Проверим загрузки: выведем начальные отрывки из каждого класса

for cls in range(CLASS_COUNT):                   # Запустим цикл по числу классов
    print(f'Класс: {CLASS_LIST[cls]}')           # Выведем имя класса
    print(f'  train: {text_train[cls][:200]}')   # Выведем фрагмент обучающей выборки
    print(f'  test : {text_test[cls][:200]}')    # Выведем фрагмент тестовой выборки
    print()

# Контекстный менеджер для измерения времени операций
# Операция обертывается менеджером с помощью оператора with

class timex:
    def __enter__(self):
        # Фиксация времени старта процесса
        self.t = time.time()
        return self

    def __exit__(self, type, value, traceback):
        # Вывод времени работы
        print('Время обработки: {:.2f} с'.format(time.time() - self.t))

"""## Решение"""

# Токенизация и построение частотного словаря по обучающим текстам
def build_vocab(text_list, vocab_size=10000):
  with timex():
      # Используется встроенный в Keras токенизатор для разбиения текста и построения частотного словаря
      tokenizer = Tokenizer(num_words=vocab_size, filters='!"#$%&()*+,-–—./…:;<=>?@[\\]^_`{|}~«»\t\n\xa0\ufeff', lower=True, split=' ', oov_token='неизвестное_слово', char_level=False)

      # Использованы параметры:
      # num_words   - объем словаря
      # filters     - убираемые из текста ненужные символы
      # lower       - приведение слов к нижнему регистру
      # split       - разделитель слов
      # char_level  - указание разделять по словам, а не по единичным символам
      # oov_token   - токен для слов, которые не вошли в словарь

      # Построение частотного словаря по обучающим текстам
      tokenizer.fit_on_texts(text_list)
      
      # Построение словаря в виде пар слово - индекс
      vocab = list(tokenizer.word_index.items())

      # 
      seq = tokenizer.texts_to_sequences(text_list)

      print("STATISTICS")
        # Вывод нескольких наиболее часто встречающихся слов
      print(vocab[:120])
      # Размер словаря может быть больше, чем num_words, но при преобразовании в последовательности
      # и векторы bag of words будут учтены только первые num_words слов
      print("Размер словаря", len(vocab)) 
      print("Фрагмент обучающего текста:")
      print("  В виде оригинального текста:              ", text_list[1][:101])
      print("  Он же в виде последовательности индексов: ", seq[1][:20])

  return vocab, seq

"""### Проверка функции build_vocab

"""

print('TRAIN')
vocab_train, seq_train = build_vocab(text_train, 20000)

print('TEST')
vocab_test, seq_test = build_vocab(text_test, 20000)

"""## Статистика по текстам"""

# Функция вывода статистики по текстам
def print_text_stats(title, texts, sequences, class_labels=CLASS_LIST):
    # Суммарное количество символов и слов в тексте
    chars = 0
    words = 0

    print(f'Статистика по {title} текстам:')

    # Вывод итогов по всем классам данного набора текстов и их последовательностей индексов
    for cls in range(len(class_labels)):
        print('{:<15} {:9} символов,{:8} слов'.format(class_labels[cls],
                                                      len(texts[cls]),
                                                      len(sequences[cls])))
        chars += len(texts[cls])
        words += len(sequences[cls])

    print('----')
    print('{:<15} {:9} символов,{:8} слов\n'.format('В сумме', chars, words))

# Вывод итогов по текстам
print_text_stats('обучающим', text_train, seq_train)
print_text_stats('тестовым', text_test, seq_test)

"""## Функции формирования выборки

sequence – последовательность индексов;  
win_size – размер окна;  
hop – шаг окна.  
"""

# Функция разбиения последовательности на отрезки скользящим окном
# На входе - последовательность индексов, размер окна, шаг окна
def split_sequence(sequence, win_size, hop):
    # Последовательность разбивается на части до последнего полного окна
    return [sequence[i:i + win_size] for i in range(0, len(sequence) - win_size + 1, hop)]


# Функция формирования выборок из последовательностей индексов
# формирует выборку отрезков и соответствующих им меток классов в виде one hot encoding
def vectorize_sequence(seq_list, win_size, hop):
    # В списке последовательности следуют в порядке их классов
    # Всего последовательностей в списке ровно столько, сколько классов
    class_count = len(seq_list)

    # Списки для исходных векторов и категориальных меток класса
    x, y = [], []

    # Для каждого класса:
    for cls in range(class_count):
        # Разбиение последовательности класса cls на отрезки
        vectors = split_sequence(seq_list[cls], win_size, hop)
        # Добавление отрезков в выборку
        x += vectors
        # Для всех отрезков класса cls добавление меток класса в виде OHE
        y += [utils.to_categorical(cls, class_count)] * len(vectors)

    # Возврат результатов как numpy-массивов
    return np.array(x), np.array(y)

"""## Функции для модели (из-зи ограничений ресурсов убираю всё лишнее)

Напишите три уже стандартные функции:

первая – создание, компиляция, обучение и вывод статистики по модели;
вторая – вывод результатов оценки модели;
третья – функция, объединяющая первую и вторую.
"""

# Функция компиляции и обучения модели нейронной сети
def compile_train_model(model, 
                        x_train,
                        y_train,
                        x_val,
                        y_val,
                        optimizer='adam',
                        epochs=50,
                        batch_size=128,
                        figsize=(20, 5)):

    # Компиляция модели
    model.compile(optimizer=optimizer, 
                  loss='categorical_crossentropy', 
                  metrics=['accuracy'])

    # Вывод сводки
    # model.summary()

    # Вывод схемы модели
    # display(plot_model(model, dpi=60, show_shapes=True))

    # Обучение модели с заданными параметрами
    history = model.fit(x_train,
                        y_train,
                        epochs=epochs,
                        batch_size=batch_size,
                        validation_data=(x_val, y_val))

    # Вывод графиков точности и ошибки
    # fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    # fig.suptitle('График процесса обучения модели')
    # ax1.plot(history.history['accuracy'], 
    #            label='Доля верных ответов на обучающем наборе')
    # ax1.plot(history.history['val_accuracy'], 
    #            label='Доля верных ответов на проверочном наборе')
    # ax1.xaxis.get_major_locator().set_params(integer=True)
    # ax1.set_xlabel('Эпоха обучения')
    # ax1.set_ylabel('Доля верных ответов')
    # ax1.legend()

    # ax2.plot(history.history['loss'], 
    #            label='Ошибка на обучающем наборе')
    # ax2.plot(history.history['val_loss'], 
    #            label='Ошибка на проверочном наборе')
    # ax2.xaxis.get_major_locator().set_params(integer=True)
    # ax2.set_xlabel('Эпоха обучения')
    # ax2.set_ylabel('Ошибка')
    # ax2.legend()
    # plt.show()

# Функция вывода результатов оценки модели на заданных данных
def eval_model(model, x, y_true,
               class_labels=[],
               cm_round=3,
               title='',
               figsize=(10, 10)):
    # Вычисление предсказания сети
    y_pred = model.predict(x)
    # Построение матрицы ошибок
    cm = confusion_matrix(np.argmax(y_true, axis=1),
                          np.argmax(y_pred, axis=1),
                          normalize='true')
    # Округление значений матрицы ошибок
    cm = np.around(cm, cm_round)

    # Отрисовка матрицы ошибок
    # fig, ax = plt.subplots(figsize=figsize)
    # ax.set_title(f'Нейросеть {title}: матрица ошибок нормализованная', fontsize=18)
    # disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_labels)
    # disp.plot(ax=ax)
    # plt.gca().images[-1].colorbar.remove()  # Стирание ненужной цветовой шкалы
    # plt.xlabel('Предсказанные классы', fontsize=16)
    # plt.ylabel('Верные классы', fontsize=16)
    # fig.autofmt_xdate(rotation=45)          # Наклон меток горизонтальной оси при необходимости
    # plt.show()    

    print('-'*100)
    print(f'Нейросеть: {title}')

    # Для каждого класса:
    for cls in range(len(class_labels)):
        # Определяется индекс класса с максимальным значением предсказания (уверенности)
        cls_pred = np.argmax(cm[cls])
        # Формируется сообщение о верности или неверности предсказания
        msg = 'ВЕРНО :-)' if cls_pred == cls else 'НЕВЕРНО :-('
        # Выводится текстовая информация о предсказанном классе и значении уверенности
        print('Класс: {:<20} {:3.0f}% сеть отнесла к классу {:<20} - {}'.format(class_labels[cls],
                                                                               100. * cm[cls, cls_pred],
                                                                               class_labels[cls_pred],
                                                                               msg))
    avg_accuracy = 100. * cm.diagonal().mean()
    # Средняя точность распознавания определяется как среднее диагональных элементов матрицы ошибок
    print('\nСредняя точность распознавания: {:3.0f}%'.format(avg_accuracy))
    return avg_accuracy


# Совместная функция обучения и оценки модели нейронной сети
def compile_train_eval_model(model, 
                             x_train,
                             y_train,
                             x_test,
                             y_test,
                             class_labels=CLASS_LIST,
                             title='',
                             optimizer='adam',
                             epochs=50,
                             batch_size=128,
                             graph_size=(20, 5),
                             cm_size=(10, 10)):

    # Компиляция и обучение модели на заданных параметрах
    # В качестве проверочных используются тестовые данные
    compile_train_model(model, 
                        x_train, y_train,
                        x_test, y_test,
                        optimizer=optimizer,
                        epochs=epochs,
                        batch_size=batch_size,
                        figsize=graph_size)

    # Вывод результатов оценки работы модели на тестовых данных
    avg_accuracy = eval_model(model, x_test, y_test, 
               class_labels=class_labels, 
               title=title,
               figsize=cm_size)
    
    return avg_accuracy

"""## Основной цикл для модели №13: Embedding(50) + BLSTM(8)x2 + GRU(16)x2 + Dense(200)

Подготовьте датасет с параметрами VOCAB_SIZE=20'000, WIN_SIZE=1000, WIN_HOP=100, как в ноутбуке занятия, и обучите выбранную сеть. Параметры обучения можно взять из практического занятия. Для всех обучаемых сетей в данной работе они должны быть одни и теже.
Поменяйте размер словаря tokenaizera (VOCAB_SIZE) на 5000, 10000, 40000. Пересоздайте датасеты, при этом оставьте WIN_SIZE=1000, WIN_HOP=100. Обучите выбранную нейронку на этих датасетах. Сделайте выводы об изменении точности распознавания авторов текстов. Результаты сведите в таблицу
Поменяйте длину отрезка текста и шаг окна разбиения текста на векторы (WIN_SIZE, WIN_HOP) используя значения (500,50) и (2000,200). Пересоздайте датасеты, при этом оставьте VOCAB_SIZE=20000. Обучите выбранную нейронку на этих датасетах. Сделайте выводы об изменении точности распознавания авторов текстов.
Результаты всей работы сведите в таблицу.
"""

import pandas as pd
df = pd.DataFrame(columns = ['VOCAB_SIZE', 'WIN_SIZE', 'WIN_HOP', 'avg_accuracy'])

for VOCAB_SIZE in [5000, 10000, 20000, 40000]:
  vocab_train, seq_train, vocab_test, seq_test = None, None, None, None
  vocab_train, seq_train = build_vocab(text_train, VOCAB_SIZE)
  vocab_test, seq_test = build_vocab(text_test, VOCAB_SIZE)
  for WIN_SIZE in [50, 500, 1000]:
    for WIN_HOP in [100, 200, 2000]:
      print(3*"\n")
      print(80*"=")
      print(f"VOCAB_SIZE={VOCAB_SIZE}; WIN_SIZE={WIN_SIZE}; WIN_HOP={WIN_HOP}")

      x_train, y_train, x_test, y_test, model_LSTM_6 = None, None, None, None, None
      # Формирование обучающей и тестовой выборок
      # with timex():
      # Формирование обучающей выборки
      x_train, y_train = vectorize_sequence(seq_train, WIN_SIZE, WIN_HOP) 
      # Формирование тестовой выборки
      x_test, y_test = vectorize_sequence(seq_test, WIN_SIZE, WIN_HOP)

      # Проверка формы сформированных данных
      print(x_train.shape, y_train.shape)
      print(x_test.shape, y_test.shape)

      # Создание модели
      model_LSTM_6 = Sequential()
      model_LSTM_6.add(Embedding(VOCAB_SIZE, 50, input_length=WIN_SIZE))
      model_LSTM_6.add(SpatialDropout1D(0.4))
      model_LSTM_6.add(BatchNormalization())
      # Два двунаправленных рекуррентных слоя LSTM
      # model_LSTM_6.add(Bidirectional(LSTM(8, return_sequences=True)))
      # model_LSTM_6.add(Bidirectional(LSTM(8, return_sequences=True)))
      # model_LSTM_6.add(Dropout(0.3))
      # model_LSTM_6.add(BatchNormalization())
      # Два рекуррентных слоя GRU
      model_LSTM_6.add(GRU(16, return_sequences=True, reset_after=True))
      model_LSTM_6.add(GRU(16, reset_after=True))
      model_LSTM_6.add(Dropout(0.3))
      model_LSTM_6.add(BatchNormalization())
      # Дополнительный полносвязный слой
      model_LSTM_6.add(Dense(200, activation='relu'))
      model_LSTM_6.add(Dropout(0.3))
      model_LSTM_6.add(BatchNormalization())
      model_LSTM_6.add(Dense(CLASS_COUNT, activation='softmax'))

      avg_accuracy = compile_train_eval_model(model_LSTM_6,
                              x_train, y_train,
                              x_test, y_test,
                              optimizer='rmsprop',
                              epochs=50,
                              batch_size=512,
                              class_labels=CLASS_LIST,
                              title='mynet')
      print(f"{VOCAB_SIZE};{WIN_SIZE};{WIN_HOP};{avg_accuracy}")
      df = df.append({'VOCAB_SIZE' : VOCAB_SIZE, 'WIN_SIZE' : WIN_SIZE, 'WIN_HOP' : WIN_HOP, 'avg_accuracy' : avg_accuracy}, ignore_index = True)
      df.to_csv('results.csv', index=False)

"""## Результирующая таблица"""

df