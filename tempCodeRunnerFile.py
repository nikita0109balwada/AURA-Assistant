def save_chat():
    if backend.last_generated_text:
        backend.save_pdf_dialog(backend.last_generated_text)
    else:
        print("No recent chat to save.")