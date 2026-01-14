def mock_lead_capture(name: str, email: str, platform: str):

    print(f"\n[TOOL CALLED] Lead captured successfully: {name}, {email}, {platform}\n")
    return "Lead processed successfully."