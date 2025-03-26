# battle_report.py
# 전투 데이터 분석 및 리포트 생성 모듈

from app.utils.report_utils import (
    process_attack_event, 
    process_state_info, 
    process_character_status,
    convert_and_sort_data,
    process_eff_info,
    get_current_states_summary
)
from typing import Union, Any

def generate_battle_report(data, report_type=None):
    report = ["◆ Battle Analysis Report ({report_type})\n"]
    characters = {}
    current_turn = 0
    
    for turn_data in data:
        current_turn = turn_data.get("turn_index", current_turn)
        report.extend(process_battle_events(turn_data, characters, report_type))
    
    if report_type == "full":
        report.extend(["\n◆ Battle Summary\n",f"• Total Turns: {current_turn}\n","• Participating Characters:\n"])
        for code, info in characters.items():
            report.append(f"  ◦ {code} (ID: {info['id']})\n")
    
    return "".join(report)

def process_battle_events(turn_data: dict, characters: dict, report_type: str) -> list[str]:
    report = []
    
    if "turn_index" in turn_data:
        report.append(f"\n## Turn {turn_data['turn_index']}\n")
    
    if "history" in turn_data:
        for sub_history in turn_data["history"]:
            if "sub_owner_code" in sub_history:
                report.append(f"# {sub_history['sub_owner_code']} Action ({sub_history['sub_type']})\n")

                # Add status summary
                if report_type == "full" or report_type == "effect":
                    state_summary = get_current_states_summary()
                    if state_summary:
                        report.append(state_summary)
            
            if "history" in sub_history:
                for event in sub_history["history"]:
                    event_type = event.get("type", "")
                    
                    if event_type == "attack":
                        report.append(process_attack_event(event, report_type))
                    
                    elif event_type == "sub_state_info":
                        state = event.get("state", "")
                        report.append(process_state_info(state, report_type))
                        
                        # Process allies
                        if "frineds" in event:  # Keep typo
                            friends_data = convert_and_sort_data(event["frineds"])
                            for char_info in friends_data:
                                report.extend(process_character_status(
                                    char_info.get("code", ""),
                                    char_info,
                                    characters,
                                    is_friend=True,
                                    report_type=report_type
                                ))
                        
                        # Process enemies
                        if "enemies" in event:
                            enemies_data = convert_and_sort_data(event["enemies"])
                            for enemy_info in enemies_data:
                                report.extend(process_character_status(
                                    enemy_info.get("code", ""),
                                    enemy_info,
                                    characters,
                                    is_friend=False,
                                    report_type=report_type
                                ))

                    elif event_type in ["add_state", "remove_state", "immune", "anti_skill_effect"]:
                        eff_report = process_eff_info(event, report_type)
                        if eff_report:
                            report.append(eff_report)
    
    return report