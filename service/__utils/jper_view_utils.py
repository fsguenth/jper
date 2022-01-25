from flask import request
from octopus.core import app


def get_req_page_num() -> int:
    page_num = int(request.values.get("page", app.config.get("DEFAULT_LIST_PAGE_START", 1)))
    return page_num
