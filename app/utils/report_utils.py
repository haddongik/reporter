from typing import Union, Any

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

def convert_and_sort_data(data: Union[dict, list, Any]) -> list:
    """
    데이터를 리스트로 변환하고 code 기준으로 정렬합니다.
    """
    # 딕셔너리인 경우 리스트로 변환
    if isinstance(data, dict):
        data = list(data.values())
    # 리스트가 아닌 경우 리스트로 감싸기
    elif not isinstance(data, list):
        data = [data]
    
    return data

# 전역 상태 추적기
class StateTracker:
    def __init__(self):
        self.states = {}  # uid -> set(states)
    
    def add_state(self, uid: Union[str, int], state: str):
        uid_str = str(uid)
        if uid_str not in self.states:
            self.states[uid_str] = set()
        self.states[uid_str].add(str(state))
    
    def remove_state(self, uid: Union[str, int], state: str):
        uid_str = str(uid)
        if uid_str in self.states:
            self.states[uid_str].discard(str(state))
            if not self.states[uid_str]:
                del self.states[uid_str]
    
    def get_states(self, uid: Union[str, int]) -> set:
        return self.states.get(str(uid), set())
    
    def get_all_states(self) -> dict:
        try:
            # uid를 정수로 변환하여 정렬
            sorted_uids = sorted(self.states.keys(), key=lambda x: int(x))
            result = {}
            for uid in sorted_uids:
                # 각 상태를 문자열로 처리하여 정렬
                states = self.states[uid]
                result[uid] = sorted(str(state) for state in states)
            return result
        except (ValueError, TypeError):
            # 정수 변환 실패 시 문자열 기준 정렬
            sorted_uids = sorted(self.states.keys())
            return {uid: sorted(str(state) for state in self.states[uid]) 
                   for uid in sorted_uids}

# 전역 상태 추적기 인스턴스 생성
state_tracker = StateTracker()

def process_add_state_event(event: dict) -> str:

    target_code = event.get("target_code", "알 수 없음")
    state = event.get("state", "알 수 없음")
    target_uid = str(event.get("target_uid", "알 수 없음"))
    
    # 전역 상태 업데이트
    state_tracker.add_state(target_uid, state)
    
    return f"- {target_code}(UID:{target_uid})에게 상태 추가: {state}\n"

def process_remove_state_event(event: dict) -> str:

    target_code = event.get("target_code", "알 수 없음")
    state = event.get("state", "알 수 없음")
    target_uid = str(event.get("target_uid", "알 수 없음"))
    
    # 전역 상태 업데이트
    state_tracker.remove_state(target_uid, state)
    
    return f"- {target_code}(UID:{target_uid})의 상태 제거: {state}\n"

def get_current_states_summary() -> str:

    summary = ["\n◆ 현재 상태 요약\n"]
    
    try:
        all_states = state_tracker.get_all_states()
        for uid in all_states:
            states = all_states[uid]
            if states:  # 상태가 있는 경우만 표시
                summary.append(f"• UID:{uid}의 현재 상태: {', '.join(states)}\n")
    except Exception as e:
        summary.append(f"• 상태 정보 처리 중 오류 발생: {str(e)}\n")
    
    return "".join(summary) if len(summary) > 1 else ""

def process_eff_info(event: dict) -> str:

    event_type = event.get("type", "")
    target_code = event.get("target_code", "알 수 없음")
    state = event.get("state", "알 수 없음")
    target_uid = str(event.get("target_uid", "알 수 없음"))
    
    if event_type == "add_state":
        state_tracker.add_state(target_uid, state)
        #return f"- {target_code}(UID:{target_uid})에게 상태 추가: {state}\n"
    elif event_type == "remove_state":
        state_tracker.remove_state(target_uid, state)
        #return f"- {target_code}(UID:{target_uid})의 상태 제거: {state}\n"
    elif event_type == "immune":
        pass
        #return f"- {target_code}(UID:{target_uid})가 {state} 상태에 면역\n"
    elif event_type == "anti_skill_effect":
        pass
        #return f"- {target_code}(UID:{target_uid})가 {state} 효과에 저항\n"
    else:
        pass
        #return f"- 알 수 없는 상태 효과: {event_type}\n"