"""FastAPI entry point for the POS receipt API."""
import os
from io import BytesIO

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from bootstrap import tao_web


def create_app(dsn):
    app = FastAPI(title="MI4090 POS API")
    receipts = tao_web(dsn)

    def dispatch(request, account, body):
        # The existing receipt handler owns validation, transactions and error mapping.
        env = {
            "PATH_INFO": request.url.path,
            "REQUEST_METHOD": "POST",
            "REMOTE_USER": account,
            "CONTENT_TYPE": request.headers.get("content-type", ""),
            "CONTENT_LENGTH": str(len(body)),
            "HTTP_IDEMPOTENCY_KEY": request.headers.get("idempotency-key"),
            "wsgi.input": BytesIO(body),
        }
        metadata = {}

        def start_response(status, headers):
            metadata.update(status_code=int(status.split()[0]), headers=dict(headers))

        content = b"".join(receipts(env, start_response))
        return Response(content, **metadata)

    async def receipt(request: Request):
        account = getattr(request.state, "ma_tk", None)
        if not account:
            return JSONResponse({"loi": "Cần đăng nhập"}, status_code=401)
        if request.headers.get("content-type", "").split(";")[0].strip() != "application/json":
            return JSONResponse({"loi": "Cần application/json"}, status_code=415)
        body = bytearray()
        async for chunk in request.stream():
            if len(body) + len(chunk) > 1024 * 1024:
                return JSONResponse({"loi": "Kích thước yêu cầu quá lớn"}, status_code=413)
            body.extend(chunk)
        return await run_in_threadpool(dispatch, request, account, body)

    for path, title, is_return in [
        ("/api/ban", "Lập phiếu bán", False),
        ("/api/tra", "Lập phiếu trả", True),
    ]:
        line = [{"type": "string"}, {"type": "integer", "minimum": 1}]
        fields = {"ca": {"type": "string"}, "pt": {"enum": ["TM", "CK"]}}
        if is_return:
            fields["goc"] = {"type": "string"}
            line.append({"enum": ["TOT", "HONG"]})
        fields["dong"] = {"type": "array", "minItems": 1, "items": {
            "type": "array", "prefixItems": line, "minItems": len(line), "maxItems": len(line),
        }}
        schema = {"type": "object", "properties": fields,
                  "required": list(fields), "additionalProperties": False}
        app.add_api_route(path, receipt, methods=["POST"], summary=title, status_code=201,
                          responses={200: {"description": "Phiếu đã ghi trước đó"}},
                          openapi_extra={
                              "parameters": [{"name": "Idempotency-Key", "in": "header",
                                              "required": True, "schema": {"type": "string"}}],
                              "requestBody": {"required": True, "content": {
                                  "application/json": {"schema": schema}}},
                          })
    return app


def application():
    return create_app(os.environ["DATABASE_URL"])
