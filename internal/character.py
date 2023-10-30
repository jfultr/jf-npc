class Character:
    def __init__(self, name: str, 
                 role: str, 
                 background: str) -> None:
        super().__init__()
        self.name = name
        self.role = role.lower()
        self.background = f'{name} является {role}. ' + background


