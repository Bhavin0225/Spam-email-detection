from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import jwt
from app.core.security import decode_token
from app.database.crud import get_user_by_email, write_audit_log

class AuditLoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware that intercepts requests and writes access records to the system_logs collection
    for critical actions, authentication flows, administrative operations, and client/server errors.
    """
    async def dispatch(self, request: Request, call_next):
        # Resolve client IP
        ip_address = request.client.host if request.client else None

        # Check for authentication token to link log record to a user
        user_id = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = decode_token(token)
                email = payload.get("sub")
                if email:
                    user = get_user_by_email(email)
                    if user:
                        user_id = user.get("user_id")
            except Exception:
                pass  # Ignore invalid signatures; let route dependencies handle authentication

        # Process the request
        response = await call_next(request)

        # Skip logging documentation assets and health probes
        path = request.url.path
        if path in ("/docs", "/openapi.json", "/health", "/"):
            return response

        status_code = response.status_code

        # Log errors, auth changes, admin routes, predictions, and feedbacks
        is_sensitive = (
            "auth" in path
            or "admin" in path
            or "predict" in path
            or "feedback" in path
            or status_code >= 400
        )

        if is_sensitive:
            # Determine severity based on HTTP response status code
            severity = "info"
            if status_code >= 500:
                severity = "critical"
            elif status_code >= 400:
                severity = "warning"

            # Determine event classification
            event_type = "system"
            if "signup" in path:
                event_type = "signup"
            elif "login" in path:
                event_type = "login"
            elif "admin" in path:
                event_type = "role_change" if "role" in path else "system"
            elif "predict" in path:
                event_type = "prediction"
            elif "feedback" in path:
                event_type = "feedback"
            elif status_code >= 400:
                event_type = "error"

            details = {
                "method": request.method,
                "path": path,
                "status_code": status_code,
            }
            request_id = request.headers.get("X-Request-ID")

            # Write the log to system_logs defensively
            write_audit_log(
                event_type=event_type,
                details=details,
                user_id=user_id,
                ip_address=ip_address,
                severity=severity,
                request_id=request_id
            )

        return response
