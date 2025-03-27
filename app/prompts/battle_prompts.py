BATTLE_PROMPTS = {
    "STATUS": {
        "turn_compare": """You are a battle analysis expert. Compare the user's battle log with the server's battle log for each turn.
Focus on analyzing status changes and their effects on the battle.
Provide a concise analysis of any discrepancies or notable patterns in status changes.
Format your response in a clear, structured manner.""",
        "summary": """Based on the turn-by-turn analysis, provide a comprehensive summary of the battle's status changes.
Focus on key patterns, significant discrepancies, and their impact on the battle outcome.
Format your response in a clear, structured manner.""",
        "translate": """Translate the battle analysis summary into Korean.
Maintain the technical accuracy while ensuring natural Korean expression.
Keep any game-specific terms in their original form if they are commonly used that way."""
    },
    "HP": {
        "turn_compare": """You are a battle analysis expert. Compare the user's battle log with the server's battle log for each turn.
Focus on analyzing HP changes and their effects on the battle.
Provide a concise analysis of any discrepancies or notable patterns in HP changes.
Format your response in a clear, structured manner.""",
        "summary": """Based on the turn-by-turn analysis, provide a comprehensive summary of the battle's HP changes.
Focus on key patterns, significant discrepancies, and their impact on the battle outcome.
Format your response in a clear, structured manner.""",
        "translate": """Translate the battle analysis summary into Korean.
Maintain the technical accuracy while ensuring natural Korean expression.
Keep any game-specific terms in their original form if they are commonly used that way."""
    },
    "ATTACK": {
        "turn_compare": """You are a battle analysis expert. Compare the user's battle log with the server's battle log for each turn.
Focus on analyzing attack patterns and their effects on the battle.
Provide a concise analysis of any discrepancies or notable patterns in attack sequences.
Format your response in a clear, structured manner.""",
        "summary": """Based on the turn-by-turn analysis, provide a comprehensive summary of the battle's attack patterns.
Focus on key patterns, significant discrepancies, and their impact on the battle outcome.
Format your response in a clear, structured manner.""",
        "translate": """Translate the battle analysis summary into Korean.
Maintain the technical accuracy while ensuring natural Korean expression.
Keep any game-specific terms in their original form if they are commonly used that way."""
    },
    "FULL": {
        "turn_compare": """You are a battle analysis expert. Compare the user's battle log with the server's battle log.
Provide a comprehensive analysis covering all aspects of the battle including:
1. Status changes and their effects
2. HP changes and their impact
3. Attack patterns and sequences
4. Overall battle flow and strategy
5. Any discrepancies or anomalies

Format your response in a clear, structured manner with appropriate sections and bullet points."""
    },
    "PDF": {
        "create": """You are a professional report writer. Create a well-structured PDF report based on the battle analysis results.
The report should include:

1. Title Page:
   - Battle Analysis Report
   - Date and Time
   - Report ID

2. Executive Summary:
   - Brief overview of the battle
   - Key findings
   - Main conclusions

3. Detailed Analysis Sections:
   - Status Analysis
   - HP Analysis
   - Attack Pattern Analysis
   - Full Battle Analysis

4. Conclusions and Recommendations

Format the content in a professional manner with appropriate headings, subheadings, and sections.
Use bullet points and numbered lists where appropriate.
Include relevant statistics and data points.

The report should be clear, concise, and easy to read while maintaining technical accuracy."""
    }
} 