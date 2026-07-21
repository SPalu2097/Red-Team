import sys
import os
import re
import csv

def parse_smtp_log(input_file, output_file):
    records = []

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Eraldame logi plokkideks kriipsude järgi
        blocks = content.split("--------------------------------------------------")

        for block in blocks:
            lines = [line.strip() for line in block.strip().split("\n") if line.strip()]
            if not lines:
                continue

            pakett_nr = ""
            uhendus = ""
            allikas_ip = ""
            sihtkoht_ip = ""
            andmed = []

            for line in lines:
                # 1. Otsime paketi numbrit päisest
                header_match = re.search(r"Pakett #(\d+)", line)
                if header_match:
                    pakett_nr = header_match.group(1)
                    continue

                # 2. Otsime ühenduse rida
                if line.startswith("Ühendus:"):
                    uhendus = line.replace("Ühendus:", "").strip()
                    if "->" in uhendus:
                        parts = uhendus.split("->")
                        allikas_ip = parts[0].strip()
                        sihtkoht_ip = parts[1].strip()
                    continue

                # 3. Eraldame andmete rea (ja järgnevad mitmerealised vastused)
                if line.startswith("Andmed:"):
                    andmed.append(line.replace("Andmed:", "").strip())
                else:
                    # Kui rida ei ole päis ega ühendus, on see mitmerealiste andmete jätk
                    andmed.append(line)

            # Kui leiti vähemalt paketi number või andmed, lisame tulemusse
            if pakett_nr or andmed:
                records.append({
                    "Paketi_nr": pakett_nr,
                    "Ühendus": uhendus,
                    "Allikas_IP_Port": allikas_ip,
                    "Sihtkoht_IP_Port": sihtkoht_ip,
                    "Andmed": "\n".join(andmed)
                })

        if not records:
            print("⚠️ Hoiatus: Ühtegi vastavat SMTP rida ei leitud. Kontrolli sisendfaili!")
            return

        # Kirjutame andmed CSV-faili (kasutades sisseehitatud csv moodulit)
        fieldnames = ["Paketi_nr", "Ühendus", "Allikas_IP_Port", "Sihtkoht_IP_Port", "Andmed"]
        
        with open(output_file, "w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()
            writer.writerows(records)

        print(f"✅ Edukalt töödeldud {len(records)} SMTP plokki!")
        print(f"📁 Tulemus salvestatud faili: {output_file}")

    except Exception as e:
        print(f"❌ Viga faili töötlemisel: {e}")

def main():
    # 1. KONTROLL: Kas kasutaja andis failinime käsurea argumendina?
    if len(sys.argv) > 1:
        input_filename = sys.argv[1]
    else:
        # 2. KÜSIMINE: Kui argumenti polnud, küsime kasutajalt
        input_filename = input("Sisesta TXT faili tee või nimi: ").strip()

    if not os.path.exists(input_filename):
        print(f"❌ Viga: Faili '{input_filename}' ei leitud!")
        sys.exit(1)

    # Moodustame automaatselt väljundfaili nime (.csv laiendiga)
    base_name = os.path.splitext(input_filename)[0]
    output_filename = f"{base_name}.csv"

    parse_smtp_log(input_filename, output_filename)

if __name__ == "__main__":
    main()