def format_status(status: dict | None) -> str:

    if not status:
        return "[]"
    
    # 딕셔너리의 각 항목을 'key:value' 형식으로 변환
    status_items = [f"   {key}:{value}" for key, value in status.items()]
    return "[\n" + "\n".join(status_items) + "\n]"

def compare_status_values(old_status: dict | None, new_status: dict | None) -> list[str]:

    if not old_status or not new_status:
        return []
    
    changes = []
    for key in set(old_status.keys()) | set(new_status.keys()):
        old_value = old_status.get(key)
        new_value = new_status.get(key)
        
        if old_value != new_value:
            if isinstance(old_value, (int, float)) and isinstance(new_value, (int, float)):
                change = new_value - old_value
                direction = "증가" if change > 0 else "감소"
                changes.append(f"   {key}:{old_value} -> {key}:{new_value} ({abs(change)} {direction})")
            else:
                changes.append(f"   {key}:{old_value} -> {key}:{new_value}")
    
    return changes

def process_attack_event(event: dict) -> str:

    attacker = event.get("from_code", "알 수 없음")
    target = event.get("target_code", "알 수 없음")
    damage = event.get("dec_hp", 0)
    critical = "치명타" if event.get("critical", False) else ""
    miss = "빗나감" if event.get("miss", False) else ""
    
    attack_desc = f"- {attacker}이(가) {target}에게 공격: {damage} 데미지"
    if critical:
        attack_desc += f" ({critical})"
    if miss:
        attack_desc += f" ({miss})"
    if "eff" in event:
        attack_desc += f" [효과: {event['eff']}]"
    
    return attack_desc + "\n"

def process_state_info(state: str) -> str:

    state_messages = {
        "sub_state_init": "sub_state_init",
        "pending_ready": "pending_ready",
        "ready": "ready",
        "pending_start": "pending_start",
        "pending_end": "pending_end",
        "ended": "ended",
        "next": "next",
        "attack": "attack",
    }
    return f"• {state_messages.get(state, '알 수 없는 상태')}\n"

def process_character_status(code: str, char_info: dict, characters: dict, is_friend: bool = True) -> list[str]:

    messages = []
    char_id = char_info.get("id")
    hp = char_info.get("hp", 0)
    status = char_info.get("status")
    team = "아군" if is_friend else "적군"
    
    # 초기 상태 기록
    if code not in characters:
        characters[code] = {"id": char_id, "last_hp": hp, "last_status": status}
        messages.append(f"{team} {code}의 최초 HP : {abs(hp)}\n")
        messages.append(f"{team} {code}의 최초 STATUS : {format_status(status)}\n")
    
    # HP 변화 추적
    if characters[code]["last_hp"] != 0 and characters[code]["last_hp"] != hp:
        hp_change = hp - characters[code]["last_hp"]
        if hp_change < 0:
            messages.append(f"- {code}의 HP가 {abs(hp_change)} 감소 (현재 HP: {hp})\n")
        else:
            messages.append(f"- {code}의 HP가 {hp_change} 증가 (현재 HP: {hp})\n")
    
    # STATUS 변화 추적
    if "last_status" in characters[code]:
        if status != characters[code]["last_status"]:
            status_changes = compare_status_values(characters[code]["last_status"], status)
            if status_changes:
                messages.append(f"- {code}의 상태 변화 발생:\n[\n")
                messages.extend(f"{change}\n" for change in status_changes)
                messages.append("]\n")
            else:
                messages.append(f"- {code}의 STATUS가 {format_status(status)}로 변경됨\n")
    
    # 현재 상태 저장
    characters[code]["last_hp"] = hp
    characters[code]["last_status"] = status
    
    return messages