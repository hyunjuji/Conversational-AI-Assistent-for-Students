

gt_tools = [
    {
        "type":"function",
        "function":{
            "name": "web_search",
            "description": "Fallback web search when the university database lacks information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to perform."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "The maximum number of results to return. Defaults to 5."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "transfer_to_triage_agent",
            "description": "Call back to the triage agent if the user's question requires the other agent's help to answer.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "transfer_to_program_agent",
            "description": "Call this agent if the user is asking about the program or courses.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
        {
        "type": "function",
        "function": {
            "name": "transfer_to_calendar_agent",
            "description": "Call this agent if the user is asking about the calendar.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
        {
        "type": "function",
        "function": {
            "name": "transfer_to_db_agent",
            "description": "Call this agent if you need to get the user's or courseinformation from the database.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_program_details",
            "description": "Retrieves details of a specific program by its name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "program_name": {
                        "type": "string",
                        "description": "The name of the program to retrieve details for."
                    }
                },
                "required": ["program_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_semester_courses",
            "description": "Retrieves a list of courses for a specific semester.",
            "parameters": {
                "type": "object",
                "properties": {
                    "semester": {
                        "type": "string",
                        "description": "The semester for which to retrieve courses (e.g., 'Fall 2023')."
                    }
                },
                "required": ["semester"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "setup_credentials",
            "description": "Sets up Google Calendar and Gmail credentials for the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {
                    "type": "string",
                    "description": "The email address of the user to set up credentials for."
                }
            },
                "required": ["email"]
            }
        }
    },
    {
        "type": "function",
        "function":{
            "name": "create_event",
            "description": "Creates a new event in the user's Google Calendar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "The summary or title of the event."
                    },
                    "start": {
                        "type": "string",
                        "format": "date-time",
                        "description": "The start date and time of the event in ISO 8601 format."
                    },
                    "end": {
                        "type": "string",
                        "format": "date-time",
                        "description": "The end date and time of the event in ISO 8601 format."
                    },
                    "timezone": {
                        "type": "string",
                        "default": 'America/Atlanta',
                        "description": "The timezone for the event. Defaults to 'America/Atlanta'."
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description of the event."
                    },
                    "location": {
                        "type": "string",
                        "description": "Optional location of the event."
                    },
                    "recurrence": {
                        "type": "string",
                        "description": """Optional recurrence rule in RFC 5545 RRULE format. Use this to define repeating events (e.g., weekly meetings or daily tasks).
                        Examples:
                        - 'Every day for a week': RRULE:FREQ=DAILY;UNTIL=20250614T235900Z
                        - 'Every Monday': RRULE:FREQ=WEEKLY;BYDAY=MO
                        - 'Every weekday (Mon-Fri)': RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR
                        - 'Every month on the 1st': RRULE:FREQ=MONTHLY;BYMONTHDAY=1
                        - 'Every year on July 4th': RRULE:FREQ=YEARLY;BYMONTH=7;BYMONTHDAY=4
                        Make sure the UNTIL date is in UTC and formatted as YYYYMMDDThhmmssZ (e.g., 20251231T235900Z)."""
                    }
                },
                "required": ["summary", "start", "end"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_event",
            "description": "Deletes an event from the user's Google Calendar by event ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_id": {
                        "type": "string",
                        "description": "The ID of the event to delete."
                    },
                    "delete_series": {
                        "type": "boolean",
                        "default": False,
                        "description": "If true, deletes the entire series of recurring events. Defaults to false."
                    }
                },
                "required": ["event_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_dateandtime",
            "description": "Returns the current date and time in isoformat.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_events",
            "description": "Retrieves a list of events from the user's Google Calendar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "time_min": {
                        "type": "string",
                        "format": "date-time",
                        "description": "The start time to filter events from in ISO 8601 format(e.g., 2025-06-10T09:00:00-04:00)."
                    },
                    "time_max": {
                        "type": "string",
                        "format": "date-time",
                        "description": "The end time to filter events until in ISO 8601 format (e.g., 2025-06-11T09:00:00-04:00)."
                    }
                },
                "required": ["time_min"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_draft",
            "description": "Creates a draft email in the user's Gmail account.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "The recipient's email address."
                    },
                    "subject": {
                        "type": "string",
                        "description": "The subject of the email."  
                    },
                    "body": {
                        "type": "string",
                        "description": "The body content of the email."
                    }
                },
                "required": ["to", "subject", "body"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_draft",
            "description": "Sends a draft email from the user's Gmail account.",
            "parameters": {
                "type": "object",
                "properties": {
                    "draft_id": {
                        "type": "string",
                        "description": "The ID of the draft email to send."
                    }
                },
                "required": ["draft_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_emails",
            "description": "Retrieves a list of emails from the user's Gmail account within a specified time range.",
            "parameters": {
                "type": "object",
                "properties": {
                    "time_min": {
                        "type": "string",
                        "format": "date-time",
                        "description": "The start time to filter emails from in ISO 8601 format (e.g., 2025-06-10T09:00:00-04:00)."
                    },
                    "time_max": {
                        "type": "string",
                        "format": "date-time",
                        "description": "The end time to filter emails until in ISO 8601 format (e.g., 2025-06-11T09:00:00-04:00)."
                    },
                    "max_results": {
                        "type": "integer",
                        "default": 10,
                        "description": "The maximum number of emails to retrieve. Defaults to 10."
                    }
                },
                "required": ["time_min", "time_max"]
            }
        }
    },
    {
    "type": "function",
    "function": {
        "name": "query_university_db",
        "description": "Executes a SQL query on the university database and returns the result.",
        "parameters": {
            "type": "object",
            "properties": {
                "sql_query": {
                    "type": "string",
                    "description": "The SQL query to execute on university.db"
                }
            },
            "required": ["sql_query"]
        }
    }
},
]

gt_tools_dict = {tool["function"]["name"]: tool for tool in gt_tools}
