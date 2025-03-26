BATTLE_PROMPTS = {
    "STATUS": {
        "turn_compare": """
        Analyze the following battle logs in English:

        [User Turn Log]
        {user_turn_content}

        [Server Turn Log]
        {server_turn_content}

        Analysis points:
        - Compare the data. If there are no differences, simply output the message: 'Verification successful.' Do not include any additional explanation.
        - Differences in actions/damage/effects/status
        - Similarities
        - User advantages
        - Suspicious manipulations
        Analysis result:
        """
    },
    "HP": {
        "turn_compare": """
        Analyze the following battle logs in English:

        [User Turn Log]
        {user_turn_content}

        [Server Turn Log]
        {server_turn_content}

        Analysis points:
        - Compare the data. If there are no differences, simply output the message: 'Verification successful.' Do not include any additional explanation.
        - Differences in HP values
        - HP changes
        - User advantages
        - Suspicious manipulations
        Analysis result:
        """
    },
    "ATTACK": {
        "turn_compare": """
        Analyze the following battle logs in English:

        [User Turn Log]
        {user_turn_content}

        [Server Turn Log]
        {server_turn_content}

        Analysis points:
        - Compare the data. If there are no differences, simply output the message: 'Verification successful.' Do not include any additional explanation.
        - Differences in attack actions
        - Damage values
        - Critical hits
        - User advantages
        - Suspicious manipulations
        Analysis result:
        """
    },
    "FULL": {
        "full_analyze": """
        Analyze the differences and similarities between user data and server data.
        The server data is considered to be completely accurate without any errors,
        while the user data may contain errors (including potential hacking attempts).

        User Data:
        {original}

        Server Data:
        {comparison}

        Analysis Points:
        1. Key Differences
        2. Similarities
        3. If errors are found, determine if the user data shows significant advantages or disadvantages
        4. Overall Assessment (whether to consider it as false detection or hacking)
        5. If determined as hacking, identify the hacking method
        6. If determined as false detection, identify the false detection method
        Detailed Analysis Result:
        """
    }
} 