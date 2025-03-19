# battle_report.py
# 전투 데이터 분석 및 리포트 생성 모듈

def generate_battle_report(data, report_type=None):

    if report_type == "minimal":
        return generate_minimal_report(data)
    elif report_type == "regular":
        return generate_regular_report(data)
    else:
        print(f"지원하지 않는 리포트 타입: {report_type}")
        return

def generate_minimal_report(data):

    report = []
    report.append("# 전투 분석 리포트\n")
    
    # 턴 정보 추적
    current_turn = 0
    
    # 캐릭터 정보 저장 (코드 -> 이름 매핑 등을 위해)
    characters = {}
    
    # 데이터 순회하며 분석
    for turn_data in data:
        if "turn_index" in turn_data:
            current_turn = turn_data["turn_index"]
            report.append(f"\n## 턴 {current_turn}\n")
        
        if "history" in turn_data:
            for sub_history in turn_data["history"]:
                if "sub_owner_code" in sub_history:
                    owner_code = sub_history["sub_owner_code"]
                    report.append(f"### {owner_code}의 행동\n")
                
                if "history" in sub_history:
                    for event in sub_history["history"]:
                        event_type = event.get("type", "")
                        
                        # 공격 이벤트 분석
                        if event_type == "attack":
                            attacker = event.get("from_code", "알 수 없음")
                            target = event.get("target_code", "알 수 없음")
                            damage = event.get("dec_hp", 0)
                            total_damage = event.get("total_damage", 0)
                            critical = "치명타!" if event.get("critical", False) else ""
                            miss = "빗나감!" if event.get("miss", False) else ""
                            
                            attack_desc = f"- {attacker}이(가) {target}에게 공격: {damage} 데미지"
                            if critical:
                                attack_desc += f" ({critical})"
                            if miss:
                                attack_desc += f" ({miss})"
                            if "eff" in event:
                                attack_desc += f" [효과: {event['eff']}]"
                                
                            report.append(attack_desc + "\n")
                        
                        # 상태 정보 이벤트 분석
                        elif event_type == "sub_state_info":
                            state = event.get("state", "")
                            
                            if state == "sub_state_init":
                                report.append("- 전투 상태 초기화\n")
                            elif state == "pending_ready":
                                report.append("- 준비 대기 중\n")
                            elif state == "ready":
                                report.append("- 준비 완료\n")
                            elif state == "pending_start":
                                report.append("- 시작 대기 중\n")
                            elif state == "pending_end":
                                report.append("- 종료 대기 중\n")
                            elif state == "ended":
                                report.append("- 행동 종료\n")
                            elif state == "next":
                                report.append("- 다음 행동 준비\n")
                            
                            # 캐릭터 상태 정보 수집
                            if "friends" in event:
                                for char_id, char_info in event["friends"].items():
                                    code = char_info.get("code", "")
                                    hp = char_info.get("hp", 0)
                                    
                                    if code not in characters:
                                        characters[code] = {"id": char_id, "last_hp": 0}
                                    
                                    # HP 변화 추적
                                    if characters[code]["last_hp"] != 0 and characters[code]["last_hp"] != hp:
                                        hp_change = hp - characters[code]["last_hp"]
                                        if hp_change < 0:
                                            report.append(f"- {code}의 HP가 {abs(hp_change)} 감소 (현재 HP: {hp})\n")
                                        else:
                                            report.append(f"- {code}의 HP가 {hp_change} 증가 (현재 HP: {hp})\n")
                                    
                                    characters[code]["last_hp"] = hp
                            
                            if "enemies" in event:
                                enemies_data = event["enemies"]
                                # enemies가 딕셔너리인 경우
                                if isinstance(enemies_data, dict):
                                    for enemy_id, enemy_info in enemies_data.items():
                                        code = enemy_info.get("code", "")
                                        hp = enemy_info.get("hp", 0)
                                        
                                        if code not in characters:
                                            characters[code] = {"id": enemy_id, "last_hp": 0}
                                        
                                        # HP 변화 추적
                                        if characters[code]["last_hp"] != 0 and characters[code]["last_hp"] != hp:
                                            hp_change = hp - characters[code]["last_hp"]
                                            if hp_change < 0:
                                                report.append(f"- {code}의 HP가 {abs(hp_change)} 감소 (현재 HP: {hp})\n")
                                            else:
                                                report.append(f"- {code}의 HP가 {hp_change} 증가 (현재 HP: {hp})\n")
                                        
                                        characters[code]["last_hp"] = hp
                                # enemies가 리스트인 경우
                                elif isinstance(enemies_data, list):
                                    for i, enemy_info in enumerate(enemies_data):
                                        if isinstance(enemy_info, dict):
                                            enemy_id = enemy_info.get("id", f"enemy_{i}")
                                            code = enemy_info.get("code", "")
                                            hp = enemy_info.get("hp", 0)
                                            
                                            if code not in characters:
                                                characters[code] = {"id": enemy_id, "last_hp": 0}
                                            
                                            # HP 변화 추적
                                            if characters[code]["last_hp"] != 0 and characters[code]["last_hp"] != hp:
                                                hp_change = hp - characters[code]["last_hp"]
                                                if hp_change < 0:
                                                    report.append(f"- {code}의 HP가 {abs(hp_change)} 감소 (현재 HP: {hp})\n")
                                                else:
                                                    report.append(f"- {code}의 HP가 {hp_change} 증가 (현재 HP: {hp})\n")
                                            
                                            characters[code]["last_hp"] = hp
    
    # 전투 요약 정보
    report.append("\n## 전투 요약\n")
    report.append(f"- 총 턴 수: {current_turn}\n")
    report.append("- 참가 캐릭터:\n")
    
    for code, info in characters.items():
        report.append(f"  - {code} (ID: {info['id']})\n")
    
    return "".join(report) 

def generate_regular_report(data):
    pass