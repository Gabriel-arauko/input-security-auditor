import subprocess
import winreg
import logging
from pathlib import Path
import json


def verificar_uac() -> dict:
    """
    Verifica no Registro do Windows se o Controle de Conta de Usuário (UAC)
    e o Secure Desktop estão ativos para proteger entradas de credenciais.
    """
    caminho_chave = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
    resultado = {
        "uac_ativo": False,
        "secure_desktop_ativo": False,
        "status": "RISCO"
    }

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, caminho_chave) as chave:
            enable_lua, _ = winreg.QueryValueEx(chave, "EnableLUA")
            prompt_secure, _ = winreg.QueryValueEx(chave, "PromptOnSecureDesktop")

            resultado["uac_ativo"] = (enable_lua == 1)
            resultado["secure_desktop_ativo"] = (prompt_secure == 1)

            if resultado["uac_ativo"] and resultado["secure_desktop_ativo"]:
                resultado["status"] = "SEGURO"
            elif resultado["uac_ativo"]:
                resultado["status"] = "PARCIAL"

        logging.info(f"Verificação de UAC concluída: {resultado['status']}")
    except Exception as erro:
        logging.error(f"Falha ao ler chaves do UAC no registro: {erro}")
        resultado["erro"] = str(erro)

    return resultado


def auditar_inicializacao_registro() -> list[dict]:
    """
    Lê as chaves Run do usuário atual (HKCU) para identificar programas
    configurados para iniciar automaticamente com o Windows.
    """
    caminho_run = r"Software\Microsoft\Windows\CurrentVersion\Run"
    entradas = []

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, caminho_run) as chave:
            total_valores = winreg.QueryInfoKey(chave)[1]
            for i in range(total_valores):
                nome, comando, _ = winreg.EnumValue(chave, i)
                entradas.append({
                    "nome": nome,
                    "comando": comando,
                    "origem": "HKCU\\...\\Run"
                })
        logging.info(f"Auditoria de inicialização encontrou {len(entradas)} entradas.")
    except Exception as erro:
        logging.error(f"Erro ao auditar chaves Run do registro: {erro}")

    return entradas


def listar_processos_ativos() -> list[str]:
    """
    Obtém a lista única de processos em execução no sistema usando tasklist.
    """
    try:
        saida = subprocess.check_output(
            ["tasklist", "/FO", "CSV", "/NH"],
            text=True,
            encoding="latin-1"
        )
        processos = set()
        for linha in saida.strip().splitlines():
            colunas = [col.strip('"') for col in linha.split('","')]
            if colunas and colunas[0]:
                processos.add(colunas[0])
        return sorted(processos)
    except Exception as erro:
        logging.error(f"Erro ao listar processos ativos: {erro}")
        return []


def comparar_com_baseline(processos_ativos: list[str], caminho_baseline: Path) -> dict:
    """
    Compara os processos em execução com uma baseline de processos conhecidos.
    Se a baseline não existir, cria uma automaticamente.
    """
    if not caminho_baseline.exists():
        caminho_baseline.parent.mkdir(parents=True, exist_ok=True)
        caminho_baseline.write_text(
            json.dumps({"processos_aprovados": processos_ativos}, indent=4, ensure_ascii=False),
            encoding="utf-8"
        )
        logging.info("Baseline inicial de processos criada.")
        return {
            "primeira_execucao": True,
            "novos_processos": []
        }

    dados = json.loads(caminho_baseline.read_text(encoding="utf-8"))
    aprovados = set(dados.get("processos_aprovados", []))
    novos = [p for p in processos_ativos if p not in aprovados]

    if novos:
        logging.warning(f"Processos fora da baseline detectados: {novos}")
    else:
        logging.info("Nenhum processo desconhecido detectado em relação à baseline.")

    return {
        "primeira_execucao": False,
        "novos_processos": novos
    }