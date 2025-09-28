from app import email_client, classifier, summarizer, translator, formatter, image_gen, sender, db

def main():
    db.init_db()
    sender_email = "jaimemorenosanchez96@gmail.com"

    emails = email_client.fetch_emails(sender_email)
    for email in emails:
        email_id = email['id']
        if classifier.is_newsletter(email['text']):
            summary = summarizer.summarize_text(email['text'])
            summary_translated = translator.translate_to_spanish(summary)
            image_path = f"data/images/{email_id}.png"
            image_gen.generate_image(summary_translated, image_path)
            html_content = formatter.format_email(summary_translated, image_path)
            sender.send_email("mi_correo@dominio.com", email['subject'], html_content)
            db.mark_email_processed(email_id, email['sender'], email['subject'], email['date'])

if __name__ == "__main__":
    main()
