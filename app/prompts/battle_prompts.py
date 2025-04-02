BATTLE_PROMPTS = {
    "STATUS": {
        "turn_compare":
		"""
            너는 전투 로그 및 보안 분석 전문가이다. 유저와 서버의 전투 로그를 턴 단위로 비교해 검증 결과를 생성하라.

            ### 목적:
            - 유저 로그와 서버 로그를 **턴 단위로 비교**한다.
            - 각 턴의 핵심 비교 포인트는 다음과 같다:
            1. STATUS CHANGE 항목의 정확성 비교
            2. 이전 턴의 STATUS INIT 결과를 기억하고 변화가 타당한지 평가
            - 일치 여부를 판별하고, 차이점이 있을 경우 구체적으로 기술한다.

            ### 출력 규칙:
            1. 유저 로그와 서버 로그가 동일하거나 논리적으로 일관되면:
            - turn {turn_index}: verify_success

            2. 차이가 있거나, 부자연스러운 변화가 있다면:
            - turn {turn_index}: verify_fail
                fact: STATUS CHANGE의 차이나 비정상적인 상태 변화 내용
                opinion: 이 차이에 대한 해석 (예: 조작 가능성, 불합리한 상태 변화 등)

            3. 첫 verify_fail 항목에는 "🔥불일치 최초 발견"을 추가한다.

            ### 분석 지침:
            - STATUS INIT은 초기 상태이므로 **다음 턴 이후에도 참고하여 비교**한다.
            - STATUS CHANGE가 실제로 타당한 변화인지 판단할 수 있어야 한다.
            - 로그는 대부분 structured format이므로, 변화 수치와 논리 흐름을 중심으로 판단한다.

            ### 입력 예시:
            User log:
            (실제 유저 턴 로그)

            Server log:
            (실제 서버 턴 로그)

            ### 출력 형식 예시:
            turn 1: verify_success  
            turn 2: verify_fail 🔥불일치 최초 발견  
            fact: user 로그에서는 c2023의 공격력이 1228 → 1596으로 증가하였지만, 서버 로그에서는 변화가 없음  
            opinion: 클라이언트가 임의로 STATUS CHANGE를 조작했을 가능성이 있음
		""",
        "summary":
		"""

        """
    },
    "HP": {
        "turn_compare": """
            너는 전투 로그 및 보안 분석 전문가이다. 유저와 서버의 전투 로그를 턴 단위로 비교해 검증 결과를 생성하라.

            ### 분석 대상:
            - 유저와 서버 각각의 전투 로그는 턴(Turn) 단위로 구성되어 있다.
            - 각 턴에는 캐릭터 UID 별 HP INFO가 포함된다.
            - 로그에는 중복된 HP INFO가 있을 수 있으며, 변화된 HP 수치만을 중심으로 분석해야 한다.

            ### 분석 목적:
            - 유저 로그와 서버 로그를 비교하여 각 턴의 HP 변화가 일치하는지 확인한다.
            - HP 수치가 불일치하거나, 피해량 계산이 불합리할 경우 이를 지적한다.
            - 단순히 수치만 비교하는 것이 아니라, **턴 전후 HP 변화가 논리적으로 일관적인지**도 평가한다.

            ### 출력 규칙:
            1. 유저 로그와 서버 로그가 동일하거나 논리적으로 일치하면:
            - turn {turn_index}: verify_success

            2. 차이가 있거나, 피해량이 불합리한 경우:
            - turn {turn_index}: verify_fail
                fact: 어떤 캐릭터의 어떤 HP 변화가 달랐는지, 얼마나 차이가 있었는지
                opinion: 이 차이에 대한 해석 (예: 클라이언트 조작 가능성, 버그 가능성 등)

            3. 첫 번째 verify_fail에는 "🔥불일치 최초 발견"을 표시한다.

            ### 비교 기준:
            - **HP 변화만을 중심으로 비교**한다. 중복된 HP INFO는 무시하고, 변화된 값을 중점 분석한다.
            - 동일한 캐릭터 UID 기준으로 전후 HP를 비교한다.
            - HP가 회복 또는 감소된 이유가 불명확하거나, 유저/서버 간 수치가 달라진다면 "verify_fail" 처리한다.

            ### 출력 형식 예시:
            turn 0: verify_success  
            turn 1: verify_fail 🔥불일치 최초 발견  
            fact: 유저 로그에서 c2023의 HP가 6266 → 8145로 증가했지만, 서버 로그에서는 6266 → 7351로 감소함  
            opinion: 유저가 클라이언트에서 체력을 임의로 회복했을 가능성이 있음

            ### 입력 예시:
            User Turn Log:
            {user_turn_log}

            Server Turn Log:
            {server_turn_log}
        """,
        "summary":
		"""

        """
    },
    "ATTACK": {
        "turn_compare":
		"""
            너는 전투 로그 및 보안 분석 전문가이다. 유저와 서버의 전투 로그를 턴 단위로 비교해 검증 결과를 생성하라.

            ### 분석 대상:
            - 각 턴은 공격자의 행동(Action)과 공격 결과 로그들로 구성된다.
            - 로그 항목은 다음과 같은 형식을 따른다:
            {공격자} deals {데미지 수치} damage to {피해자} [Effect: {효과}]

            ### 분석 목적:
            - 유저 로그와 서버 로그를 턴 단위로 비교하여 공격 로그가 일치하는지 확인한다.
            - 공격 횟수, 대상, 데미지 수치, 효과(Effect) 가 **모두 동일한지**를 확인한다.
            - 일치하지 않거나 수치가 다르거나 효과가 다른 경우 **비정상적인 조작이나 오류 가능성**을 판단한다.

            ### 출력 규칙:
            1. 유저 로그와 서버 로그가 동일하거나 논리적으로 일관되면:
            - turn {turn_index}: verify_success

            2. 차이가 있거나, 불일치가 발견되면:
            - turn {turn_index}: verify_fail
                fact: 어떤 공격이 어떻게 달랐는지 구체적으로 명시
                opinion: 이 차이에 대한 해석 (예: 데미지 조작 가능성, 누락된 공격 등)

            3. 첫 번째 verify_fail 항목에는 "🔥불일치 최초 발견"을 표시한다.

            ### 비교 기준:
            - 다음 항목이 모두 일치해야 `verify_success` 처리된다:
            - 공격자 UID
            - 피해자 UID
            - 데미지 수치 (± 허용 오차 없음)
            - 적용된 Effect
            - 공격 순서도 일치해야 한다.
            - 누락, 순서 바뀜, 수치 변경, 다른 Effect는 모두 `verify_fail` 대상이다.

            ### 출력 형식 예시:
            turn 1: verify_success  
            turn 2: verify_fail 🔥불일치 최초 발견  
            fact: 유저 로그에서 c2090_d_b_ray가 c2023에게 408 damage (Effect: HPDOWN_CASTER_ATT)를 입혔으나, 서버 로그에서는 0 damage 처리됨  
            opinion: 클라이언트가 공격 로그를 조작했거나, 서버 처리와 일치하지 않음

            ### 입력 예시:
            User Turn Log:
            {user_turn_log}

            Server Turn Log:
            {server_turn_log}
        """,
        "summary":
		"""

        """
    },
    "FULL": {
        "turn_compare": """You are a battle analysis expert. Compare the user's battle report with the server's battle report.
Focus on analyzing overall battle flow, key events, and any discrepancies.
Provide a comprehensive analysis of the entire battle.""",
        "summary": """You are a battle analysis expert. Create a comprehensive summary of the battle analysis.
Focus on key patterns, significant changes, and overall battle flow.
Keep the summary concise but informative."""
    },
    "TRANSLATE": """You are a professional translator. Translate the following battle analysis summary into Korean.
        Keep the translation natural and maintain the technical accuracy of the battle analysis terms.
        Use polite and formal Korean language."""
} 