#!/usr/bin/env python3
"""
Universal HTTP & MMTLS Report TXT to CSV Converter
Blue Team Security Analysis Tool
"""

import re
import csv
import sys

def parse_report_txt_to_csv(input_txt_path: str, output_csv_path: str):
    """
    Loeb txt-kujul analüüsiraporti ja teisendab selle CSV-failiks.
    Toetab nii MMTLS-spetsiifilist kui ka universaalset HTTP raporti formaati.
    """
    with open(input_txt_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Eraldame raporti plokid (iga plokk algab sümbolitega "[+] Päring")
    blocks = re.split(r'(?=\[\+\]\s*Päring)', content)
    
    records = []

    for block in blocks:
        if not block.strip() or "[+] Päring" not in block:
            continue
        
        # Eraldame väljad regexi abil (paindlikud reeglid mõlema raporti jaoks)
        req_pkt = re.search(r'\[\+\]\s*Päring\s*#(\d+)\s*\|\s*Pakett\s*#(\d+)', block)
        method = re.search(r'Meetod:\s*(.*)', block)
        url = re.search(r'URL:\s*(.*)', block)
        mmtls_id = re.search(r'MMTLS ID:\s*(.*)', block)
        length = re.search(r'Sisu pikkus:\s*(\d+)', block)
        entropy = re.search(r'Entropia:\s*([\d\.]+)', block)
        
        # MMTLS raportis oli "Krüpto profiil", universaalses "Sisu tüüp"
        crypto = re.search(r'(?:Krüpto profiil|Sisu tüüp):\s*(.*)', block)
        
        structure = re.search(r'Sõnumi struktuur:\s*(.*)', block)
        features = re.search(r'Tunnused:\s*(.*)', block)
        preview = re.search(r'Sisu eelvaade:\s*(.*)', block)

        if req_pkt:
            # Kui olemas on Meetod (HTTP GET/POST), kasutame seda, muidu MMTLS ID-d
            meetod_voi_id = method.group(1).strip() if method else (mmtls_id.group(1).strip() if mmtls_id else "UNKNOWN")

            record = {
                "Päring_Nr": req_pkt.group(1).strip(),
                "Pakett_ID": req_pkt.group(2).strip(),
                "HTTP_Meetod_või_ID": meetod_voi_id,
                "URL": url.group(1).strip() if url else "",
                "Sisu_Pikkus_Baiti": int(length.group(1)) if length else 0,
                "Entropia": float(entropy.group(1)) if entropy else 0.0,
                "Sisu_Tyyp_ja_Krypto": crypto.group(1).strip() if crypto else "Tuvastamata",
                "Sonumi_Struktuur": structure.group(1).strip() if structure else "N/A",
                "Tunnused": features.group(1).strip() if features else "",
                "Sisu_Eelvaade": preview.group(1).strip() if preview else ""
            }
            records.append(record)

    # Kirjutame andmed CSV faili Euroopa/Eesti formaadis (semikooloniga)
    fieldnames = [
        "Päring_Nr", 
        "Pakett_ID", 
        "HTTP_Meetod_või_ID", 
        "URL", 
        "Sisu_Pikkus_Baiti", 
        "Entropia", 
        "Sisu_Tyyp_ja_Krypto", 
        "Sonumi_Struktuur", 
        "Tunnused", 
        "Sisu_Eelvaade"
    ]

    with open(output_csv_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(records)

    print(f"[+] Edukalt teisendatud {len(records)} paketti CSV faili: {output_csv_path}")

def main():
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else "http_analuys.csv"
        parse_report_txt_to_csv(input_file, output_file)
    else:
        print("Kasutamine: python http_raport_to_csv.py <raport.txt> [tulemus.csv]")

if __name__ == "__main__":
    main()