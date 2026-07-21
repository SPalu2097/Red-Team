import csv
import os
import socket
import sys

# Kontrollime, kas faili nimi anti käsurealt argumentina
if len(sys.argv) > 1:
    sisend_fail = sys.argv[1].strip()
else:
    # Kui argumenti ei antud, küsime seda kasutajalt
    sisend_fail = input(
        "Sisesta IP-aadresside faili nimi (nt list1.txt): "
    ).strip()

# Kontrollime, kas fail on olemas
if not os.path.exists(sisend_fail):
    print(f"Viga: Faili nimega '{sisend_fail}' ei leitud!")
    exit()

# Loeme IP-aadressid failist
with open(sisend_fail, "r", encoding="utf-8", errors="ignore") as f:
    ips = [line.strip() for line in f if line.strip()]

if not ips:
    print("Fail on tühi või ei sisalda IP-aadresse.")
    exit()

print(
    f"\nFailist leiti {len(ips)} IP-aadressi. Pärime andmed Team Cymru WHOIS"
    " serverist..."
)

# Team Cymru WHOIS formaadi koostamine
query_lines = ["begin", "verbose"] + ips + ["end"]
query_payload = "\n".join(query_lines) + "\n"

tulemused = []

try:
    # Ühendume Team Cymru WHOIS serveriga (port 43)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(15)
    s.connect(("whois.cymru.com", 43))

    # Saadame päringu ja võtame vastuse vastu
    s.sendall(query_payload.encode("utf-8"))

    response = ""
    while True:
        data = s.recv(4096)
        if not data:
            break
        response += data.decode("utf-8", errors="ignore")
    s.close()

    # Töötleme vastuse read
    lines = response.strip().split("\n")

    for line in lines:
        line = line.strip()
        # Jätame vahele päised ja kommentaarid
        if (
            not line
            or line.startswith("Bulk mode")
            or line.startswith("AS")
            or line.startswith("An entry")
        ):
            continue

        parts = [p.strip() for p in line.split("|")]

        if len(parts) >= 7:
            asn = f"AS{parts[0]}" if parts[0] != "NA" else "Teadmata"
            ip = parts[1]
            riik = parts[3]
            as_nimi = parts[6]

            print(f"IP: {ip} -> Riik: {riik} | {asn} - {as_nimi}")
            tulemused.append([ip, riik, asn, as_nimi])

except Exception as e:
    print(f"Viga Team Cymru päringu tegemisel: {e}")

# Genereerime väljundfaili nime
faili_nimi_ilma_laiendita = os.path.splitext(sisend_fail)[0]
valjund_fail = f"tulemused_{faili_nimi_ilma_laiendita}.csv"

# Salvestame tulemused CSV failina
with open(valjund_fail, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["IP Aadress", "Riik (Kood)", "ASN", "Ettevõte / AS Nimi"])
    writer.writerows(tulemused)

print(f"\nValmis! Tulemused salvestati faili: {valjund_fail}")
