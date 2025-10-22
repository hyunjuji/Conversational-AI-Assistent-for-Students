import datetime as dt
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os


SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://mail.google.com/']

class gtCalendarManager:

    def __init__(self):

        self.creds = None
        self.service = None
        self.current_user = None

    def setup_credentials(self,email):

        try:
            user_token_file = os.path.join("credentials", f"{email.split('@')[0]}_token.json")
            credentials_file = os.path.join("credentials", "credentials.json")
            
            if not os.path.exists(credentials_file):
                return {"success": False, "message": f"Missing credentials.json at {credentials_file}"}
            
            if not os.path.exists(user_token_file):
                try:
                    self.creds = Credentials.from_authorized_user_file(user_token_file, SCOPES)
                except Exception as e:
                    self.creds = None

            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    try:
                        self.creds.refresh(Request())
                    except Exception as e:
                        self.creds = None
                if not self.creds:
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
                    self.creds = flow.run_local_server(port=0)
                    with open(user_token_file, 'w') as token:
                        token.write(self.creds.to_json())

            self.current_user = email

            self.service = build('calendar', 'v3', credentials=self.creds)

            return {"success": True, "message": f"Successfully set up credentials for {email}"}

        except Exception as e:
            return {"success": False, "message": f"Error setting up credentials: {str(e)}"}
    

    def create_event(self, summary, start, end, timezone='America/New_York', description=None, location=None, recurrence=None):
        
        if not self.service:
            return {"success": False, "message": "Service not initialized. Please run setup_credentials first."}

        event = {
            'summary': summary,
            'start': {
                'dateTime': start,
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end,
                'timeZone': timezone,
            },
        }

        if description:
            event['description'] = description
        if location:
            event['location'] = location
        if recurrence:
            event['recurrence'] = [recurrence]

        try:
            result = self.service.events().insert(calendarId='primary', body=event).execute()
            
            return {
                "success": True,
                "event_id": result["id"],
                "user": self.current_user,
                "summary": summary,
                "start_time": start,
                "end_time": end,
                "timezone": timezone,
                "message": f"Successfully created event '{summary}' from {start} to {end}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": "event_creation_failed",
                "message": f"Failed to create event '{summary}': {str(e)}"
            }
    
    def delete_event(self, event_id, delete_series=False):
        if not self.service:
            return {    
                "success": False,
                "error": "service_not_initialized",
                "message": "Service not initialized. Call setup_credentials first."
            }

        try:
            try:
                event = self.service.events().get(calendarId='primary', eventId=event_id).execute()
                event_summary = event.get('summary', 'Untitled Event')
                event_start = event.get('start', {}).get('dateTime', 'Unknown time')
                recurring_event_id = event.get('recurringEventId', None)
            except Exception:
                event_summary = 'Unknown Event'
                event_start = 'Unknown time'
                recurring_event_id = None

            if delete_series and recurring_event_id:
                target_id = recurring_event_id
            else:
                target_id = event_id
            
            self.service.events().delete(calendarId='primary', eventId=target_id).execute()
            
            return {
                "success": True,
                "event_id": target_id,
                "user": self.current_user,
                "deleted_event": event_summary,
                "start_time": event_start,
                "message": f"Successfully deleted event '{event_summary}' (ID: {target_id})"
            }
            
        except Exception as e:
            error_msg = str(e)
            if "notFound" in error_msg or "404" in error_msg:
                return {
                    "success": False,
                    "error": "event_not_found",
                    "message": f"Event with ID '{event_id}' not found or already deleted"
                }
            else:
                return {
                    "success": False,
                    "error": "event_deletion_failed",
                    "message": f"Failed to delete event '{event_id}': {error_msg}"
                }


    def get_events(self, time_min=None, time_max=None):
        if not self.service:
            return {
                "success": False,
                "error": "service_not_initialized",
                "message": "Service not initialized. Call setup_credentials first."
            }
        
        if not time_max:
            time_max = (dt.datetime.utcnow() + dt.timedelta(hours=3)).isoformat() + 'Z'

        event_result = self.service.events().list(calendarId='primary', timeMin=time_min, timeMax=time_max, singleEvents=True, orderBy='startTime').execute()
        events = event_result.get('items', [])

        if not events:
            return {
                "success": True,
                "user": self.current_user,
                "events_count": 0,
                "events": [],
                "message": "No events found"
            }
        
        formatted_events = []
        for event in events:
            formatted_events.append({
                'id': event['id'],
                'summary': event.get('summary', 'No title'),
                'start': event.get('start', {}).get('dateTime', event.get('start', {}).get('date', 'No start time')),
                'end': event.get('end', {}).get('dateTime', event.get('end', {}).get('date', 'No end time')),
                'description': event.get('description', ''),
                'location': event.get('location', ''),
                'recurrence': event.get('recurrence', []),
                'recurringEventId': event.get('recurringEventId', None),
            })

        return formatted_events

