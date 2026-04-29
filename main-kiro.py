lista = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 3, 7, 11, 4, 9]

def verificar_duplicados(lista):
    vistos = set()
    duplicados = set()
    lista_limpa = []

    for numero in lista:
        if numero in vistos:
            duplicados.add(numero)
        else:
            vistos.add(numero)
            lista_limpa.append(numero)

    if duplicados:
        print("Há números duplicados na lista.")
        print("Números duplicados:", sorted(duplicados))
    else:
        print("Não há números duplicados.")

    print("Lista limpa:", lista_limpa)

verificar_duplicados(lista)

# prompt usado no Kiro: kiro, crie em Python uma função que verifica se existem numeros duplicados em uma lista de 20 numeros inteiros, com 5 destes 20 sendo duplicados. Print se há duplicados, quais são os numeros duplicados e, faça uma limpeza nesta lista, removendo os numeros duplicados, printando na tela a lista "limpa".

# Kiro, compare o arquivo "main.py" crido na mão, com o arquivo "main-kiro.py que vcês mesmo criou. Quero que você compare a implementação com em legilibilidade, eficiência e edge cases, por gentileza.

# Kiro, quero que você crie um arquivo em markdown com este resultado da comparação, este arquivo vai se chamar "comparaçao_cod_manual_kiro.md"

