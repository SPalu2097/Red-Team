import sys
import os
import re
import csv

def parse_dns_log(input_file, output_file):
    pattern = r"Pakett #(\d+) \| IP: ([\d\.]+) -> Päris domeeni: ([\w\.-]+)"
    rows = []

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            for line in f:
                match = re.search(pattern, line)
                if match:
                    pkt, ip, domain = match.groups()
                    role = "Klient (Päring)" if ip == "172.17.0.2" else "DNS Server (Vastus)"
                    
                    # Eraldame juurdomeeni (nt google.hu, live.com)
                    parts = domain.split(".")
                    root_domain = ".".join(parts[-2:]) if len(parts) >= 2 else domain
                        
                    rows.append({
                        "Paketi_nr": int(pkt),
                        "IP_Aadress": ip,
                        "Roll": role,
                        "Subdomeen_ja_Domeen": domain,
                        "Juurdomeen": root_domain
                    })

        if not rows:
            print("⚠️ Hoiatus: Ühtegi vastavat DNS rida ei leitud. Kontrolli sisendfaili formaati!")
            return

        # Kirjutame andmed CSV-faili kasutades sisseehitatud csv.DictWriter-it
        fieldnames = ["Paketi_nr", "IP_Aadress", "Roll", "Subdomeen_ja_Domeen", "Juurdomeen"]
        
        # utf-8-sig lisab faili algusesse BOM-i, et Excel avaks eesti tähed täpselt õigesti
        with open(output_file, "w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()
            writer.writerows(rows)

        print(f"✅ Edukalt töödeldud {len(rows)} rida!")
        print(f"📁 Tulemus salvestatud faili: {output_file}")

    except Exception as e:
        print(f"❌ Viga faili töötlemisel: {e}")

def main():
    # 1. KONTROLL: Kas kasutaja andis failinime käsurea argumendina?
    if len(sys.argv) > 1:
        input_filename = sys.argv[1]
    else:
        # 2. KÜSIMINE: Kui argumenti polnud, küsime käsureal kasutajalt
        input_filename = input("Sisesta TXT faili tee või nimi: ").strip()

    # Kontrollime, kas sisendfail on olemas
    if not os.path.exists(input_filename):
        print(f"❌ Viga: Faili '{input_filename}' ei leitud!")
        sys.exit(1)

    # Moodustame automaatselt väljundfaili nime (.csv laiendiga)
    base_name = os.path.splitext(input_filename)[0]
    output_filename = f"{base_name}.csv"

    parse_dns_log(input_filename, output_filename)

if __name__ == "__main__":
    main()
