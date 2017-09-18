import tensorflow as tf
from .base_model import Base_Model
from . import config


class Vanilla_GRU(Base_Model):
  '''
  Model that uses vanilla GRUs for encoding sequences
  '''

  def __init__(self, sess, config, model_name="vanilla_gru.model"):
    Base_Model.__init__(self, sess, config)
    self.model_name = model_name

  def build_model(self, local_batch_size=config.BATCH_SIZE):
    assert(self.x.shape == (local_batch_size, config.NUMBERS['flows'], config.NUMBERS['packets'], config.NUMBERS['packet_features']))
    assert(self.target.shape == (local_batch_size, 2))

    # Packets encoder
    packets_encoder_config = {
        'n_seqs': local_batch_size * config.NUMBERS['flows'],
        'seq_len': config.NUMBERS['packets'],
        'n_features': config.NUMBERS['packet_features'],
        'n_gru_hidden': config.HIDDEN['packets_gru'],
        'n_dense_hidden': config.NUMBERS['flow_features']
    }
    packet_x = tf.reshape(self.x, (packets_encoder_config['n_seqs'], packets_encoder_config['seq_len'], packets_encoder_config['n_features']))
    encoded_flows_flat = self._encoder_layer(packet_x, "packets_encoder", packets_encoder_config)
    encoded_flows = tf.reshape(encoded_flows_flat, (local_batch_size, config.NUMBERS['flows'], config.NUMBERS['flow_features']))

    # Flow encoders
    flows_encoder_config = {
        'n_seqs': local_batch_size,
        'seq_len': config.NUMBERS['flows'],
        'n_features': config.NUMBERS['flow_features'],
        'n_gru_hidden': config.HIDDEN['flows_gru'],
        'n_dense_hidden': config.NUMBERS['ip_features']
    }
    encoded_ips = self._encoder_layer(encoded_flows, "flows_encoder", flows_encoder_config)

    # Get predictions
    predictor_config = {
        'n_batches': local_batch_size,
        'n_input': config.NUMBERS['ip_features'],
        'n_classes': 2
    }
    self.prediction = self._prediction_layer(encoded_ips, 'predictor', predictor_config)

    # Get loss and optimizer
    self.loss, self.optim, self.acc = self._define_optimization_vars(self.target, self.prediction, config.LOSS_WEIGHTING)

    self.summary_op = self._summaries()

    return self

