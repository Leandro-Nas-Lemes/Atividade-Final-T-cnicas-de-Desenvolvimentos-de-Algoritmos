#!/usr/bin/env python3
"""
Gerenciador de Tarefas
Implementa os requisitos da Atividade Final:
- Menu com opções (criar, atualizar, concluir, excluir, relatórios, sair)
- Persistência em tarefas.json e tarefas_arquivadas.json
- Arquivamento automático de tarefas concluídas há mais de 7 dias
- Exclusão lógica (status = "Excluída")
- Cada função tem docstring e um print inicial para debug
- Validações e tratamento de exceções
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

tarefas: List[Dict] = []
ARQUIVO_TAREFAS = "tarefas.json"
ARQUIVO_TAREFAS_ARQUIVADAS = "tarefas_arquivadas.json"
next_id: int = 1  # será recalculado ao carregar os dados

PRIORIDADES = ["Urgente", "Alta", "Média", "Baixa"]
STATUS_VALIDOS = ["Pendente", "Fazendo", "Concluída", "Arquivado", "Excluída"]
ORIGENS = ["E-mail", "Telefone", "Chamado do Sistema"]

def inicializar_arquivos():
    """
    Garante que os arquivos JSON existam; se não, cria com lista vazia.
    Também carrega dados para a variável global tarefas e ajusta next_id.
    Parâmetros: nenhum
    Retorno: nenhum
    """
    print("Executando a função inicializar_arquivos")
    global tarefas, next_id
    # Criar arquivos se não existirem
    for nome in (ARQUIVO_TAREFAS, ARQUIVO_TAREFAS_ARQUIVADAS):
        if not os.path.exists(nome):
            with open(nome, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    with open(ARQUIVO_TAREFAS, "r", encoding="utf-8") as f:
        try:
            tarefas = json.load(f)
        except json.JSONDecodeError:
            tarefas = []
            
    max_id = 0
    for t in tarefas:
        try:
            if isinstance(t.get("id"), int) and t["id"] > max_id:
                max_id = t["id"]
        except Exception:
            continue
    next_id = max_id + 1

def salvar_tarefas():
    """
    Salva a lista global de tarefas no arquivo tarefas.json.
    Parâmetros: nenhum
    Retorno: nenhum
    """
    print("Executando a função salvar_tarefas")
    with open(ARQUIVO_TAREFAS, "w", encoding="utf-8") as f:
        json.dump(tarefas, f, ensure_ascii=False, indent=2, default=str)

def anexar_arquivo_arquivadas(tarefa: Dict):
    """
    Adiciona uma tarefa ao arquivo tarefas_arquivadas.json (acumula histórico).
    Parâmetros:
        tarefa: dict com os dados da tarefa a anexar
    Retorno: nenhum
    """
    print("Executando a função anexar_arquivo_arquivadas")
    try:
        with open(ARQUIVO_TAREFAS_ARQUIVADAS, "r+", encoding="utf-8") as f:
            try:
                dados = json.load(f)
            except json.JSONDecodeError:
                dados = []
            dados.append(tarefa)
            f.seek(0)
            json.dump(dados, f, ensure_ascii=False, indent=2, default=str)
            f.truncate()
    except FileNotFoundError:
        with open(ARQUIVO_TAREFAS_ARQUIVADAS, "w", encoding="utf-8") as f:
            json.dump([tarefa], f, ensure_ascii=False, indent=2, default=str)

def validar_prioridade(prio: str) -> bool:
    """
    Valida se a prioridade informada está entre as permitidas.
    Parâmetros:
        prio: string informada pelo usuário
    Retorno: True se válida, False caso contrário
    """
    print("Executando a função validar_prioridade")
    return prio.capitalize() in [p.capitalize() for p in PRIORIDADES]

def validar_origem(orig: str) -> bool:
    """
    Valida se a origem informada está entre as permitidas.
    """
    print("Executando a função validar_origem")
    return any(orig.lower() == o.lower() for o in ORIGENS)

def buscar_tarefa_por_id(tid: int) -> Optional[Dict]:
    """
    Retorna a tarefa com o ID informado ou None se não existir.
    """
    print("Executando a função buscar_tarefa_por_id")
    for t in tarefas:
        if t.get("id") == tid:
            return t
    return None

def input_com_tratamento(prompt: str) -> str:
    """
    Wrapper para input, com strip e tratamento básico.
    """
    return input(prompt).strip()

def criar_tarefa():
    """
    Cria uma nova tarefa solicitando informações ao usuário,
    valida os dados e adiciona a tarefa à lista global de tarefas.
    Parâmetros: nenhum
    Retorno: nenhum
    """
    print("Executando a função criar_tarefa")
    global next_id, tarefas
    titulo = input_com_tratamento("Título (obrigatório): ")
    while not titulo:
        print("Título é obrigatório.")
        titulo = input_com_tratamento("Título (obrigatório): ")

    descricao = input_com_tratamento("Descrição (opcional): ")

    print("Prioridades disponíveis:", ", ".join(PRIORIDADES))
    prioridade = input_com_tratamento("Prioridade (obrigatório): ")
    while not validar_prioridade(prioridade):
        print("Prioridade inválida. Escolha entre:", ", ".join(PRIORIDADES))
        prioridade = input_com_tratamento("Prioridade (obrigatório): ")
    prioridade = prioridade.capitalize()

    print("Origens possíveis:", ", ".join(ORIGENS))
    origem = input_com_tratamento("Origem da Tarefa (obrigatório): ")
    while not validar_origem(origem):
        print("Origem inválida. Escolha entre:", ", ".join(ORIGENS))
        origem = input_com_tratamento("Origem da Tarefa (obrigatório): ")

    origem = next(o for o in ORIGENS if o.lower() == origem.lower())

    data_criacao = datetime.now().isoformat()
    tarefa = {
        "id": next_id,
        "titulo": titulo,
        "descricao": descricao,
        "prioridade": prioridade,
        "status": "Pendente",
        "origem": origem,
        "data_criacao": data_criacao
    }
    tarefas.append(tarefa)
    next_id += 1
    print(f"Tarefa criada com ID {tarefa['id']}.")

def verificar_urgencia_e_pegar():
    """
    Verifica se há tarefas com prioridade máxima (Urgente). Se houver,
    retorna a primeira tarefa dessa prioridade; caso contrário, busca a
    primeira da próxima prioridade disponível. Atualiza status para "Fazendo".
    Parâmetros: nenhum
    Retorno: None (exibe a tarefa selecionada)
    """
    print("Executando a função verificar_urgencia_e_pegar")
    pendentes = [t for t in tarefas if t.get("status") == "Pendente"]
    if not pendentes:
        print("Não há tarefas pendentes.")
        return

    for prio in PRIORIDADES: 
        for t in pendentes:
            if t.get("prioridade", "").lower() == prio.lower():
                t["status"] = "Fazendo"
                print("Tarefa selecionada para execução:")
                imprimir_tarefa(t)
                return
    t = pendentes[0]
    t["status"] = "Fazendo"
    print("Tarefa selecionada (fallback):")
    imprimir_tarefa(t)

def atualizar_prioridade():
    """
    Altera a prioridade de uma tarefa existente após validação.
    Parâmetros: nenhum
    Retorno: nenhum
    """
    print("Executando a função atualizar_prioridade")
    try:
        tid = int(input_com_tratamento("Informe o ID da tarefa a alterar prioridade: "))
    except ValueError:
        print("ID inválido. Operação cancelada.")
        return
    t = buscar_tarefa_por_id(tid)
    if not t:
        print("Tarefa não encontrada.")
        return
    print("Prioridades válidas:", ", ".join(PRIORIDADES))
    nova = input_com_tratamento("Nova prioridade: ")
    if not validar_prioridade(nova):
        print("Prioridade inválida. Operação cancelada.")
        return
    t["prioridade"] = nova.capitalize()
    print("Prioridade atualizada com sucesso.")

def concluir_tarefa():
    """
    Marca uma tarefa como concluída, adiciona data_conclusao e atualiza status.
    Parâmetros: nenhum
    Retorno: nenhum
    """
    print("Executando a função concluir_tarefa")
    try:
        tid = int(input_com_tratamento("Informe o ID da tarefa a concluir: "))
    except ValueError:
        print("ID inválido. Operação cancelada.")
        return
    t = buscar_tarefa_por_id(tid)
    if not t:
        print("Tarefa não encontrada.")
        return
    if t.get("status") == "Concluída":
        print("Tarefa já está concluída.")
        return
    t["status"] = "Concluída"
    t["data_conclusao"] = datetime.now().isoformat()
    print("Tarefa marcada como Concluída.")

def arquivar_tarefas_antigas():
    """
    Para tarefas com status 'Concluída' e data_conclusao há mais de 7 dias,
    atualiza o status para 'Arquivado' e registra no arquivo de arquivadas.
    Parâmetros: nenhum
    Retorno: nenhum
    """
    print("Executando a função arquivar_tarefas_antigas")
    agora = datetime.now()
    sete_dias = timedelta(days=7)
    for t in tarefas:
        if t.get("status") == "Concluída" and t.get("data_conclusao"):
            try:
                data_conc = datetime.fromisoformat(t["data_conclusao"])
            except Exception:
                continue
            if agora - data_conc > sete_dias:
                t["status"] = "Arquivado"
                anexar_arquivo_arquivadas(t.copy())
                print(f"Tarefa ID {t['id']} arquivada automaticamente.")

def exclusao_logica():
    """
    Marca uma tarefa como 'Excluída' (não a remove da lista).
    Parâmetros: nenhum
    Retorno: nenhum
    """
    print("Executando a função exclusao_logica")
    try:
        tid = int(input_com_tratamento("Informe o ID da tarefa a excluir: "))
    except ValueError:
        print("ID inválido. Operação cancelada.")
        return
    t = buscar_tarefa_por_id(tid)
    if not t:
        print("Tarefa não encontrada.")
        return
    t["status"] = "Excluída"
    print("Tarefa marcada como Excluída (exclusão lógica).")

def imprimir_tarefa(t: Dict):
    """
    Exibe todas as informações de uma tarefa e, se concluída, calcula tempo de execução.
    Parâmetros:
        t: dict (tarefa)
    Retorno: nenhum
    """
    print("Executando a função imprimir_tarefa")
    print("=" * 40)
    print(f"ID: {t.get('id')}")
    print(f"Título: {t.get('titulo')}")
    print(f"Descrição: {t.get('descricao')}")
    print(f"Prioridade: {t.get('prioridade')}")
    print(f"Status: {t.get('status')}")
    print(f"Origem: {t.get('origem')}")
    print(f"Data criação: {t.get('data_criacao')}")
    if t.get("data_conclusao"):
        print(f"Data conclusão: {t.get('data_conclusao')}")
        try:
            inicio = datetime.fromisoformat(t["data_criacao"])
            fim = datetime.fromisoformat(t["data_conclusao"])
            dur = fim - inicio
            print(f"Tempo de execução: {dur}")
        except Exception:
            print("Não foi possível calcular o tempo de execução.")
    print("=" * 40)

def relatorio_todas():
    """
    Exibe todas as tarefas e suas informações (inclui excluídas e arquivadas).
    Parâmetros: nenhum
    Retorno: nenhum
    """
    print("Executando a função relatorio_todas")
    if not tarefas:
        print("Nenhuma tarefa cadastrada.")
        return
    for t in tarefas:
        imprimir_tarefa(t)

def relatorio_arquivados():
    """
    Exibe a lista de tarefas arquivadas (status == 'Arquivado').
    Tarefas com status 'Excluída' não devem aparecer aqui.
    Parâmetros: nenhum
    Retorno: nenhum
    """
    print("Executando a função relatorio_arquivados")
    arquivadas = [t for t in tarefas if t.get("status") == "Arquivado"]
    if not arquivadas:
        print("Nenhuma tarefa arquivada na lista ativa.")
        return
    for t in arquivadas:
        imprimir_tarefa(t)
def mostrar_menu():
    """
    Mostra as opções do menu principal.
    """
    print("Executando a função mostrar_menu")
    print("\n--- Gerenciador de Tarefas ---")
    print("1 - Criar tarefa")
    print("2 - Verificar urgência e pegar tarefa")
    print("3 - Atualizar prioridade")
    print("4 - Concluir tarefa")
    print("5 - Arquivar tarefas antigas (rodar manualmente)")
    print("6 - Excluir tarefa (lógica)")
    print("7 - Relatório (todas)")
    print("8 - Relatório (arquivadas)")
    print("9 - Sair (salva e encerra)")
    print("-------------------------------")

def menu_principal():
    """
    Controla o fluxo principal do programa: exibe menu, valida opção e chama funções.
    """
    print("Executando a função menu_principal")
    inicializar_arquivos()
    while True:
        arquivar_tarefas_antigas()
        mostrar_menu()
        opc = input_com_tratamento("Escolha uma opção: ")
        try:
            opc_num = int(opc)
        except ValueError:
            print("Opção inválida. Informe um número correspondente ao menu.")
            continue

        if opc_num == 1:
            criar_tarefa()
        elif opc_num == 2:
            verificar_urgencia_e_pegar()
        elif opc_num == 3:
            atualizar_prioridade()
        elif opc_num == 4:
            concluir_tarefa()
        elif opc_num == 5:
            arquivar_tarefas_antigas()
        elif opc_num == 6:
            exclusao_logica()
        elif opc_num == 7:
            relatorio_todas()
        elif opc_num == 8:
            relatorio_arquivados()
        elif opc_num == 9:
            salvar_tarefas()
            print("Dados salvos em", ARQUIVO_TAREFAS)
            print("Encerrando o programa.")
            exit()
        else:
            print("Opção não existe. Escolha uma das opções do menu.")

if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        salvar_tarefas()
        print("\nPrograma encerrado pelo usuário. Dados salvos.")
        exit()
