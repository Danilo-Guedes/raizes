

def handle_week_text(weekday_text):
    if weekday_text in ["segunda", "terça", "quarta", "quinta", "sexta"]:
        return weekday_text + "-feira"
    else:
        return weekday_text

