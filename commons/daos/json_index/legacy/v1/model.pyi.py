"""
CODEC INTERNAL STATE

Codec = Codec(
    Recruiter: CodecModel(
        encoder: '...',
        decoder: '...',
        keys: {
            'age': CodecModelKey(int, ...),
            'name': CodecModelKey(str, ...),
            'dog': CodecModelKey(Dog, encoder=Codec[Dog].encoder, ...),
            'dogs': CodecModelIterKey(
                type = list
                child_type = CodecModelKey(type=Dog,encoder=Codec[Dog].encoder, ...)
                encoder = Encoder
            )
            'map': CodecModelDictKey(
                type = dict
                encode=lambda o: {k:v for k,v, in self.items()}
                keys = {
                    'yes': CodecModelKey(),
                    'no': CodecModelKey()
                }
            )
        }
    ),
    Dog: CodecModel(
        encoder: '...',
        decoder: '...',
        keys: {...}
    ),
    list: CodecModel(
        encoder: lambda prev_key, model: ...,
        decoder: lambda prev_key, obj: ...,
    ),
    dict: CodecModel(
        encoder: ...
    )
)
"""
