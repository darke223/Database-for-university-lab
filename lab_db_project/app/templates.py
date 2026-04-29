from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

def format_json_filter(data):
    import json
    if not data:
        return "—"
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except:
            return data
    if isinstance(data, dict):
        return ", ".join([f"{k}: {v}" for k, v in data.items()])
    return str(data)

templates.env.filters["format_json"] = format_json_filter
