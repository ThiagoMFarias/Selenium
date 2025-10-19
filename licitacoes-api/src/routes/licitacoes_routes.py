from flask import Blueprint, request, jsonify
from controllers.licitacoes_controller import LicitacoesController

licitacoes_bp = Blueprint('licitacoes', __name__)
licitacoes_controller = LicitacoesController()

@licitacoes_bp.route('/licitacoes', methods=['GET'])
def buscar_licitacoes():
    natureza = request.args.get('natureza')
    if natureza == 'material de consumo':
        licitacoes = licitacoes_controller.buscar_por_natureza(natureza)
        return jsonify(licitacoes), 200
    return jsonify({'error': 'Natureza da aquisição não encontrada'}), 400

def set_routes(app):
    app.register_blueprint(licitacoes_bp)