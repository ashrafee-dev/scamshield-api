
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _find_call(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == name:
                return node
    raise AssertionError(f"{name}() call not found")


def _kw(call, key):
    for kw in call.keywords:
        if kw.arg == key:
            return ast.literal_eval(kw.value)
    raise AssertionError(f"keyword {key!r} not found")


def _route_decorators(tree):
    found = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for deco in node.decorator_list:
                if not isinstance(deco, ast.Call) or not isinstance(deco.func, ast.Attribute):
                    continue
                if not isinstance(deco.func.value, ast.Name) or deco.func.value.id != "router":
                    continue
                if not deco.args:
                    continue
                path = ast.literal_eval(deco.args[0])
                found[path] = (node, deco)
    return found


def test_fastapi_app_metadata_is_documented():
    tree = ast.parse((ROOT / "app/main.py").read_text())
    app_call = _find_call(tree, "FastAPI")

    assert _kw(app_call, "title") == "ScamShield API"
    assert "email" in _kw(app_call, "description").lower()
    assert "audio" in _kw(app_call, "description").lower()


def test_http_routes_have_openapi_summaries_and_error_responses():
    tree = ast.parse((ROOT / "app/api/analyze.py").read_text())
    routes = _route_decorators(tree)

    email = routes["/email"][1]
    assert "scam" in _kw(email, "summary").lower()
    email_responses = _kw(email, "responses")
    assert 429 in email_responses

    audio = routes["/audio"][1]
    assert "audio" in _kw(audio, "summary").lower()
    audio_responses = _kw(audio, "responses")
    assert {413, 415, 429}.issubset(audio_responses)


def test_websocket_route_has_a_clear_docstring():
    tree = ast.parse((ROOT / "app/api/analyze.py").read_text())
    routes = _route_decorators(tree)
    websocket_node = routes["/ws"][0]
    doc = ast.get_docstring(websocket_node) or ""

    assert "audio" in doc.lower()
    assert "websocket" in doc.lower()
