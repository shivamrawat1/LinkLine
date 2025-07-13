import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GmailService:
    @staticmethod
    def send_email_with_credentials(credentials, to_email, subject, body):
        """Send email using Gmail API with provided credentials object"""
        try:
            service = build('gmail', 'v1', credentials=credentials)
            message = MIMEText(body)
            message['to'] = to_email
            message['subject'] = subject
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            sent_message = service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            return {
                'success': True,
                'message_id': sent_message['id'],
                'thread_id': sent_message['threadId']
            }
        except HttpError as error:
            print(f'An error occurred: {error}')
            return {
                'success': False,
                'error': str(error)
            }
        except Exception as e:
            print(f'An unexpected error occurred: {e}')
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def send_bulk_emails_with_credentials(credentials, recipients, subject, body):
        """Send emails to multiple recipients using provided credentials object"""
        results = {
            'sent_count': 0,
            'failed_count': 0,
            'errors': []
        }
        for recipient in recipients:
            if recipient.get('email') and recipient['email'] != 'Not found':
                result = GmailService.send_email_with_credentials(credentials, recipient['email'], subject, body)
                if result['success']:
                    results['sent_count'] += 1
                else:
                    results['failed_count'] += 1
                    results['errors'].append({
                        'email': recipient['email'],
                        'error': result.get('error', 'Unknown error')
                    })
        return results 