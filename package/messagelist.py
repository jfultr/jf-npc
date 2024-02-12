class MessageList(list):
    def __init__(self, id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # override
    def append(self, item):
        super().append(item)
    
    # override
    def extend(self, item):
        super().extend(item)