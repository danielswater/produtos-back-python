from flask import Flask, request, jsonify, render_template, send_from_directory
from datetime import datetime
import json
import sqlite3
from flask_cors import CORS
import os

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

    nome = request.form['nome']
    descricao = request.form['descricao']
    preco = request.form['preco']
    data_cadastro = datetime.now().strftime('%Y-%m-%d')
    data_validade = request.form['data_validade']
    imagem = request.files.get('imagem')
    if not imagem:
        filename = "no_image.png"
    else:
        upload_dir = os.path.join(app.root_path, './imagens')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}.jpg"
        filepath = os.path.join(upload_dir, filename)
        imagem.save(filepath)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO produtos (nome, descricao, preco, data_cadastro, data_validade, imagem) VALUES (?, ?, ?, ?, ?, ?)",(nome, descricao, preco, data_cadastro, data_validade, filename))
    rows = cursor.rowcount
    conn.commit()
    conn.close()

    if rows == 1:
        return jsonify({'status': 'sucesso', 'mensagem': 'Produto cadastrado com sucesso!'})
    else:
        return jsonify({'status': 'erro', 'mensagem': 'Ocorreu um erro ao cadastrar!'})

#ROTA PARA ATUALIZAR UM PRODUTO
#PERCEBE QUE AQUI NA ATUALIZAÇÃO E A MESMA COISA DO POST (INSERIR) SO VAI MUDAR O QUERY DO SQL
#VEJA TAMBEM QUE NA ROTA VAMOS PASSAR O ID DO PROTUDO
@app.route('/api/update-produtos/<int:id>', methods=['PUT'])
def update_produtos(id):
    nome = request.form['nome']
    descricao = request.form['descricao']
    preco = request.form['preco']
    data_cadastro = request.form['data_cadastro']
    data_validade = request.form['data_validade']
    imagem = request.files.get('imagem', None)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if imagem is None: 
        produto = get_produto_by_id(id)
        filename = produto['imagem']
    else:
        upload_dir = os.path.join(app.root_path, './imagens')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}.jpg"
        filepath = os.path.join(upload_dir, filename)
        imagem.save(filepath)
    cursor.execute("UPDATE produtos SET nome=?, descricao=?, preco=?, data_cadastro=?, data_validade=?, imagem=? WHERE id=?",(nome, descricao, preco, data_cadastro, data_validade, filename, id,))
    rows = cursor.rowcount
    conn.commit()
    conn.close()
    if rows == 1:
        return jsonify({'status': 'sucesso', 'mensagem': 'Produto atualizado com sucesso!'})
    else:
        return jsonify({'status': 'erro', 'mensagem': 'Ocorreu um erro ao atualizar o produto!'})


#ROTA PRA DELETAR UM PRODUTO, TAMBEM VAMOS PASSAR O ID DO PRODUTO
@app.route('/api/delete-produtos/<int:id>', methods=['DELETE'])
def delete_produtos(id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produtos WHERE id=?",(id))
    rows = cursor.rowcount
    conn.commit()
    conn.close()
    if rows == 1:
        return jsonify({'status': 'sucesso', 'mensagem': 'Produto deletado com sucesso'})
    else:
        return jsonify({'status': 'erro', 'mensagem': 'Ocorreu um erro ao deletar o produto'})

@app.route('/api/detalhe-produto/<int:id>', methods=['GET'])
def get_produto_by_id(id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE id=?",(id,))
    produto = cursor.fetchone()
    conn.close()
    if produto:
        # produto_dict = {'id': produto[0], 'nome': produto[1], 'preco': produto[2], 'data_cadastro': produto[3], 'data_vencimento': produto[4], 'imagem': produto[5]}
        produto_dict = {'id': produto[0], 'nome': produto[1], 'descricao': produto[2], 'preco': produto[3], 'data_cadastro': produto[4], 'data_validade': produto[5], 'imagem':produto[6]}
        return produto_dict
    else:
        return None

@app.route('/imagens/<path:path>')
def send_image(path):
    return send_from_directory(os.path.join(app.root_path, 'imagens'), path)

if __name__ == '__main__':
    app.run()
