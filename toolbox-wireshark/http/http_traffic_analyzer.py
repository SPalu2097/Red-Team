#!/usr/bin/env python3
"""
Universal HTTP Payload & Security Analyzer
Blue Team Security Analysis Tool - General Protocol & Encoding Inspector
"""

import re
import math
import sys
from dataclasses import dataclass
from typing import List

def calculate_entropy(data: bytes) -> float:
    """Arvutab andmete Shannoni entropia (0.0 kuni 8.0)."""
    if not data:
        return 0.0
    entropy = 0.0
    for x in range(256):
        p_x = float(data.count(x)) / len(data)
        if p_x > 0:
            entropy -= p_x * math.log(p_x, 2)
    return round(entropy, 4)

def parse_escaped_string(raw_str: str) -> bytes:
    """Teisendab logis oleva hex/escape stringi baitideks."""
    cleaned = raw_str.replace('\n', '').replace(' ', '').replace('\\', '')
    byte_list = bytearray()
    i = 0
    while i < len(cleaned):
        chunk = cleaned[i:i+2]
        if len(chunk) == 2:
            try:
                byte_list.append(int(chunk, 16))
            except ValueError:
                pass
        i += 2
    return bytes(byte_list)

def format_hexdump(data: bytes, length: int = 32) -> str:
    """Formatib esimesed N baiti Hex/ASCII vaateks."""
    snippet = data[:length]
    hex_part = " ".join(f"{b:02X}" for b in snippet)
    ascii_part = "".join(chr(b) if 32 <= b <= 126 else "." for b in snippet)
    return f"{hex_part:<96} | {ascii_part}"

@dataclass
class PacketAnalysis:
    request_num: str
    packet_id: str
    method: str
    url: str
    payload_len_bytes: int
    entropy: float
    payload_type: str
    features: List[str]
    hexdump_preview: str

class UniversalHTTPAnalyzer:
    def __init__(self, log_content: str):
        self.log_content = log_content

    def _detect_payload_type(self, raw_bytes: bytes, entropy: float) -> str:
        """Tuvastab universaalselt sisu tüübi, tihenduse või krüpteeringu."""
        if len(raw_bytes) == 0:
            return "Tühi sisu (No Payload)"
            
        # GZip tihenduse tuvastus
        if raw_bytes.startswith(b'\x1f\x8b'):
            return "GZip tihendatud andmed (Compressed Data)"
            
        # TLS / SSL tunnel
        if raw_bytes.startswith(b'\x17\x03\x03') or raw_bytes.startswith(b'\x16\x03\x03'):
            return "Krüpteeritud TLS/SSL sessiooni andmed"

        # Loetav tekst (JSON / HTML / XML / Plaintext)
        if entropy < 4.8 and all(32 <= b <= 126 or b in (9, 10, 13) for b in raw_bytes[:100]):
            if raw_bytes.strip().startswith(b'{') or raw_bytes.strip().startswith(b'['):
                return "Selgetekst: JSON objekt"
            elif raw_bytes.strip().startswith(b'<'):
                return "Selgetekst: XML / HTML dokument"
            else:
                return "Selgetekst: Tavalised HTTP parameetrid / Plaintext"

        # Tugevalt krüpteeritud või tihendatud sisu
        if entropy > 7.0:
            return "Kõrge entropia: Krüpteeritud payload või binaarfail (AES/ZIP/Pilt)"

        return "Binaarsed andmed / Tundmatu kood"

    def analyze(self) -> List[PacketAnalysis]:
        results = []
        # Tuvastame HTTP POST, GET, PUT, DELETE päringu plokid
        blocks = re.split(r'-{3,}\s*HTTP\s+(POST|GET|PUT|DELETE|PATCH)', self.log_content)
        
        # re.split moodustab paare (meetod, ploki sisu)
        i = 1
        while i < len(blocks) - 1:
            method = blocks[i]
            block = blocks[i+1]
            i += 2
            
            req_match = re.search(r'#(\d+)\s*\(Pakett\s*#(\d+)\)', block)
            url_match = re.search(r'URL:\s*(\S+)', block)
            payload_match = re.search(r'Sisu \(Payload\):\s*(.*)', block, re.DOTALL)
            
            if not (req_match and url_match):
                continue
                
            req_num = req_match.group(1)
            packet_id = req_match.group(2)
            url = url_match.group(1)
            
            payload_text = payload_match.group(1) if payload_match else ""
            payload_text = re.split(r'-{3,}', payload_text)[0].strip()
            
            raw_bytes = parse_escaped_string(payload_text)
            entropy = calculate_entropy(raw_bytes)
            
            features = []
            if raw_bytes.startswith(b'\x1f\x8b'):
                features.append("GZIP_Header")
            if b'{"' in raw_bytes or b'":' in raw_bytes:
                features.append("JSON_Structure")
            if b'\x17\x03\x03' in raw_bytes:
                features.append("TLS_App_Data")

            payload_type = self._detect_payload_type(raw_bytes, entropy)
            hexdump = format_hexdump(raw_bytes, length=32)

            results.append(PacketAnalysis(
                request_num=req_num,
                packet_id=packet_id,
                method=method,
                url=url,
                payload_len_bytes=len(raw_bytes),
                entropy=entropy,
                payload_type=payload_type,
                features=features if features else ["Generic_Payload"],
                hexdump_preview=hexdump
            ))
            
        return results

def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    else:
        print("Kasutamine: python universal_http_analyzer.py <logifail.txt>")
        return

    analyzer = UniversalHTTPAnalyzer(content)
    analyses = analyzer.analyze()

    output_filename = "http_analuysi_raport.txt"

    with open(output_filename, "w", encoding="utf-8") as f:
        def custom_print(text=""):
            print(text)
            print(text, file=f)

        custom_print("=" * 85)
        custom_print("         BLUE TEAM UNIVERSAL HTTP PROTOCOL INSPECTION REPORT")
        custom_print("=" * 85)
        custom_print(f"Kokku tuvastatud HTTP pakette: {len(analyses)}\n")

        for p in analyses:
            custom_print(f"[+] Päring #{p.request_num} | Pakett #{p.packet_id}")
            custom_print(f"    Meetod:          {p.method}")
            custom_print(f"    URL:             {p.url}")
            custom_print(f"    Sisu pikkus:     {p.payload_len_bytes} baiti")
            custom_print(f"    Entropia:        {p.entropy} / 8.0")
            custom_print(f"    Sisu tüüp:       {p.payload_type}")
            custom_print(f"    Tunnused:        {', '.join(p.features)}")
            custom_print(f"    Sisu eelvaade:   {p.hexdump_preview}")
            custom_print("-" * 85)

    print(f"\n[+] Raport salvestati faili: {output_filename}")

if __name__ == "__main__":
    main()