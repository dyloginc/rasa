from typing import Any, List, Text

from rasa.nlu.config import RasaNLUModelConfig
from rasa.nlu.tokenizers.tokenizer import Token, Tokenizer
from rasa.nlu.training_data import Message, TrainingData

from rasa.nlu.constants import (
    MESSAGE_TEXT_ATTRIBUTE,
    MESSAGE_TOKENS_NAMES,
    MESSAGE_ATTRIBUTES,
)


class MitieTokenizer(Tokenizer):

    provides = [MESSAGE_TOKENS_NAMES[attribute] for attribute in MESSAGE_ATTRIBUTES]

    defaults = {
        # add __CLS__ token to the end of the list of tokens
        "use_cls_token": True
    }

    @classmethod
    def required_packages(cls) -> List[Text]:
        return ["mitie"]

    def train(
        self, training_data: TrainingData, config: RasaNLUModelConfig, **kwargs: Any
    ) -> None:

        for example in training_data.training_examples:

            for attribute in MESSAGE_ATTRIBUTES:

                if example.get(attribute) is not None:
                    example.set(
                        MESSAGE_TOKENS_NAMES[attribute],
                        self.tokenize(example.get(attribute), attribute),
                    )

    def process(self, message: Message, **kwargs: Any) -> None:

        message.set(
            MESSAGE_TOKENS_NAMES[MESSAGE_TEXT_ATTRIBUTE], self.tokenize(message.text)
        )

    def _token_from_offset(
        self, text: Text, offset: int, encoded_sentence: bytes
    ) -> Token:
        return Token(
            text.decode("utf-8"), self._byte_to_char_offset(encoded_sentence, offset)
        )

    def tokenize(
        self, text: Text, attribute: Text = MESSAGE_TEXT_ATTRIBUTE
    ) -> List[Token]:
        import mitie

        encoded_sentence = text.encode("utf-8")
        tokenized = mitie.tokenize_with_offsets(encoded_sentence)
        tokens = [
            self._token_from_offset(token, offset, encoded_sentence)
            for token, offset in tokenized
        ]

        self.add_cls_token(tokens, attribute)

        return tokens

    @staticmethod
    def _byte_to_char_offset(text: bytes, byte_offset: int) -> int:
        return len(text[:byte_offset].decode("utf-8"))
