class Licitacao:
    def __init__(self, id, titulo, descricao, natureza):
        self.id = id
        self.titulo = titulo
        self.descricao = descricao
        self.natureza = natureza

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "natureza": self.natureza
        }