import time
import uuid
import logging

from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        correlation_id = request.headers.get('x-correlation-id', str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        started = time.perf_counter()

        response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        response.headers['x-correlation-id'] = correlation_id

        logger.info(
            'request_completed method=%s path=%s status_code=%s elapsed_ms=%s',
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
            extra={'correlation_id': correlation_id},
        )
        return response
