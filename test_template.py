from common import get_root_path, read_yaml, is_json_equal
import os
import pytest
import json
import requests
import datetime
import pandas as pd
import re
from config import *
from model import add_all
from itertools import zip_longest

_records = []


def read_cases() -> list:
    path_dir = os.path.join(get_root_path(), 'cases')
    _cases = []
    _records = []
    for root, dirs, files in os.walk(path_dir):
        for file in files:
            if file.endswith(('.yaml', '.yml')):
                res = read_yaml(os.path.join(root, file))
                if isinstance(res, list):
                    _cases.extend(res)
                elif res is None:
                    continue
                else:
                    raise RuntimeError('yaml 用例和用例之间非数组关系')
    return _cases


def record(data: list):
    df = pd.DataFrame(data)
    df_list = df.to_dict('record')
    add_all(df_list)


def req(url, method, params, data: dict, headers):
    if method == 'get':
        res = requests.get(url, params=params, headers=headers)
    elif method == 'post':
        if data:
            for key, value in data.items():
                try:
                    if isinstance(value, (dict, list)):
                        data[key] = json.dumps(value, ensure_ascii=False)
                except:
                    pass
        res = requests.post(url, params=params, data=data, headers=headers)
    else:
        raise RuntimeError('仅支持[get, post] 方法')
    res_text = res.text
    rex = re.search(r"(\{.+\})", res_text)
    res_json_text = rex.group(1) if rex else "{}"
    # print('-----$',rex.groups())
    return res_json_text


@pytest.mark.parametrize('case', read_cases())
def test_case_one(case):
    if not isinstance(case, dict):
        raise RuntimeError('yaml单个用例里应该为字典(key: value)格式')
    actual_keys = set(case.keys())
    keys1 = {'desc', 'api', 'method'}
    if not actual_keys > keys1:
        raise RuntimeError('yaml 该用例缺少必要参数 %r \n %r' % (keys1 - (keys1 & actual_keys), case))
    params = case['params'] if 'params' in actual_keys else None
    data = case['data'] if 'data' in actual_keys else None
    headers = case['headers'] if 'headers' in actual_keys else None
    method = case['method']
    old_res = req(url=old_host + case['api'], method=method, params=params, data=data, headers=headers)
    new_res = req(url=new_host + case['api'], method=method, params=params, data=data, headers=headers)
    _records.append(dict(api=case['api'], old_res=old_res, new_res=new_res, desc=case['desc']))
    try:
        old_res_json = json.loads(old_res)
        new_res_json = json.loads(new_res)
        # 排除
        for old_key, new_key in zip_longest(old_res_json.copy(), new_res_json.copy(), fillvalue=''):
            if 'report_url' == old_key:
                old_res_json.pop('report_url')
            if 'report_url' == new_key:
                new_res_json.pop('report_url')
    except json.JSONDecodeError:
        assert False, '响应不是json'
    assert is_json_equal(old_res_json, new_res_json)


@pytest.fixture(scope='module', autouse=True)
def test_case():
    yield
    record(_records)


if __name__ == '__main__':
    read_cases()
