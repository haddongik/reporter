# battle_report.py
# 전투 데이터 분석 및 리포트 생성 모듈

from app.utils.report_utils import (process_attack_event,process_state_info, process_character_status)

def generate_battle_report(data, report_type=None):
    if report_type == "minimal":
        return generate_minimal_report(data)
    elif report_type == "regular":
        return generate_regular_report(data)
    else:
        print(f"지원하지 않는 리포트 타입: {report_type}")
        return

def process_battle_events(turn_data: dict, characters: dict) -> list[str]:
    report = []
    
    if "turn_index" in turn_data:
        report.append(f"\n## 턴 {turn_data['turn_index']}\n")
    
    if "history" in turn_data:
        for sub_history in turn_data["history"]:
            if "sub_owner_code" in sub_history:
                report.append(f"# {sub_history['sub_owner_code']}의 행동\n")
            
            if "history" in sub_history:
                for event in sub_history["history"]:
                    event_type = event.get("type", "")
                    
                    if event_type == "attack":
                        report.append(process_attack_event(event))
                    
                    elif event_type == "sub_state_info":
                        state = event.get("state", "")
                        report.append(process_state_info(state))
                        
                        # 아군 처리
                        if "frineds" in event:  # 오타 유지
                            friends_data = event["frineds"]
                            # 딕셔너리인 경우 리스트로 변환
                            if isinstance(friends_data, dict):
                                friends_data = list(friends_data.values())
                            # 리스트가 아닌 경우 리스트로 감싸기
                            elif not isinstance(friends_data, list):
                                friends_data = [friends_data]
                            
                            # code를 기준으로 정렬
                            friends_data.sort(key=lambda x: x.get("code", ""))
                            
                            for char_info in friends_data:
                                report.extend(process_character_status(
                                    char_info.get("code", ""),
                                    char_info,
                                    characters,
                                    is_friend=True
                                ))
                        
                        # 적군 처리
                        if "enemies" in event:
                            enemies_data = event["enemies"]
                            # 딕셔너리인 경우 리스트로 변환
                            if isinstance(enemies_data, dict):
                                enemies_data = list(enemies_data.values())
                            # 리스트가 아닌 경우 리스트로 감싸기
                            elif not isinstance(enemies_data, list):
                                enemies_data = [enemies_data]
                            
                            # code를 기준으로 정렬
                            enemies_data.sort(key=lambda x: x.get("code", ""))
                            
                            for enemy_info in enemies_data:
                                report.extend(process_character_status(
                                    enemy_info.get("code", ""),
                                    enemy_info,
                                    characters,
                                    is_friend=False
                                ))
    
    return report

def generate_minimal_report(data):
    report = ["◆ 전투 분석 리포트(minimal)\n"]
    characters = {}
    current_turn = 0
    
    for turn_data in data:
        current_turn = turn_data.get("turn_index", current_turn)
        report.extend(process_battle_events(turn_data, characters))
    
    # 전투 요약 정보
    report.extend([
        "\n◆ 전투 요약\n",
        f"• 총 턴 수: {current_turn}\n",
        "• 참가 캐릭터:\n"
    ])
    
    for code, info in characters.items():
        report.append(f"  ◦ {code} (ID: {info['id']})\n")
    
    return "".join(report)

def generate_regular_report(data):
    report = ["◆ 전투 분석 리포트(regular)\n"]
    characters = {}
    current_turn = 0
    
    for turn_data in data:
        current_turn = turn_data.get("turn_index", current_turn)
        report.extend(process_battle_events(turn_data, characters))
    
    # 전투 요약 정보
    report.extend([
        "\n◆ 전투 요약\n",
        f"• 총 턴 수: {current_turn}\n",
        "• 참가 캐릭터:\n"
    ])
    
    for code, info in characters.items():
        report.append(f"  ◦ {code} (ID: {info['id']})\n")
    
    return "".join(report)