import os
import sys
from scapy.all import (
    ARP,
    DNS,
    DNSQR,
    ICMP,
    IP,
    TCP,
    UDP,
    PcapReader,
)
from scapy.layers.http import HTTPRequest


def analoosi_pcap(
    sisend_pcap,
    http_valjund,
    ip_valjund,
    paroolide_valjund,
    dns_valjund,
    plaintext_valjund,
):
    print(f"\nAlustan faili {sisend_pcap} töötlemist...")

    unikaalsed_ipd = set()
    unikaalsed_dns = set()

    post_count = 0
    paroolide_count = 0
    dns_count = 0
    arp_count = 0
    plaintext_count = 0

    protokolli_nimed = {1: "ICMP", 6: "TCP", 17: "UDP"}

    with (
        open(http_valjund, "w", encoding="utf-8") as http_file,
        open(paroolide_valjund, "w", encoding="utf-8") as pass_file,
        open(dns_valjund, "w", encoding="utf-8") as dns_file,
        open(plaintext_valjund, "w", encoding="utf-8") as pt_file,
    ):

        with PcapReader(sisend_pcap) as pcap_paketid:
            for packet_idx, packet in enumerate(pcap_paketid, 1):

                # 1. IP ja ARP detailide kogumine
                if packet.haslayer(IP):
                    src_ip = packet[IP].src
                    dst_ip = packet[IP].dst
                    ttl = packet[IP].ttl
                    proto_num = packet[IP].proto
                    proto_nimi = protokolli_nimed.get(
                        proto_num, f"Muu ({proto_num})"
                    )
                    unikaalsed_ipd.add((src_ip, dst_ip, proto_nimi, ttl))

                elif packet.haslayer(ARP):
                    arp_count += 1
                    src_ip = packet[ARP].psrc
                    dst_ip = packet[ARP].pdst
                    unikaalsed_ipd.add((src_ip, dst_ip, "ARP", "-"))

                # 2. DNS päringud
                if packet.haslayer(DNS) and packet.haslayer(DNSQR):
                    dns_count += 1
                    try:
                        qname = packet[DNSQR].qname.decode(
                            "utf-8", errors="ignore"
                        ).rstrip(".")
                        src_ip = (
                            packet[IP].src
                            if packet.haslayer(IP)
                            else "Tundmatu"
                        )

                        if (src_ip, qname) not in unikaalsed_dns:
                            unikaalsed_dns.add((src_ip, qname))
                            dns_file.write(
                                f"Pakett #{packet_idx} | IP: {src_ip} -> Päris"
                                f" domeeni: {qname}\n"
                            )
                    except Exception:
                        pass

                # 3. HTTP POST päringud
                if packet.haslayer(HTTPRequest):
                    http_layer = packet[HTTPRequest]
                    method = (
                        http_layer.Method.decode("utf-8", errors="ignore")
                        if http_layer.Method
                        else ""
                    )

                    if method == "POST":
                        host = (
                            http_layer.Host.decode("utf-8", errors="ignore")
                            if http_layer.Host
                            else "Tundmatu"
                        )
                        path = (
                            http_layer.Path.decode("utf-8", errors="ignore")
                            if http_layer.Path
                            else ""
                        )

                        http_file.write(
                            f"--- HTTP POST PÄRING #{post_count + 1} (Pakett"
                            f" #{packet_idx}) ---\n"
                        )
                        http_file.write(f"URL: http://{host}{path}\n")

                        if packet.haslayer(TCP) and packet[TCP].payload:
                            payload = bytes(packet[TCP].payload)
                            if b"\r\n\r\n" in payload:
                                sisu = payload.split(b"\r\n\r\n", 1)[1]
                                if sisu:
                                    sisu_tekst = sisu.decode(
                                        "utf-8", errors="ignore"
                                    ).strip()
                                    if sisu_tekst:
                                        http_file.write(
                                            f"Sisu (Payload):\n{sisu_tekst}\n"
                                        )

                        http_file.write("-" * 50 + "\n\n")
                        post_count += 1

                # 4. PLAIN TEXT PROTOKOLLIDE LEIDMINE (FTP, TELNET, SMTP, HTTP Headers)
                if packet.haslayer(TCP) and packet[TCP].payload:
                    dport = packet[TCP].dport
                    sport = packet[TCP].sport
                    raw_payload = bytes(packet[TCP].payload)

                    # FTP (Port 21), Telnet (Port 23), SMTP (Port 25)
                    if dport in [21, 23, 25] or sport in [21, 23, 25]:
                        tekst = raw_payload.decode(
                            "utf-8", errors="ignore"
                        ).strip()
                        if tekst:
                            proto_silt = (
                                "FTP"
                                if 21 in (dport, sport)
                                else "TELNET"
                                if 23 in (dport, sport)
                                else "SMTP"
                            )
                            pt_file.write(
                                f"--- {proto_silt} TEKST (Pakett"
                                f" #{packet_idx}) ---\n"
                            )
                            if packet.haslayer(IP):
                                pt_file.write(
                                    f"Ühendus: {packet[IP].src}:{sport} ->"
                                    f" {packet[IP].dst}:{dport}\n"
                                )
                            pt_file.write(f"Andmed: {tekst}\n")
                            pt_file.write("-" * 50 + "\n\n")
                            plaintext_count += 1

                # 5. Paroolide / kasutajate üldine otsing toorandmetest
                raw_bytes = bytes(packet)
                if (
                    b"password" in raw_bytes.lower()
                    or b"passwd" in raw_bytes.lower()
                ):
                    tekstina = raw_bytes.decode("utf-8", errors="ignore")

                    pass_file.write(
                        f"--- LEITUD HUVITAV PAKETT #{packet_idx} ---\n"
                    )
                    if packet.haslayer(IP):
                        pass_file.write(
                            f"Ühendus: {packet[IP].src} -> {packet[IP].dst}\n"
                        )

                    pass_file.write("Paketi sisu (kust leiti vaste):\n")
                    for rida in tekstina.splitlines():
                        if any(
                            x in rida.lower()
                            for x in ["pass", "user", "login", "admin"]
                        ):
                            pass_file.write(f"  > {rida.strip()}\n")

                    pass_file.write("-" * 50 + "\n\n")
                    paroolide_count += 1

                if packet_idx % 10000 == 0:
                    print(f"Töödeldud {packet_idx} paketti...")

    # 6. IP-ühenduste faili kirjutamine
    print(f"Kirjutan unikaalsed IP-aadressid faili {ip_valjund}...")
    with open(ip_valjund, "w", encoding="utf-8") as ip_file:
        ip_file.write(
            f"Kokku leiti {len(unikaalsed_ipd)} unikaalset ühendust (sealhulgas"
            f" {arp_count} ARP paketti).\n"
        )
        ip_file.write("=" * 85 + "\n")
        ip_file.write(
            f"{'SOURCE IP':<22} -> {'DESTINATION IP':<22} | {'PROTO':<8} |"
            f" {'TTL':<5}\n"
        )
        ip_file.write("-" * 85 + "\n")

        for src, dst, proto, ttl in sorted(
            unikaalsed_ipd, key=lambda x: (x[2], x[0])
        ):
            ip_file.write(f"{src:<22} -> {dst:<22} | {proto:<8} | {ttl:<5}\n")

    print("\nTöö valmis!")
    print(f"1. HTTP POST päringud: {http_valjund} (Leiti {post_count} tk)")
    print(
        f"2. DNS päringud: {dns_valjund} (Leiti {len(unikaalsed_dns)} unikaalset"
        " päringut)"
    )
    print(
        f"3. Plain-text liiklus (FTP/Telnet/SMTP): {plaintext_valjund} (Leiti"
        f" {plaintext_count} rida)"
    )

    if paroolide_count > 0:
        print(
            f"4. Potentsiaalsed paroolid: {paroolide_valjund} (Leiti"
            f" {paroolide_count} kahtlast paketti)"
        )
    else:
        print("4. Otsing 'password' ei andnud ühtegi tulemust.")

    print(
        f"5. IP nimekiri salvestatud: {ip_valjund} (Leiti"
        f" {len(unikaalsed_ipd)} unikaalset rida)"
    )


if __name__ == "__main__":
    print("=== PCAP/PCAPNG ANALÜSAATOR ===")

    if len(sys.argv) > 1:
        sisend_fail = sys.argv[1].strip()
    else:
        sisend_fail = input(
            "Sisesta uuritava PCAP/PCAPNG faili nimi või tee: "
        ).strip()

    sisend_fail = sisend_fail.strip("'\"")

    if not sisend_fail:
        print("Viga: Faili nime ei sisestatud!")
    elif not os.path.exists(sisend_fail):
        print(
            f"Viga: Faili nimega '{sisend_fail}' ei leitud praegusest kaustast."
        )
    else:
        baas_nimi = os.path.splitext(os.path.basename(sisend_fail))[0]

        http_valjund = f"1_{baas_nimi}_http_post.txt"
        ip_valjund = f"2_{baas_nimi}_ip_laiendatud.txt"
        paroolide_valjund = f"3_{baas_nimi}_paroolid.txt"
        dns_valjund = f"4_{baas_nimi}_dns_paringud.txt"
        plaintext_valjund = f"5_{baas_nimi}_plaintext_andmed.txt"

        analoosi_pcap(
            sisend_pcap=sisend_fail,
            http_valjund=http_valjund,
            ip_valjund=ip_valjund,
            paroolide_valjund=paroolide_valjund,
            dns_valjund=dns_valjund,
            plaintext_valjund=plaintext_valjund,
        )
