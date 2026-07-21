import os
import re
import sys


def korja_unikaalsed_ipd(failitee):
    unikaalsed_ipd = set()

    # Regulaaravaldis standardse IPv4 aadressi tuvastamiseks
    ip_muster = re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b")

    try:
        with open(failitee, "r", encoding="utf-8", errors="ignore") as fail:
            for rida in fail:
                leitud = ip_muster.findall(rida)
                unikaalsed_ipd.update(leitud)

        return sorted(list(unikaalsed_ipd))

    except FileNotFoundError:
        print(f"Viga: Faili nimega '{failitee}' ei leitud.")
        return []


if __name__ == "__main__":
    # Kui argument anti käsurealt kaasa (nt: python3 vahendaja.py analuus.txt)
    if len(sys.argv) > 1:
        faili_tee = sys.argv[1].strip()
    else:
        # Kui argumenti ei antud, küsime seda kasutajalt
        faili_tee = input(
            "Sisesta tekstifaili nimi või tee (nt analuus.txt): "
        ).strip()

    if not faili_tee:
        print("Faili nime ei sisestatud!")
    else:
        tulemused = korja_unikaalsed_ipd(faili_tee)

        if tulemused:
            print(f"\nKokku leiti {len(tulemused)} unikaalset IP-aadressi.")

            valjund_fail = "ip_aadressid.txt"

            with open(valjund_fail, "w", encoding="utf-8") as f:
                for ip in tulemused:
                    f.write(f"{ip}\n")

            print(f"Tulemused edukalt salvestatud faili: {valjund_fail}")
