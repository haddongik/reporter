import os
import json
import base64
import zlib
from typing import Dict, Any, Optional

def print_json_recursively(data: Any, indent: int = 0) -> None:
    """
    JSON 데이터를 재귀적으로 순회하며 출력합니다.
    
    Args:
        data: 출력할 데이터
        indent: 들여쓰기 레벨
    """
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
    """
    JSON 파일을 읽어서 로드합니다.
    
    Args:
        file_path: JSON 파일 경로
        
    Returns:
        Optional[Dict[str, Any]]: 로드된 JSON 데이터
    """
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
    """
    Base64 디코딩 후 zlib 압축 해제를 수행합니다.
    
    Args:
        encoded_data: Base64로 인코딩된 데이터
        
    Returns:
        Optional[str]: 압축 해제된 데이터
    """
    try:
        decoded_bytes = base64.b64decode(encoded_data)
        decompressed_data = zlib.decompress(decoded_bytes).decode("utf-8")
        return decompressed_data
    except (base64.binascii.Error, zlib.error, UnicodeDecodeError) as e:
        print(f"디코딩/압축 해제 오류: {e}")
        return None

def process_json_data(json_data: Dict[str, Any], header: str, key: str) -> Optional[Dict[str, Any]]:
    """
    JSON 데이터에서 특정 헤더와 키를 사용하여 데이터를 추출합니다.
    
    Args:
        json_data: 원본 JSON 데이터
        header: 추출할 헤더
        key: 추출할 키
        
    Returns:
        Optional[Dict[str, Any]]: 처리된 데이터
    """
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
    """
    JSON 데이터를 분석용 데이터로 변환합니다.
    
    Args:
        json_data: 원본 JSON 데이터
        header: 추출할 헤더
        key: 추출할 키
        
    Returns:
        Optional[Dict[str, Any]]: 분석용 데이터
    """
    processed_data = process_json_data(json_data, header, key)
    if not processed_data:
        print("데이터 처리에 실패했습니다.")
        return None
    return processed_data 