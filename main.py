from flask import Flask, request, jsonify, render_template
from datetime import datetime
import json
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
app.config['DEBUG'] = True
CORS(app)

#AQUI, DEFINE O CAMINHO P O BANCO DE DADOS
DB_PATH = './produtos.db'

#AQUI VAI CRIAR A TABELA PRODUTOS NO BANCO
def create_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS produtos
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        descricao TEXT,
        preco REAL NOT NULL,
        data_cadastro DATE NOT NULL,
        data_validade DATE NOT NULL)''')
    conn.commit()
    conn.close()

create_table()

#CRIA A ROTA P A APLICAÇÃO (E O QUE A GENTE USA NO FRONT P FAZER AS CHAMADAS, AS FAMOSAS APIS)
#ESSA PRIMEIRA ROTA, REDIRECIONA P A PAGINA INICIAL, OU SEJA O INDEX.HTML
@app.route('/', methods=['GET'])
def index():
    # conn = sqlite3.connect(DB_PATH)
    # cursor = conn.cursor()
    # cursor.execute("DELETE FROM produtos;")
    # conn.commit()
    # conn.close()
    return render_template('index.html')

#ESSA ROTA TRAZ TODOS OS PRODUTOS CADASTRADOS
@app.route('/api/produtos', methods=['GET'])
def get_produtos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM produtos')
    rows = cursor.fetchall()

    produtos = []
    columns = [col[0] for col in cursor.description]
    for row in rows:
        produto = {}
        for i, column in enumerate(columns):
            produto[column] = row[i]
        produtos.append(produto)
    conn.close()
    if len(produtos) == 0:
        return jsonify({'status': 'erro', 'mensagem': 'Nenhum produto cadastrado'})
    else:
        return jsonify(produtos)

#AQUI NESSA ROTA, VAI CADASTRAR UM PRODUTO
@app.route('/api/add-produtos', methods=['POST'])
def add_produtos():

    if request.content_type != 'multipart/form-data':
        return jsonify({'status': 'erro', 'mensagem': 'Ocorreu um erro'})
    nome = request.form['nome']
    descricao = request.form['descricao']
    preco = request.form['preco']
    data_cadastro = datetime.now().strftime('%Y-%m-%d')
    data_validade = request.form['data_validade']

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO produtos (nome, descricao, preco, data_cadastro, data_validade) VALUES (?, ?, ?, ?, ?)",(nome, descricao, preco, data_cadastro, data_validade))
    conn.commit()
    conn.close()
    return jsonify({'status': 'sucesso', 'mensagem': 'Produto cadastrado com sucesso!'})

#ROTA PARA ATUALIZAR UM PRODUTO
#PERCEBE QUE AQUI NA ATUALIZAÇÃO E A MESMA COISA DO POST (INSERIR) SO VAI MUDAR O QUERY DO SQL
#VEJA TAMBEM QUE NA ROTA VAMOS PASSAR O ID DO PROTUDO
@app.route('/api/update-produtos/<int:id>', methods=['PUT'])
def update_produtos(id):
    data = request.get_json()
    nome = data['nome']
    descricao = data['descricao']
    preco = data['preco']
    data_cadastro = data['data_cadastro']
    data_validade = data['data_validade']
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE produtos SET nome=?, descricao=?, preco=?, data_cadastro=?, data_validade=? WHERE id=?",(nome, descricao, preco, data_cadastro, data_validade, id))
    conn.commit()
    conn.close()
    return jsonify({'status': 'sucesso', 'mensagem': 'Produto atualizado com sucesso!'})

#ROTA PRA DELETAR UM PRODUTO, TAMBEM VAMOS PASSAR O ID DO PRODUTO
@app.route('/api/delete-produtos/<int:id>', methods=['DELETE'])
def delete_produtos(id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produtos WHERE id=?",(id))
    conn.commit()
    conn.close()
    return jsonify({'status': 'sucesso', 'mensagem': 'Produto deletado com sucesso'})

@app.route('/api/detalhe-produto/<int:id>', methods=['GET'])
def get_produto_by_id(id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE id=?",(id))
    produto = cursor.fetchone()
    conn.close()
    if produto:
        return jsonify(dict(produto))
    else:
        return jsonify({'status': 'erro', 'mensagem': 'Produto não encontrado'})

if __name__ == '__main__':
    app.run()
