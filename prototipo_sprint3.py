# Sprint 3 - Sistema de Monitoramento de Consumo Energético e Sustentabilidade
# Protótipo Funcional: Estação de Recarga de VE integrada a Energia Solar com Automação
# Equipe: André Debiazzi, 
#	  Lucas Barros,
#         Renan Eskildssen, 
#         Kaique da Silva Assis,
#         Vinicius Cristal de Oliveira



# 1. CONSUMO DOS EQUIPAMENTOS


potencia_celular_watts = 10
potencia_secador_watts = 1800
potencia_chuveiro_watts = 5500
potencia_carro_watts = 7000

tempo_minutos_celular = float(input("Tempo de uso do celular em carregamento (minutos): "))
tempo_minutos_secador = float(input("Tempo de uso do secador de cabelo (minutos): "))
tempo_minutos_banho = float(input("Tempo de banho com o chuveiro elétrico (minutos): "))
tempo_horas_carro = float(input("Tempo de recarga do carro elétrico sem automação (horas): "))

consumo_celular = (potencia_celular_watts / 1000) * (tempo_minutos_celular / 60)
consumo_secador = (potencia_secador_watts / 1000) * (tempo_minutos_secador / 60)
consumo_banho = (potencia_chuveiro_watts / 1000) * (tempo_minutos_banho / 60)
consumo_carro_sem_automacao = (potencia_carro_watts / 1000) * tempo_horas_carro

consumo_total = consumo_celular + consumo_secador + consumo_banho + consumo_carro_sem_automacao

print("\n=== Consumo doméstico (base Sprint 2) ===")
print("Celular:", round(consumo_celular, 3), "kWh")
print("Secador:", round(consumo_secador, 3), "kWh")
print("Chuveiro:", round(consumo_banho, 3), "kWh")
print("Carro elétrico (recarga comum, sem automação):", round(consumo_carro_sem_automacao, 3), "kWh")
print("Consumo total:", round(consumo_total, 3), "kWh")


# 2. GERAÇÃO SOLAR SIMULADA (energia renovável - novo componente)
# Valores simulados de geração (kWh) de um painel solar de 5 kWp, hora a hora,
# representando um dia típico: sem geração à noite, subindo pela manhã, pico
# por volta do meio-dia e caindo ao entardecer.

geracao_solar_por_hora = [
    0, 0, 0, 0, 0, 0,               # 0h às 5h - sem sol
    0.8, 1.8, 2.9, 3.8, 4.5, 4.9,   # 6h às 11h - sol nascendo
    5.0, 4.8, 4.3, 3.6, 2.7, 1.7,   # 12h às 17h - pico e queda
    0.6, 0, 0, 0, 0, 0              # 18h às 23h - sem sol
]


# 3. BATERIA DE ARMAZENAMENTO

capacidade_bateria_kwh = 10
bateria_atual_kwh = 3   # começa parcialmente carregada


# 4. AUTOMAÇÃO DA RECARGA DO VEÍCULO ELÉTRICO
# Regras do controlador de automação:
#   1) Se há geração solar suficiente -> recarga em potência máxima com solar
#   2) Se não, mas a bateria está acima de 30% -> recarga reduzida com bateria
#   3) Caso contrário -> recarga em modo econômico usando a rede elétrica
# O excedente de energia solar não usado na recarga é guardado na bateria.

potencia_max_recarga_kw = 7
limiar_solar_kw = 2
limiar_bateria_percentual = 30

hora_conecta_veiculo = 8
hora_desconecta_veiculo = 18

horas = []
solar_registrado = []
bateria_percentual_registrado = []
fonte_registrada = []
ve_kwh_registrado = []
comando_registrado = []

for hora in range(24):
    geracao_solar = geracao_solar_por_hora[hora]
    veiculo_conectado = hora_conecta_veiculo <= hora < hora_desconecta_veiculo

    fonte = "-"
    ve_kwh = 0
    comando = "Nenhum veículo conectado"

    if veiculo_conectado:
        if geracao_solar >= limiar_solar_kw:
            # Regra 1: recarga em potência máxima usando energia solar
            ve_kwh = min(potencia_max_recarga_kw, geracao_solar)
            excedente = geracao_solar - ve_kwh
            if excedente > 0:
                espaco_livre = capacidade_bateria_kwh - bateria_atual_kwh
                armazenado = min(excedente, espaco_livre)
                bateria_atual_kwh = bateria_atual_kwh + armazenado
            fonte = "Solar"
            comando = "Recarga em potência máxima (energia solar disponível)"
        else:
            bateria_percentual = (bateria_atual_kwh / capacidade_bateria_kwh) * 100
            if bateria_percentual > limiar_bateria_percentual:
                # Regra 2: completa com a bateria, em potência reduzida
                if geracao_solar > 0:
                    espaco_livre = capacidade_bateria_kwh - bateria_atual_kwh
                    armazenado = min(geracao_solar, espaco_livre)
                    bateria_atual_kwh = bateria_atual_kwh + armazenado
                ve_kwh = min(potencia_max_recarga_kw * 0.5, bateria_atual_kwh)
                bateria_atual_kwh = bateria_atual_kwh - ve_kwh
                fonte = "Bateria"
                comando = "Recarga reduzida usando energia armazenada na bateria"
            else:
                # Regra 3: usa a rede, em modo econômico
                if geracao_solar > 0:
                    espaco_livre = capacidade_bateria_kwh - bateria_atual_kwh
                    armazenado = min(geracao_solar, espaco_livre)
                    bateria_atual_kwh = bateria_atual_kwh + armazenado
                ve_kwh = potencia_max_recarga_kw * 0.3
                fonte = "Rede"
                comando = "Recarga em modo econômico (bateria baixa, sem sol)"
    else:
        # veículo não conectado: energia solar gerada vai só para a bateria
        if geracao_solar > 0:
            espaco_livre = capacidade_bateria_kwh - bateria_atual_kwh
            armazenado = min(geracao_solar, espaco_livre)
            bateria_atual_kwh = bateria_atual_kwh + armazenado

    bateria_percentual_atual = round((bateria_atual_kwh / capacidade_bateria_kwh) * 100, 1)

    horas.append(hora)
    solar_registrado.append(round(geracao_solar, 2))
    bateria_percentual_registrado.append(bateria_percentual_atual)
    fonte_registrada.append(fonte)
    ve_kwh_registrado.append(round(ve_kwh, 2))
    comando_registrado.append(comando)


# 5. REGISTRO E RELATÓRIO DA SESSÃO (coleta e exibição dos dados)

print("\n=== RELATÓRIO DA SESSÃO DE RECARGA (24h simuladas) ===")
print("Hora | Solar(kWh) | Bateria(%) | Fonte VE | VE(kWh) | Comando automático")
for i in range(24):
    print(
        horas[i], "|",
        solar_registrado[i], "|",
        bateria_percentual_registrado[i], "|",
        fonte_registrada[i], "|",
        ve_kwh_registrado[i], "|",
        comando_registrado[i]
    )

total_solar_gerado = round(sum(solar_registrado), 2)
total_ve = round(sum(ve_kwh_registrado), 2)

total_solar_usado_ve = 0
total_bateria_usado_ve = 0
total_rede_usado_ve = 0
for i in range(24):
    if fonte_registrada[i] == "Solar":
        total_solar_usado_ve = total_solar_usado_ve + ve_kwh_registrado[i]
    elif fonte_registrada[i] == "Bateria":
        total_bateria_usado_ve = total_bateria_usado_ve + ve_kwh_registrado[i]
    elif fonte_registrada[i] == "Rede":
        total_rede_usado_ve = total_rede_usado_ve + ve_kwh_registrado[i]

print("\nResumo:")
print("Energia solar gerada no dia:", total_solar_gerado, "kWh")
print("Energia total entregue ao veículo elétrico:", total_ve, "kWh")
print("  - Vinda do solar:", round(total_solar_usado_ve, 2), "kWh")
print("  - Vinda da bateria:", round(total_bateria_usado_ve, 2), "kWh")
print("  - Vinda da rede:", round(total_rede_usado_ve, 2), "kWh")

if total_ve > 0:
    percentual_energia_limpa = round((total_solar_usado_ve / total_ve) * 100, 1)
else:
    percentual_energia_limpa = 0

print("Percentual da recarga proveniente de energia renovável (solar):", percentual_energia_limpa, "%")
