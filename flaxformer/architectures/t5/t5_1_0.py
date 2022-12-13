# Copyright 2022 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""An implementation of t5_base version 1.0."""

import abc
import dataclasses
import functools
from jax import numpy as jnp

from flaxformer.architectures.t5 import t5_architecture
from flaxformer.architectures.t5 import t5_common_layers

DROPOUT_RATE = 0.0
ACTIVATIONS = ('relu',)
VOCAB_SIZE = 32128


@dataclasses.dataclass(frozen=True)
class Config(abc.ABC):
  """T5 configuration base dataclass."""
  # The size of the embeddings, hidden layers, and intermediates.
  embedding_dim: int
  mlp_dim: int
  head_dim: int

  # The total number of layers and the number of attention heads in each layer.
  num_heads: int
  num_encoder_layers: int
  num_decoder_layers: int


SMALL_CONFIG = Config(
    embedding_dim=512,
    head_dim=64,
    mlp_dim=2048,
    num_heads=8,
    num_encoder_layers=6,
    num_decoder_layers=6,
)

BASE_CONFIG = Config(
    embedding_dim=768,
    head_dim=64,
    mlp_dim=3072,
    num_heads=12,
    num_encoder_layers=12,
    num_decoder_layers=12,
)

LARGE_CONFIG = Config(
    embedding_dim=1024,
    head_dim=64,
    mlp_dim=4096,
    num_heads=16,
    num_encoder_layers=24,
    num_decoder_layers=24,
)

# Also known as T5-3B.
XL_CONFIG = Config(
    embedding_dim=1024,
    head_dim=128,
    mlp_dim=16384,
    num_heads=32,
    num_encoder_layers=24,
    num_decoder_layers=24,
)

# Also known as T5-11B.
XXL_CONFIG = Config(
    embedding_dim=1024,
    head_dim=128,
    mlp_dim=65536,
    num_heads=128,
    num_encoder_layers=24,
    num_decoder_layers=24,
)


def encoder_decoder(embedding_dim,
                    mlp_dim,
                    num_heads,
                    num_encoder_layers,
                    num_decoder_layers,
                    head_dim,
                    vocabulary_size=VOCAB_SIZE,
                    dropout_rate=DROPOUT_RATE,
                    activations=ACTIVATIONS,
                    dtype=jnp.bfloat16):
  """Create a T5-1.0 style encoder-decoder stack.

  Args:
    embedding_dim: The size of the embedding for this stack.
    mlp_dim: The dimension of the multilayer perceptron.
    num_heads: The number of attention heads.
    num_encoder_layers: The number of encoder layers to create.
    num_decoder_layers: The number of decoder layers to create.
    head_dim: The dimension of the attention head.
    vocabulary_size: The size of the embedding vocabulary.
    dropout_rate: The dropout rate. Set to 0.0 to turn off dropout.
    activations: The activations to use for the MLP.
    dtype: The dtype for all layers in this encoder-decoder.

  Returns:
    A T5-style encoder-decoder.
  """
  decoder_factory = functools.partial(
      t5_common_layers.decoder,
      num_heads=num_heads,
      head_dim=head_dim,
      mlp_dim=mlp_dim,
      num_layers=num_decoder_layers,
      dropout_rate=dropout_rate,
      activations=activations,
      dtype=dtype)
  encoder_factory = functools.partial(
      t5_common_layers.encoder,
      num_heads=num_heads,
      head_dim=head_dim,
      mlp_dim=mlp_dim,
      num_layers=num_encoder_layers,
      dropout_rate=dropout_rate,
      activations=activations,
      dtype=dtype)
  embedding_factory = functools.partial(
      t5_common_layers.embedding,
      vocabulary_size=vocabulary_size,
      embedding_dim=embedding_dim,
      dtype=dtype)

  return t5_architecture.EncoderDecoder(
      encoder_factory=encoder_factory,
      decoder_factory=decoder_factory,
      shared_token_embedder_factory=embedding_factory,
      dtype=dtype)  # pytype: disable=wrong-keyword-args
