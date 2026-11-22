import json
import logging
from datetime import datetime
from pathlib import Path
from auditor import (
    verificar_uac,
    auditar_inicializacao_registro,
    listar_processos_ativos,
    comparar_com_baseline,
)


def configurar_ambiente():
    Path("logs").mkdir(exist_ok=True)
    Path("reports").mkdir(exist_ok=True)
    Path("baseline").mkdir(exist_ok=True)

    logging.basicConfig(
        filename="logs/auditoria.log",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def executar_auditoria():
    configurar_ambiente()
    print("=== Iniciando Auditoria Defensiva de Segurança de Entrada ===\n")

    caminho_baseline = Path("baseline/processos_conhecidos.json")
    caminho_relatorio = Path("reports/relatorio_seguranca.json")

    status_uac = verificar_uac()
    entradas_startup = auditar_inicializacao_registro()
    processos = listar_processos_ativos()
    analise_processos = comparar_com_baseline(processos, caminho_baseline)

    relatorio = {
        "data_auditoria": datetime.now().isoformat(),
        "protecao_sistema": status_uac,
        "persistencia_inicializacao": {
            "total_entradas": len(entradas_startup),
            "itens": entradas_startup,
        },
        "monitoramento_processos": {
            "total_ativos": len(processos),
            "primeira_execucao": analise_processos["primeira_execucao"],
            "novos_processos_detectados": analise_processos["novos_processos"],
        },
    }

    caminho_relatorio.write_text(
        json.dumps(relatorio, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"[1] Status UAC / Secure Desktop: {status_uac['status']}")
    print(f"[2] Programas na inicialização (HKCU Run): {len(entradas_startup)}")
    print(f"[3] Total de processos ativos analisados: {len(processos)}")

    if analise_processos["primeira_execucao"]:
        print("[*] Baseline de processos criada em: baseline/processos_conhecidos.json")
    elif analise_processos["novos_processos"]:
        print(f"[!] ALERTA: {len(analise_processos['novos_processos'])} novo(s) processo(s) fora da baseline:")
        for proc in analise_processos["novos_processos"]:
            print(f"    - {proc}")
    else:
        print("[OK] Nenhum processo novo fora da baseline.")

    print(f"\nRelatório completo salvo em: {caminho_relatorio}")


if __name__ == "__main__":
    executar_auditoria()