import os
import subprocess
import platform

def handle_local_commands(user_input: str) -> bool:
    """
    Executes local system commands based on user input.
    Returns True if a command was executed.
    """
    cmd = user_input.strip().lower()
    os_name = platform.system()

    COMMANDS = {
    "open_vs_code": [
        "vscode",
        "vs code",
        "open the vs code",
        "open vs code",
        "launch visual studio code",
        "start coding",
        "open vscode"
    ],
    "open_chrome": [
        "open chrome",
        "chrome",
        "launch  chrome"
        "launch google chrome",
        "start browser",
        "open browser",
        "open the browser"
    ]
}
    # Open VS Code commmadn
    if any(c in cmd for c in COMMANDS['open_vs_code']) :#"open the vs code" in cmd or "open vs code" in cmd:
        # print("Opening Visual Studio Code...")
        if os_name == "Windows":
            os.system("code")
        elif os_name == "Darwin":  # macOS
            subprocess.run(["open", "-a", "Visual Studio Code"])
        elif os_name == "Linux":
            subprocess.run(["code"])
        return True

    if any(c in cmd for c in COMMANDS['open_chrome']) : #in cmd:
        # print("Opening Google Chrome...")
        if os_name == "Windows":
            os.system("start chrome")
        elif os_name == "Darwin":
            subprocess.run(["open", "-a", "Google Chrome"])
        elif os_name == "Linux":
            subprocess.run(["google-chrome"])
        return True

    return False
