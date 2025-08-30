import requests

def pegar_pokemon(nome):
    url = f"https://pokeapi.co/api/v2/pokemon/{nome.lower()}"
    try:
        resposta = requests.get(url, timeout=5)
        if resposta.status_code == 200:
            return resposta.json()
        else:
            print(f"Erro {resposta.status_code}: não consegui pegar {nome}")
    except requests.exceptions.RequestException as e:
        print("Erro de conexão:", e)

def pegar_tipo(url_tipo):
    try:
        resposta = requests.get(url_tipo, timeout=5)
        if resposta.status_code == 200:
            return resposta.json()
    except requests.exceptions.RequestException as e:
        print("Erro de conexão:", e)

def pegar_movimento(url_move):
    try:
        r = requests.get(url_move, timeout=5)
        if r.status_code == 200:
            return r.json()
    except requests.exceptions.RequestException:
        return None

while True:
    # --- POKÉMON DE ATAQUE ---
    
    nome_ataque = input("\nDigite o nome do Pokémon de ataque (ou 'sair' para encerrar): ")
    if nome_ataque.lower() == "sair":
        break

    pokemon_atk = pegar_pokemon(nome_ataque)
    if not pokemon_atk:
        continue

    tipos_atk = [pegar_tipo(t['type']['url']) for t in pokemon_atk['types']]
    if not all(tipos_atk):
        continue

    print("\033[35m=== Pokémon de Ataque ===\033[0m")
    print("Nome:", pokemon_atk['name'].title())
    print("Tipos:", ", ".join(t['name'].title() for t in tipos_atk))
    

    #----TELA DE SUPER AFETIVOS----

    super_efetivos = set()
    for tipo in tipos_atk:
        for t in tipo['damage_relations']['double_damage_to']:
            super_efetivos.add(t['name'])

    print("\033[35m=\033[0m" * 25)
    print("\033[36mÉ super efetivo contra:\033[0m")
    for tipo in super_efetivos:
        print("-", tipo.title())


    #----MENU DE HABILIDADES----

    movimentos = pokemon_atk['moves']
    if not movimentos:
        print("Esse Pokémon não tem movimentos cadastrados na PokéAPI.")
        continue

    print("\n\033[33mHabilidades disponíveis:\033[0m")
    for i, move in enumerate(movimentos[:7], 1):
        print(f"{i}. {move['move']['name'].title()}")

    while True:
        try:
            escolha = int(input("Escolha o número do ataque: "))
            if 1 <= escolha <= 7:
                ataque_escolhido = movimentos[escolha - 1]['move']['name']
                url_ataque = movimentos[escolha - 1]['move']['url']
                dados_ataque = pegar_movimento(url_ataque)
                break
            else:
                print("Número inválido, escolha novamente.")
        except ValueError:
            print("Digite um número válido.")

    print(f"\nVocê escolheu o ataque: \033[32m{ataque_escolhido.title()}\033[0m")
    print('')
    print("\033[36m=\033[0m" * 30)

    
    #----TANTO DE DANO QUE VAI CAUSAR/ ESPECIFICAÇÕES----

    if dados_ataque:
        print("\033[34mDetalhes do ataque:\033[0m")
        print("Tipo:", dados_ataque['type']['name'].title())
        print("Poder base:", dados_ataque.get('power', '50'))  
        print("Precisão:", dados_ataque.get('accuracy', '—'))

    tipo_ataque = dados_ataque['type']['name'] if dados_ataque else None
    dano_base = dados_ataque.get('power', 50) if dados_ataque else 50 


    # --- POKÉMON DE DEFESA ---
    nome_defesa = input("\nDigite o nome do Pokémon de defesa (ou 'sair' para encerrar): ")
    if nome_defesa.lower() == "sair":
        break

    pokemon_def = pegar_pokemon(nome_defesa)
    if not pokemon_def:
        continue

    tipos_def = [pegar_tipo(t['type']['url']) for t in pokemon_def['types']]
    if not all(tipos_def):
        continue

    print("\033[31m=== Pokémon de Defesa ===\033[0m")
    print("Nome:", pokemon_def['name'].title())
    print("Tipos:", ", ".join(t['name'].title() for t in tipos_def))


    # --- CÁLCULO DO DANO COM MULTIPLICADOR DE TIPO ---

    multiplicador = 1
    for tipo_def in tipos_def:
        damage_rel = pegar_tipo(f"https://pokeapi.co/api/v2/type/{tipo_def['name']}")
        if damage_rel:
            if any(d['name'] == tipo_ataque for d in damage_rel['damage_relations']['double_damage_from']):
                multiplicador *= 2
            elif any(d['name'] == tipo_ataque for d in damage_rel['damage_relations']['half_damage_from']):
                multiplicador *= 0.5
            elif any(d['name'] == tipo_ataque for d in damage_rel['damage_relations']['no_damage_from']):
                multiplicador *= 0

    dano_final = dano_base * multiplicador
    print(f"\n {nome_ataque.title()} causou {dano_final} de dano em {nome_defesa.title()}!")
