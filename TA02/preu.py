# python
def get_float(prompt, min_value=None, max_value=None, max_attempts=3):
    """Read a float from input with validation and a limited number of attempts."""
    for attempt in range(1, max_attempts + 1):
        try:
            raw = input(prompt).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nOperació cancel·lada.")
            raise SystemExit(0)

        if raw == "":
            remaining = max_attempts - attempt
            print(f"⚠️ Entrada buida. Introdueix un valor. Intentos restants: {remaining}")
            continue

        raw = raw.replace(",", ".")
        try:
            val = float(raw)
        except ValueError:
            remaining = max_attempts - attempt
            print(f"❌ Valor no vàlid. Introdueix un número. Intentos restants: {remaining}")
            continue

        if min_value is not None and val < min_value:
            remaining = max_attempts - attempt
            print(f"⚠️ El valor ha de ser ≥ {min_value}. Intentos restants: {remaining}")
            continue
        if max_value is not None and val > max_value:
            remaining = max_attempts - attempt
            print(f"⚠️ El valor ha de ser ≤ {max_value}. Intentos restants: {remaining}")
            continue

        return val

    # If we reach here, attempts exhausted
    raise ValueError("S'han exhaurit els intents per introduir un valor vàlid.")


def main():
    try:
        preu_original = get_float("Introdueix el preu original de l'article (€): ", min_value=0.0)
        descompte = get_float("Introdueix el descompte en percentatge (%): ", min_value=0.0, max_value=100.0)
    except ValueError as e:
        print(f"\n{e} Sortint.")
        raise SystemExit(1)

    preu_final = preu_original * (1 - descompte / 100)
    print(f"\n💰 El preu final després del descompte és: {preu_final:,.2f} €")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass


