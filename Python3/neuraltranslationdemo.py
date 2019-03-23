# encoding: utf-8

import os
import numpy as np

import tensorflow as tf
from tensorflow.python.ops import rnn_cell, rnn, seq2seq

import skflow

# Get training data

# This dataset can be downloaded from http://www.statmt.org/europarl/v6/fr-en.tgz

# Translation model

MAX_DOCUMENT_LENGTH = 10
HIDDEN_SIZE = 10

def rnn_decoder(decoder_inputs, initial_state, cell, scope=None):
    with tf.variable_scope(scope or "dnn_decoder"):
        states, sampling_states = [initial_state], [initial_state]
        outputs, sampling_outputs = [], []
        with tf.op_scope([decoder_inputs, initial_state], "training"):
            for i in range(len(decoder_inputs)):
                inp = decoder_inputs[i]
                if i > 0:
                    tf.get_variable_scope().reuse_variables()
                output, new_state = cell(inp, states[-1])
                outputs.append(output)
                states.append(new_state)
        with tf.op_scope([initial_state], "sampling"):
            for i in range(len(decoder_inputs)):
                if i == 0:
                    sampling_outputs.append(outputs[i])
                    sampling_states.append(states[i])
                else:
                    sampling_output, sampling_state = cell(sampling_outputs[-1], sampling_states[-1])
                    sampling_outputs.append(sampling_output)
                    sampling_states.append(sampling_state)
    return outputs, states, sampling_outputs, sampling_states


def rnn_seq2seq(encoder_inputs, decoder_inputs, cell, dtype=tf.float32, scope=None):
    with tf.variable_scope(scope or "rnn_seq2seq"):
        _, enc_states = rnn.rnn(cell, encoder_inputs, dtype=dtype)
        return rnn_decoder(decoder_inputs, enc_states[-1], cell)


def translate_model(X, y):
    byte_list = skflow.ops.one_hot_matrix(X, 256)
    in_X, in_y, out_y = skflow.ops.seq2seq_inputs(
        byte_list, y, MAX_DOCUMENT_LENGTH, MAX_DOCUMENT_LENGTH)
    cell = rnn_cell.OutputProjectionWrapper(rnn_cell.GRUCell(HIDDEN_SIZE), 256)
    decoding, _, sampling_decoding, _ = rnn_seq2seq(in_X, in_y, cell)
    return skflow.ops.sequence_classifier(decoding, out_y, sampling_decoding)

if __name__ == '__main__':
    import sys
    import io
    import os
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    vocab_processor = skflow.preprocessing.ByteProcessor(
        max_document_length=MAX_DOCUMENT_LENGTH)
    X_iter = ["some sentence", "some other sentence"]
    X_pred = ["some sentence", "some other sentence"]
    Y_iter = ["some sentence", "some other sentence"]

    x_iter = vocab_processor.transform(X_iter)
    y_iter = vocab_processor.transform(Y_iter)
    xpred = np.array(list(vocab_processor.transform(X_pred)))
    PATH = '/tmp/tf_examples/ntm/'
    
    if os.path.exists(PATH):
        translator = skflow.TensorFlowEstimator.restore(PATH)
    else:
        translator = skflow.TensorFlowEstimator(model_fn=translate_model,
            n_classes=256, continue_training=True)
    # print(zip(xpred, xpred_inp, predictions, text_outputs))
    translator.fit(x_iter, y_iter, logdir=PATH)
    # translator.save(PATH)
    
    predictions = translator.predict(xpred, axis=2)
    xpred_inp = vocab_processor.reverse(xpred)
    text_outputs = vocab_processor.reverse(predictions)
    try:
        for inp_data, input_text, pred, output_text in zip(xpred, xpred_inp, predictions, text_outputs):
            print(input_text, output_text)
            print(inp_data, pred)
    except Exception as e:
        print(e)
    