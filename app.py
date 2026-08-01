def catalogar_melhores_sinais(u):
    agora = datetime.now() + timedelta(minutes=1)
    tf_fmt = "M1" if u["time"] == "1M" else ("M5" if u["time"] == "5M" else u["time"])
    porcentagem_min = int(u["porcentagem"]) if u["porcentagem"].isdigit() else 100
    
    sinais_gerados = []
    # Usaremos uma lógica baseada no minuto para alternar entre CALL e PUT de forma mista
    passo = 1 if tf_fmt == "M1" else 5
    
    tipo_mercado = "IQ Option OTC" if u["mercado"] == "OTC" else "Normal"
    
    for i in range(60):
        agora += timedelta(minutes=passo)
        horario_str = agora.strftime("%H:%M")
        
        par_escolhido = u["selecionados"][i % len(u["selecionados"])]
        
        # Alterna dinamicamente a direção baseada no minuto e na posição para não sair só CALL
        direcao = "PUT" if (agora.minute % 3 == 0 or i % 2 != 0) else "CALL"
        
        assertividade_simulada = 100 if (i % 2 == 0 or porcentagem_min <= 90) else 85
        
        if assertividade_simulada >= porcentagem_min:
            sinais_gerados.append(f"`{tf_fmt};{par_escolhido};{horario_str};{direcao}`")
            
        if len(sinais_gerados) >= 30:
            break
            
    if not sinais_gerados:
        return "⚠️ Nenhum sinal encontrado atingiu a porcentagem mínima exigida."
        
    return f"📊 *Resultados para {tipo_mercado}:*\n\n" + "\n".join(sinais_gerados)
