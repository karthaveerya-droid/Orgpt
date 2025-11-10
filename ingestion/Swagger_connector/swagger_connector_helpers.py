"""
swagger_connector_helpers.py
-----------------------------
Core parsing utilities for Orgpt Swagger ingestion.
Extracts:
- Endpoints (method, path, summary, description)
- Parameters (query, path, header, cookie)
- Request bodies
- Responses (codes, schemas, examples)
- Auth schemes, components, and servers
"""

import requests
import json
import yaml
from typing import Any, Dict, List

# ---------- Fetch & Utilities ----------

def fetch_swagger(source: str) -> Dict[str, Any]:
    """Fetch Swagger JSON or YAML from URL or local file."""
    if source.startswith("http://") or source.startswith("https://"):
        resp = requests.get(source)
        resp.raise_for_status()
        text = resp.text
    else:
        with open(source, "r", encoding="utf-8") as f:
            text = f.read()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = yaml.safe_load(text)

    return data


def resolve_ref(ref: str, root: Dict[str, Any]) -> Any:
    """Resolve a $ref pointer in Swagger JSON."""
    parts = ref.lstrip("#/").split("/")
    node = root
    for p in parts:
        node = node.get(p)
        if node is None:
            return None
    return node


# ---------- Extractors ----------

def extract_parameters(param_list: List[Dict[str, Any]], root: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract detailed parameter info."""
    results = []
    for p in param_list or []:
        if "$ref" in p:
            p = resolve_ref(p["$ref"], root) or {}
        param = {
            "name": p.get("name"),
            "in": p.get("in"),
            "required": p.get("required", False),
            "description": p.get("description"),
            "schema": p.get("schema"),
            "example": p.get("example")
        }
        results.append(param)
    return results


def extract_request_body(rb: Dict[str, Any], root: Dict[str, Any]) -> Dict[str, Any]:
    """Extract request body info including schema and examples."""
    if not rb:
        return {}
    if "$ref" in rb:
        rb = resolve_ref(rb["$ref"], root) or {}

    content = rb.get("content", {})
    out = {}
    for mime, body in content.items():
        schema = body.get("schema")
        if schema and "$ref" in schema:
            schema = resolve_ref(schema["$ref"], root)
        out[mime] = {
            "schema": schema,
            "example": body.get("example"),
        }
    return out


def extract_responses(responses: Dict[str, Any], root: Dict[str, Any]) -> Dict[str, Any]:
    """Extract all response codes, descriptions, schemas, and examples."""
    result = {}
    for code, resp in (responses or {}).items():
        if "$ref" in resp:
            resp = resolve_ref(resp["$ref"], root) or {}
        content = resp.get("content", {})
        code_entry = {
            "description": resp.get("description"),
            "headers": resp.get("headers", {}),
            "content": {},
        }
        for mime, c in content.items():
            schema = c.get("schema")
            if schema and "$ref" in schema:
                schema = resolve_ref(schema["$ref"], root)
            code_entry["content"][mime] = {
                "schema": schema,
                "example": c.get("example"),
            }
        result[code] = code_entry
    return result


def extract_security(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Extract authentication / security schemes."""
    security_schemes = spec.get("components", {}).get("securitySchemes", {})
    result = {}
    for name, scheme in security_schemes.items():
        result[name] = {
            "type": scheme.get("type"),
            "description": scheme.get("description"),
            "in": scheme.get("in"),
            "name": scheme.get("name"),
            "flows": scheme.get("flows"),
        }
    return result


# ---------- Main Extraction ----------

def extract_full_api_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Extract all relevant data from a Swagger spec into a normalized structure."""
    api_info = {
        "title": spec.get("info", {}).get("title"),
        "version": spec.get("info", {}).get("version"),
        "description": spec.get("info", {}).get("description"),
        "servers": spec.get("servers", []),
        "security": extract_security(spec),
        "paths": [],
        "components": spec.get("components", {}),
    }

    for path, methods in (spec.get("paths") or {}).items():
        for method, op in methods.items():
            if method.lower() not in ["get", "post", "put", "delete", "patch", "options", "head"]:
                continue

            # Combine path-level + operation-level params
            params = []
            if "parameters" in methods:
                params.extend(extract_parameters(methods["parameters"], spec))
            if "parameters" in op:
                params.extend(extract_parameters(op["parameters"], spec))

            entry = {
                "method": method.upper(),
                "path": path,
                "summary": op.get("summary"),
                "description": op.get("description"),
                "operationId": op.get("operationId"),
                "parameters": params,
                "requestBody": extract_request_body(op.get("requestBody"), spec),
                "responses": extract_responses(op.get("responses"), spec),
                "tags": op.get("tags", []),
                "deprecated": op.get("deprecated", False),
            }
            api_info["paths"].append(entry)
    return api_info


def render_api_to_text(api_info: Dict[str, Any]) -> List[str]:
    """Convert structured API info into natural-language paragraphs for embedding."""
    docs = []
    for ep in api_info["paths"]:
        text = f"{ep['method']} {ep['path']}: {ep.get('summary','')}\n"
        if ep.get("description"):
            text += f"Description: {ep['description']}\n"
        if ep.get("parameters"):
            for p in ep["parameters"]:
                text += f"- Param {p['name']} ({p['in']}): {p.get('description','')} Required={p['required']}\n"
        if ep.get("requestBody"):
            text += f"Request Body: {list(ep['requestBody'].keys())}\n"
        if ep.get("responses"):
            text += f"Responses: {list(ep['responses'].keys())}\n"
        docs.append(text.strip())
    return docs
