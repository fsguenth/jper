# JPER: API Specification

This document specifies the interface and data formats to be used by the JPER API.

The API will be mounted at a versioned endpoint, so that future releases of the API can be made without breaking
backwards compatibility for existing users.  e.g.

    /api/v1/...

## Data Interchange Models

The data interchange models are sub-sets of the full system data models.

There are two separate models: one which is the data format the notifications are provided in (the **Incoming Data Model**),
and the other which is the format the repositories will receive the data in (the **Outgoing Data Model**)

### Incoming Data Model

Any notifications coming from the provider should meet the following specification:

```json
{
    "event" : "<keyword for the kind of notification: acceptance, publication, etc.>",
    
    "provider" : {
        "agent" : "<string defining the software/process which put the content here, provided by provider - is this useful?>",
        "ref" : "<provider's globally unique reference for this research object>"
    },
    
    "targets" : [
        {
            "repository" : "<identifying string for repository - base URL, user account>",
            "requirement" : "<must|should>"
        }
    ],
    
    "content" : {
        "packaging_format" : "<identifier for packaging format used>"
    },
    
    "links" : [
        {
            "type" : "<link type: splash|fulltext>",
            "format" : "<html|pdf|xml>",
            "access" : "<type of access control on the resource: 'router' (reuqires router auth) or 'public' (no auth)>",
            "url" : "<provider's splash, fulltext or machine readable page>"
        }
    ],
    
    "embargo" : {
        "end" : "<date embargo expires>",
        "start" : "<date embargo starts>",
        "duration" : "<number of months for embargo to run>"
    },
    
    "metadata" : {
        "title" : "<publication title>",
        "version" : "<version of the record, e.g. AAM>",
        "publisher" : "<publisher of the content>",
        "source" : {
            "name" : "<name of the journal or other source (e.g. book)>",
            "identifier" : [
                {"type" : "issn", "id" : "<issn of the journal (could be print or electronic)>" },
                {"type" : "eissn", "id" : "<electronic issn of the journal>" },
                {"type" : "pissn", "id" : "<print issn of the journal>" },
                {"type" : "doi", "id" : "<doi for the journal or series>" }
            ]
        },
        "identifier" : [
            {"type" : "doi", "id" : "<doi for the record>" }
        ],
        "type" : "publication/content type",
        "author" : [
            {
                "name" : "<author name>",
                "identifier" : [
                    {"type" : "orcid", "id" : "<author's orcid>"},
                    {"type" : "email", "id" : "<author's email address>"},
                ],
                "affiliation" : "<author affiliation>"
            }
        ],
        "language" : "<iso language code>",
        "publication_date" : "<publication date>",
        "date_accepted" : "<date accepted for publication>",
        "date_submitted" : "<date submitted for publication>",
        "license_ref" : {
            "title" : "<name of licence>",
            "type" : "<type>", 
            "url" : "<url>", 
            "version" : "<version>",
        },
        "project" : [
            {
                "name" : "<name of funder>", 
                "identifier" : [
                    {"type" : "<identifier type>", "id" : "<funder identifier>"}
                ],
                "grant_number" : "<funder's grant number>"
            }
        ],
        "subject" : ["<subject keywords/classifications>"]
    }
}
```

Note that in this version of the system the "targets" field will not be implemented.

### Outgoing Data Model

Any request for a routed notification (except from the provider who created it) will meet the following specification:

```json
{
    "id" : "<opaque identifier for this notification>",
    "created_date" : "<date this notification was received>",
    "analysis_date" : "<date the routing analysis was carried out>",
    
    "event" : "<keyword for the kind of notification: acceptance, publication, etc.>",
    
    "content" : {
        "packaging_format" : "<identifier for packaging format used>",
    },
    
    "links" : [
        {
            "type" : "<link type: splash|fulltext>",
            "format" : "<html|pdf|xml>",
            "access" : "<type of access control on the resource: 'router' (reuqires router auth) or 'public' (no auth)>",
            "url" : "<provider's splash, fulltext or machine readable page>"
        }
    ],
    
    "embargo" : {
        "end" : "<date embargo expires>",
        "start" : "<date embargo starts>",
        "duration" : "<number of months for embargo to run>"
    },
    
    "metadata" : {
        "title" : "<publication title>",
        "version" : "<version of the record, e.g. AAM>",
        "publisher" : "<publisher of the content>",
        "source" : {
            "name" : "<name of the journal or other source (e.g. book)>",
            "identifier" : [
                {"type" : "issn", "id" : "<issn of the journal (could be print or electronic)>" },
                {"type" : "eissn", "id" : "<electronic issn of the journal>" },
                {"type" : "pissn", "id" : "<print issn of the journal>" },
                {"type" : "doi", "id" : "<doi for the journal or series>" }
            ]
        },
        "identifier" : [
            {"type" : "doi", "id" : "<doi for the record>" }
        ],
        "type" : "publication/content type",
        "author" : [
            {
                "name" : "<author name>",
                "identifier" : [
                    {"type" : "orcid", "id" : "<author's orcid>"},
                    {"type" : "email", "id" : "<author's email address>"},
                ],
                "affiliation" : "<author affiliation>"
            }
        ],
        "language" : "<iso language code>",
        "publication_date" : "<publication date>",
        "date_accepted" : "<date accepted for publication>",
        "date_submitted" : "<date submitted for publication>",
        "license_ref" : {
            "title" : "<name of licence>",
            "type" : "<type>", 
            "url" : "<url>", 
            "version" : "<version>",
        },
        "project" : [
            {
                "name" : "<name of funder>", 
                "identifier" : [
                    {"type" : "<identifier type>", "id" : "<funder identifier>"}
                ],
                "grant_number" : "<funder's grant number>"
            }
        ],
        "subject" : ["<subject keywords/classifications>"]
    }
}
```


## Validation API

The Validation API allows providers to test that their data feed to the system will be successful.

You must have the user role "provider" to access this endpoint.

If you are sending binary content, the request must take the form:

    POST /validate?api_key=<api_key>
    Content-Type: multipart/form-data; boundary=FulltextBoundary
    
    --FulltextBoundary
    
    Content-Disposition: form-data; name="metadata"
    Content-Type: application/json
    
    [Incoming Data Model JSON]
    
    --FulltextBoundary
    
    Content-Disposition: form-data; name="content"
    Content-Type: application/zip
    Content-Transfer-Encoding: base64
    
    [binary content]
    
    --FulltextBoundary--

If you are sending only the JSON notification, the request must take the form:

    POST /validate?api_key=<api_key>
    Content-Type: application/json
    
    [Incoming Data Model JSON]

On authentication failure (e.g. invalid api_key, incorrect user role) the system will respond with a 401 (Unauthorised) and no response body.

On validation failure the system will respond with the following

    HTTP 1.1  400 Bad Request
    Content-Type: application/json
    
    {
        "error" : "<human readable error message>"
    }

On validation success, the system will respond with 204 (No Content) and no response body.

## Notification API

### Create new notifications

The Notification API takes an identical request to the Validation API, so that providers can develop
against the Validation API and then switch seamlessly over to live notifications.  The only difference will
be in the response body.

You must have the user role "provider" to access this endpoint.

**NOTE: should we consider making the response to the Validation API the same as the Notification API too?**

If you are sending binary content, the request must take the form:

    POST /notification?api_key=<api_key>
    Content-Type: multipart/form-data; boundary=FulltextBoundary
    
    --FulltextBoundary
    
    Content-Disposition: form-data; name="metadata"
    Content-Type: application/json
    
    [Incoming Data Model JSON]
    
    --FulltextBoundary
    
    Content-Disposition: form-data; name="content"
    Content-Type: application/zip
    Content-Transfer-Encoding: base64
    
    [binary content]
    
    --FulltextBoundary--

If you are sending only the JSON notification, the request must take the form:

    POST /notification?api_key=<api_key>
    Content-Type: application/json
    
    [Incoming Data Model JSON]

On authentication failure (e.g. invalid api_key, incorrect user role) the system will respond with a 401 (Unauthorised) and no response body.

On completion of the request, the system will respond with 202 (Accepted) and the following response body

    HTTP 1.1  202 Accepted
    Content-Type: application/json
    Location: <url for api endpoint for accepted notification>
    
    {
        "status" : "accepted",
        "id" : "<unique identifier for the notification>",
        "location" : "<url for api endpoint for newly created notification>"
    }

Note that acceptance of a notification is not the same as the notification having been entered into the system
for routing - at this point it has only been accepted for processing, which will happen asynchronously to the request.

### Retrieve created notifications

This endpoint will return to you the JSON record for the notifications.

Anyone can access this endpoint.

    GET /notification/<id>[?api_key=<api_key>]

If the notification does not exist, you will receive a 404 (Not Found), and no response body.

If the requester is not authenticated as the provider of the notification, and the notification has not yet been routed, 
you will also receive a 404 (Not Found) and no response body.

If the notification is found and has been routed, you will receive a 200 (OK) and the following response body:

    HTTP 1.1  200 OK
    Content-Type: application/json
    
    [Incoming/Outgoing Data Model JSON]

If you are the provider of the notification, you will receive back the Incoming Data Model, augumented with any
data from the Outgoing Data Model that is not already present (e.g. analysed_date).

All other requesters will receive the Outgoing Data Model.


### Retrieve router-held content associated with notifications

This endpoint will return to you the original deposit package from the provider containing the fulltext content for the notification (if available)

This URL will appear in the notification JSON "link" field if it is available to use.

You need to have the user role "provider" or "repository" to access this endpoint.

    GET /notification/<id>/content?api_key=<api_key>
    
Authentication failure will result in a 401 (Unauthorised), and no response body.  Authentication failure can happen for
the following reasons:

* api_key is invalid
* You do not have the user role "provider" or "repository"
* You have the role "provider" and you were not the original creator of this notification
* You have the role "repository" and this notification has not yet been routed

If the notification content is not found, you will receive a 404 (Not Found) and no response body.

If the notification content is found and authentication succeeds you will receive a 200 (OK) and the following response:

    HTTP 1.1  200 OK
    Content-Type: application/zip
    Content-Transfer-Encoding: base64
    Packaging: <content packaging identifier>
    
    [Binary Content]

Note that a successful access by a user with the role "repository" will log a successful delivery of content notification
into the router (used for reporting on the router's ability to support REF compliance).

If you are retrieving content from a public link directly from the publisher's site, you should consider sending an
event to the Receipt API.

## Routing API

These endpoints lists routed notifications in "analysed_date" order, oldest first.

Note that as notifications are never updated (only created), this sorted list is guaranteed to be complete and return the same results
each time for the same request.  This is the reason for sorting by analysed_date rather than created_date, as the rate
at which items pass through the analysis may vary.

Allowed parameters for each request are:

* api_key - Optional.  May be used for tracking API usage, but no authentication is required for this endpoint.
* since - Required.  Timestamp from which to provide notifications, of the form YYYY-MM-DD or YYYY-MM-DDThh:mm:ssZ (in UTC timezone)
    * YYYY-MM-DD will be considered equivalent to YYYY-MM-DDT00:00:00Z
* page - Optional; defaults to 1.  Page number of results to return.
* pageSize - Optional; defaults to 25, maximum 100.  Number of results per page to return.

The response will be a 200 OK, with the following body

    HTTP 1.1  200 OK
    Content-Type: application/json
    
    {
        "since" : "<date from which results start in the form YYYY-MM-DDThh:mm:ssZ>",
        "page" : "<page number of results>,
        "pageSize" : "<number of results per page>,
        "timestamp" : "<timestamp of this request in the form YYYY-MM-DDThh:mm:ssZ>",
        "total" : "<total number of results at this time>",
        "notifications" : [
            "<ordered list of Outgoing Data Model JSON objects>"
        ]
    }

Note that the "total" may increase between requests, as new notifications are added to the end of the list.


### All routed notifications

The endpoint lists all routed notifications, without restricting them to the repositories they have been routed to.

You will not be able to tell from this endpoint which repositories have been identified for this notification.

    GET /routed[?<params>]

params and response are as specified above.

### Repository routed notifications

The endpoint lists all routed notifications for a given repository.

You will not be able to tell from this endpoint which other repositories have been identified for this notification.

    GET /routed/<repo_id>[?<params>]

params and response are as specified above.

## Receipt API

In order to support reporting around router's support for REF compliance, it is important for the router to record when content has been
successfully delivered to a repository.

When a repository retrieves content from the "/notification/[id]/content" endpoint a log of the retrieval will
automatically be created.

In other cases - such as when the repository retrieves the content directly from a publicly accessible publisher link - this
event cannot be recorded, so this API call should be used to record that retrieval.

    POST /notification/<notification id>/<repository id>?api_key=<api_key>

If authentication fails you will receive a 401 (Unauthorised) and no response body

If successful you will receive a 204 (No Content) and no response body
