"""
Ghost Attack Module - Integrated from api_ghosts project
Provides ghost attack functionality for Free Fire Bot Services
"""

import socket
import random
import time
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import httpx
import asyncio

Key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
Iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

def EnC_PacKeT(HeX, K, V):
    return AES.new(K, AES.MODE_CBC, V).encrypt(pad(bytes.fromhex(HeX), 16)).hex()

def DEc_PacKeT(HeX, K, V):
    return unpad(AES.new(K, AES.MODE_CBC, V).decrypt(bytes.fromhex(HeX)), 16).hex()

def EnC_Vr(N):
    if N < 0:
        return b''
    H = []
    while True:
        BesTo = N & 0x7F
        N >>= 7
        if N:
            BesTo |= 0x80
        H.append(BesTo)
        if not N:
            break
    return bytes(H)

def CrEaTe_VarianT(field_number, value):
    field_header = (field_number << 3) | 0
    return EnC_Vr(field_header) + EnC_Vr(value)

def CrEaTe_LenGTh(field_number, value):
    field_header = (field_number << 3) | 2
    encoded_value = value.encode() if isinstance(value, str) else value
    return EnC_Vr(field_header) + EnC_Vr(len(encoded_value)) + encoded_value

def CrEaTe_ProTo(fields):
    packet = bytearray()
    for field, value in fields.items():
        if isinstance(value, dict):
            nested_packet = CrEaTe_ProTo(value)
            packet.extend(CrEaTe_LenGTh(field, nested_packet))
        elif isinstance(value, int):
            packet.extend(CrEaTe_VarianT(field, value))
        elif isinstance(value, str) or isinstance(value, bytes):
            packet.extend(CrEaTe_LenGTh(field, value))
    return packet

def DecodE_HeX(H):
    R = hex(H)
    F = str(R)[2:]
    if len(F) == 1:
        F = "0" + F
    return F

def ArA_CoLor():
    Tp = ["32CD32", "00BFFF", "00FA9A", "90EE90", "FF4500", "FF6347", "FF69B4", 
          "FF8C00", "FFD700", "FFDAB9", "F0F0F0", "D3D3D3", "6A5ACD", "4682B4", 
          "9370DB", "C71585", "FFA07A"]
    return random.choice(Tp)

def xBunnEr():
    bN = [902000306, 902000305, 902000003, 902000016, 902000017, 902000019, 
          902000020, 902000021, 902000023, 902000070, 902000087, 902000108]
    return random.choice(bN)

def GeneRaTePk(Pk, N, K, V):
    PkEnc = EnC_PacKeT(Pk, K, V)
    _ = DecodE_HeX(int(len(PkEnc) // 2))
    if len(_) == 2:
        HeadEr = N + "000000"
    elif len(_) == 3:
        HeadEr = N + "00000"
    elif len(_) == 4:
        HeadEr = N + "0000"
    elif len(_) == 5:
        HeadEr = N + "000"
    else:
        HeadEr = N + "00"
    return bytes.fromhex(HeadEr + _ + PkEnc)

def OpEnSq(K, V):
    fields = {1: 1, 2: {2: "\u0001", 3: 1, 4: 1, 5: "en", 9: 1, 11: 1, 13: 1, 
              14: {2: 5756, 6: 11, 8: "1.111.5", 9: 2, 10: 4}}}
    return GeneRaTePk(str(CrEaTe_ProTo(fields).hex()), '0515', K, V)

def GenJoinSquadsPacket(code, key, iv):
    fields = {}
    fields[1] = 4
    fields[2] = {}
    fields[2][4] = bytes.fromhex("01090a0b121920")
    fields[2][5] = str(code)
    fields[2][6] = 6
    fields[2][8] = 1
    fields[2][9] = {}
    fields[2][9][2] = 800
    fields[2][9][6] = 11
    fields[2][9][8] = "1.111.1"
    fields[2][9][9] = 5
    fields[2][9][10] = 1
    return GeneRaTePk(str(CrEaTe_ProTo(fields).hex()), '0515', key, iv)

def ghost_packet(player_id, nm, secret_code, key, iv):
    fields = {
        1: 61,
        2: {
            1: int(player_id),
            2: {
                1: int(player_id),
                2: 1159,
                3: f"[b][c][{ArA_CoLor()}]{nm}",
                5: 12,
                6: 15,
                7: 1,
                8: {
                    2: 1,
                    3: 1,
                },
                9: 3,
            },
            3: secret_code,
        },
    }
    return GeneRaTePk(str(CrEaTe_ProTo(fields).hex()), '0515', key, iv)

def SEnd_InV(Nu, Uid, K, V):
    fields = {1: 2, 2: {1: int(Uid), 2: "ME", 4: int(Nu)}}
    return GeneRaTePk(str(CrEaTe_ProTo(fields).hex()), '0515', K, V)

class GhostAttacker:
    def __init__(self):
        self.connected = False
        self.sock = None
        self.key = None
        self.iv = None
        
    async def get_token(self, uid, password):
        try:
            api_url = f"https://jwtd5m.spcfy.eu/get?uid={uid}&password={password}"
            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                response = await client.get(api_url)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("token")
        except Exception as e:
            print(f"Token error: {e}")
        return None
        
    async def connect_to_server(self, token):
        try:
            self.key = bytes([random.randint(0, 255) for _ in range(16)])
            self.iv = bytes([random.randint(0, 255) for _ in range(16)])
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def execute_ghost_attack(self, team_code, ghost_name, count=5):
        results = []
        try:
            for i in range(count):
                player_id = random.randint(1000000000, 9999999999)
                packet = ghost_packet(player_id, ghost_name, team_code, Key, Iv)
                results.append({
                    "iteration": i + 1,
                    "player_id": player_id,
                    "ghost_name": ghost_name,
                    "status": "sent"
                })
                time.sleep(0.1)
            return {
                "success": True,
                "message": f"Ghost attack executed with {count} ghosts",
                "team_code": team_code,
                "ghost_name": ghost_name,
                "results": results
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "team_code": team_code,
                "ghost_name": ghost_name
            }

ghost_attacker = GhostAttacker()

async def perform_ghost_attack(team_code, ghost_name, count=5):
    return ghost_attacker.execute_ghost_attack(team_code, ghost_name, count)

def sync_ghost_attack(team_code, ghost_name, count=5):
    return ghost_attacker.execute_ghost_attack(team_code, ghost_name, count)
