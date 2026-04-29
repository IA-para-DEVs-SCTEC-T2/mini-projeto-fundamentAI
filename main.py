lista = [1,2,3,4,5,6,7,4,8,9,10,3,11,12,13,5,14,15,7]

def analisar_lista(lista):
    duplicados = []
    vistos = set()
    lista_sem_duplicados = []

    for numero in lista:
        if numero in vistos:
            if numero not in duplicados:
                duplicados.append(numero)
        else:
            vistos.add(numero)
            lista_sem_duplicados.append(numero)

    if duplicados:
        print("Há valores duplicados: ", duplicados)
    else:
        print("Não há valres duplicados")

    print("Nova lista sem duplicados: ", lista_sem_duplicados)

analisar_lista(lista)
