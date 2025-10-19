class LicitacoesController:
    def __init__(self, licitacoes):
        self.licitacoes = licitacoes

    def buscar_por_natureza(self, natureza):
        resultados = [licitacao for licitacao in self.licitacoes if licitacao.natureza == natureza]
        return resultados