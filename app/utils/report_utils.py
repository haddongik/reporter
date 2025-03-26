from typing import Union, Any

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

def get_current_states_summary() -> str:
    summary = ["\n### Current States Summary\n"]
    
    try:
        all_states = state_tracker.get_all_states()
        for uid in all_states:
            states = all_states[uid]
            if states:  # Only display if states exist
                summary.append(f" * UID:{uid} Current States: {', '.join(states)}\n")
    except Exception as e:
        summary.append(f"* Error processing state information: {str(e)}\n")
    
    return "".join(summary) if len(summary) > 1 else ""

def format_status(status: dict | None) -> str:
    if not status:
        return "[]"
    
    # 딕셔너리의 각 항목을 'key:value' 형식으로 변환
    status_items = [f"   {key}:{value}" for key, value in status.items()]
    return "[\n" + "\n".join(status_items) + "\n]"

def convert_and_sort_data(data: Union[dict, list, Any]) -> list:
    # 딕셔너리인 경우 리스트로 변환 (키값 포함)
    if isinstance(data, dict):
        data = [{"id": id, **value} for id, value in data.items()]
    # 리스트가 아닌 경우 리스트로 감싸기
    elif not isinstance(data, list):
        data = [data]
    
    # id를 기준으로 정렬
    data.sort(key=lambda x: x.get("id", ""))
    
    return data

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
                direction = "increase" if change > 0 else "decrease"
                changes.append(f"{key}: {old_value} → {new_value} ({abs(change)} {direction})")
            else:
                changes.append(f"{key}: {old_value} → {new_value}")
    
    return changes

def process_attack_event(event: dict, report_type: str = "full") -> str:
    if report_type not in ["attack", "full"]:
        return ""  # 빈 문자열 반환
    
    from_uid = event.get("from_uid", "Unknown")
    from_code = event.get("from_code", "Unknown")
    target_uid = event.get("target_uid", "Unknown")
    target_code = event.get("target_code", "Unknown")
    dec_hp = event.get("dec_hp", 0)
    has_eff = event.get("eff", "Attack")
    is_critical = event.get("critical", False)
    is_miss = event.get("miss", False)
    
    attack_desc = f"- {from_code}(UID:{from_uid}) deals {dec_hp} damage to {target_code}(UID:{target_uid})"
    if has_eff:
        attack_desc += f" [Effect: {has_eff}]"
    if is_critical:
        attack_desc += f" (Critical)"
    if is_miss:
        attack_desc += f" (Miss)"

    return attack_desc + "\n"

def process_state_info(state: str, report_type: str = "full") -> str:
    if report_type not in ["status", "full"]:
        return ""  # 빈 문자열 반환
    
    return f"- event: {state}\n"

def process_character_status(
    code: str, 
    char_info: dict, 
    characters: dict, 
    is_friend: bool = True,
    report_type: str = "full"
) -> list[str]:
    report = []
    
    # 캐릭터 정보 저장
    if code not in characters:
        characters[code] = { "id": char_info.get("id", ""), "code": code, "status": {} }
    
    # 상태 정보 처리
    if report_type in ["status", "full"]:
        if "status" in char_info:
            old_status = characters[code]["status"].copy()
            characters[code]["status"] = char_info["status"]

            if not old_status and char_info["status"]:
                report.append(f"- {code}(UID:{char_info['id']}) STATUS Initialization:\n{format_status(char_info['status'])}\n")
            elif old_status != char_info["status"]:
                status_changes = compare_status_values(old_status, char_info["status"])
                if status_changes:
                    report.append(f"- {code}(UID:{char_info['id']}) STATUS Changes: {status_changes}\n")
    
    # HP 정보 처리
    if report_type in ["hp", "full"]:
        if "hp" in char_info:
            report.append(f"- {code}(UID:{char_info['id']}) HP: {char_info['hp']}\n")
    
    return report

def process_eff_info(event: dict, report_type: str = "effect") -> str:
    if report_type not in ["effect", "full"]:
        return ""  # 빈 문자열 반환
        
    event_type = event.get("type", "")
    target_code = event.get("target_code", "Unknown")
    state = event.get("state", "Unknown")
    target_uid = str(event.get("target_uid", "Unknown"))
    
    if event_type == "add_state":
        state_tracker.add_state(target_uid, state)
        return f"- Add State to {target_code}(UID:{target_uid}): {state}\n"
    elif event_type == "remove_state":
        state_tracker.remove_state(target_uid, state)
        return f"- Remove State from {target_code}(UID:{target_uid}): {state}\n"
    elif event_type == "immune":
        return f"- {target_code}(UID:{target_uid}) is immune to {state}\n"
    elif event_type == "anti_skill_effect":
        return f"- {target_code}(UID:{target_uid}) resists {state} effect\n"
    else:
        return f"- Unknown state effect: {event_type}\n"