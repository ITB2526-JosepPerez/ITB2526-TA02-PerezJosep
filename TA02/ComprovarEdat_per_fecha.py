"""
Programa: ComprovarEdat
Autor: Josep
01/10/2025
Descripció:
Aquest programa demana a l’usuari que introdueixi la seva edat
i comprova si és major o menor d’edat. Finalment, mostra un missatge
indicant que el programa ha finalitzat.
"""

from datetime import datetime

# Demanem a l'usuari que introdueixi la data de naixement
data_str = input("Introdueix la teva data de naixement (DD/MM/AAAA): ")

# Convertim la cadena en objecte datetime
try:
    data_naixement = datetime.strptime(data_str, "%d/%m/%Y")
except ValueError:
    print("Format incorrecte. Introdueix la data com DD/MM/AAAA.")
    exit()

# Obtenim la data actual
data_actual = datetime.today()

# Comprovem que la data no sigui futura
if data_naixement > data_actual:
    print("La data introduïda és futura. Introdueix una data vàlida.")
    exit()

# Calculem l'edat
edat = data_actual.year - data_naixement.year
# Ajustem si encara no ha fet els anys aquest any
if (data_actual.month, data_actual.day) < (data_naixement.month, data_naixement.day):
    edat -= 1

# Comprovem si és major d'edat
if edat >= 18:
    print("Ets major d'edat.")
else:
    print("Encara ets menor d'edat.")

print("Programa Finalitzat")