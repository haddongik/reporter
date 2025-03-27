import os
import json
import base64
import zlib
import re
from typing import Dict, Any, Optional

def split_turns(log_text: str):
    
    parts = re.split(r"(## Turn \d+)", log_text)
    turns = []
    for i in range(1, len(parts), 2):
        turn_id = parts[i].strip()
        content = parts[i+1].strip()
        turns.append((turn_id, content))
    return turns

def print_json_recursively(data: Any, indent: int = 0) -> None:

    indent_str = "  " * indent
    
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                print(f"{indent_str}{key}:")
                print_json_recursively(value, indent + 1)
            else:
                print(f"{indent_str}{key}: {value}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                print(f"{indent_str}[{i}]:")
                print_json_recursively(item, indent + 1)
            else:
                print(f"{indent_str}[{i}]: {item}")
    else:
        print(f"{indent_str}{data}")

def load_json(file_path: str) -> Optional[Dict[str, Any]]:

    if not os.path.exists(file_path):
        print(f"파일이 존재하지 않습니다: {file_path}")
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data
    except json.JSONDecodeError as e:
        print(f"JSON 디코딩 오류: {e}")
        return None

def decode64_and_decompress(encoded_data: str) -> Optional[str]:

    try:
        decoded_bytes = base64.b64decode(encoded_data)
        decompressed_data = zlib.decompress(decoded_bytes).decode("utf-8")
        return decompressed_data
    except (base64.binascii.Error, zlib.error, UnicodeDecodeError) as e:
        print(f"디코딩/압축 해제 오류: {e}")
        return None

def process_json_data(json_data: Dict[str, Any], header: str, key: str) -> Optional[Dict[str, Any]]:

    if not json_data or header not in json_data["_source"]:
        print(f"헤더 '{header}'를 찾을 수 없습니다.")
        return None
    
    if key not in json_data["_source"][header]:
        print(f"키 '{key}'를 찾을 수 없습니다.")
        return None
    
    base64_encoded = json_data["_source"][header][key]
    decompressed_data = decode64_and_decompress(base64_encoded)
    
    if not decompressed_data:
        return None
    
    try:
        parsed_data = json.loads(decompressed_data)
        return parsed_data
    except json.JSONDecodeError as e:
        print(f"JSON 파싱 오류: {e}")
        return None

def make_analysis_data(json_data: Dict[str, Any], header: str, key: str) -> Optional[Dict[str, Any]]:

    processed_data = process_json_data(json_data, header, key)
    if not processed_data:
        print("데이터 처리에 실패했습니다.")
        return None
    return processed_data 