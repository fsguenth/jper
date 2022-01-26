from io import TextIOWrapper

from flask import request

from octopus.core import app
from service import models


def get_req_page_num() -> int:
    page_num = int(request.values.get("page", app.config.get("DEFAULT_LIST_PAGE_START", 1)))
    return page_num


def set_repo_config_by_req_files(rec: models.RepositoryConfig, repo: str, encoding='utf-8') -> bool:
    saved = None
    io_wrapper = TextIOWrapper(request.files['file'], encoding=encoding)
    if request.files['file'].filename.endswith('.csv'):
        saved = rec.set_repo_config(csvfile=io_wrapper, repository=repo)
    elif request.files['file'].filename.endswith('.txt'):
        saved = rec.set_repo_config(textfile=io_wrapper, repository=repo)
    return saved
