import datetime
import hashlib
import logging
import os
import random
import re
import string
import time
from itertools import zip_longest

import faker
import requests

import yaml


def generate_mobile():
    # 第二位数字
    second = random.randint(3, 9)
    # 第三位 到 第十一位数字, 共九位
    suffix = random.randrange(100000000, 1000000000)
    # 拼接手机号
    return "1{}{}".format(second, suffix)


def random_num(start, stop, step=1, isfloat=False):
    if not isfloat:
        res = random.randrange(int(start), int(stop), int(step))
        return str(res)
    else:
        res = random.uniform(float(start), float(stop))
        return '%.2f' % res


def random_str(num=10):
    """
    完全随机数字、汉字、英文、特殊字符
    """
    a = random.randrange(num)
    b = random.randrange(num - a)
    c = random.randrange(num - a - b)
    d = num - a - b - c
    zh = [GBK2312() for _ in range(a)]
    en = [generate_english() for _ in range(b)]
    figure = [str(i) for i in range(c)]
    special = [generate_special() for _ in range(d)]
    str_list = zh + en + figure + special
    random.shuffle(str_list)
    str_ = "".join(str_list)
    return str_


def random_words(num=2, limit=None):
    """
    随机中文+英文 词语
    """
    limit = int(limit)
    keys = ['company', 'name', 'address', 'user_name']
    str_ = "".join([getattr(faker_data(), random.choice(keys))() for _ in range(num)])
    if not limit:
        return str_
    else:
        return str_[:limit]


def GBK2312():
    """
    生成常见单个汉字
    GBK2312收录了6千多常用汉字
    """
    while True:
        head = random.randint(0xb0, 0xf7)
        body = random.randint(0xa1, 0xfe)
        val = f'{head:x}{body:x}'
        if val[2:] not in ('fa', 'fb', 'fc', 'fd', 'fe'):  #:D7FA-D7FE)
            break
    str_ = bytes.fromhex(val).decode('gb2312')
    return str_


def generate_english():
    """
    生成单个英文字母
    """
    return random.choice(string.ascii_letters)


def generate_special():
    """
    随机生成单个特殊字符
    @return:
    """
    str_ = "!@#$%^&*()_+！@#￥%……&*（）——+[];,./【】、；‘，。、"
    res = random.choice(str_)
    return res


def faker_data(type_='name'):
    """
    https://faker.readthedocs.io/en/master/providers/faker.providers.person.html
    """
    f = faker.Faker(['en_US', 'zh-CN'])
    data = getattr(f, type_)()
    return data.replace(' ', '')


def is_json_equal(src, rest):
    """
    判断json相等
    src
    @return:
    """
    flag = 0
    msg = ''
    try:
        if isinstance(src, list) and isinstance(rest, list):
            # for i, j in zip(src, rest):
            #     if isinstance(i, (dict, list)):
            #         if is_json_equal(i, j):
            #             continue
            #         else:
            #             flag = 1
            #             return False
            #     elif i != j:
            #         flag = 2
            #         return False
            #     elif i == j:  # 考虑到当前情况下，数组内只有字典
            #         continue
            #     else:
            #         flag = 3
            #         return False
            t = list(src)  # make a mutable copy
            try:
                for elem in rest:
                    t.remove(elem)
            except ValueError:
                flag = 10
                msg = '\n|--src       %s\n|--rest      %s\n|--wrong key %s' % (src, rest, elem)
                return False
            return not t
        elif isinstance(src, dict) and isinstance(rest, dict):
            if len(src) != len(rest):
                flag = 8
                diff = set(src.keys()) ^ set(rest.keys())
                msg = '长度不一致 %s' % diff
                return False
            elif set(src.keys()) != set(rest.keys()):
                flag = 9
                diff = set(src.keys()) ^ set(rest.keys())
                msg = 'key 不一致 %s' % diff
                return False
            for (ik, iv), (jk, jv) in zip_longest(sorted(src.items(), key=lambda x: x[0]),
                                                  sorted(rest.items(), key=lambda x: x[0])):
                if isinstance(iv, (list, dict)) and isinstance(jv, (list, dict)):
                    if is_json_equal(iv, jv):
                        continue
                    else:
                        flag = 4
                        return False
                elif ik == jk:
                    if str(iv) == str(jv):
                        continue
                    else:
                        try:
                            if float(iv) == float(jv):
                                continue
                            else:
                                msg = '\n|---%s %s\n|---%s %s\n|---src %s\n|---rest %s' % (ik, iv, jk, jv, src, rest)
                                flag = 8
                                return False
                        except:
                            msg = '\n|---%s %s\n|---%s %s\n|---src %s\n|---rest %s' % (ik, iv, jk, jv, src, rest)
                            flag = 9
                            return False
                else:
                    msg = '\n|---%s %s\n|---%s %s\n|---src %s\n|---rest %s' % (ik, iv, jk, jv, src, rest)
                    flag = 5
                    return False
        elif isinstance(src, str) and isinstance(rest, str):
            if src != rest:
                flag = 6
                return False
        else:
            flag = 7
            return False
        return True
    except Exception as e:
        logging.error(e)
        return False
    finally:
        # logging.warning('-----\n%s\n%s' % (src,rest))
        if flag:
            logging.warning('--%s' % (flag))
        if msg:
            logging.warning('%s' % (msg))
        pass


def turn_num(json_):
    if isinstance(json_, list):
        for item in json_:
            turn_num(item)
    elif isinstance(json_, dict):
        for key, value in json_.copy().items():
            if isinstance(value, (list, dict)):
                turn_num(value)
            elif isinstance(value, str):
                if "." in value:
                    try:
                        json_[key] = float(value)
                    except:
                        pass
                else:
                    try:
                        json_[key] = int(value)
                    except:
                        pass
    elif isinstance(json_, str):
        if "." in json_:
            try:
                json_ = float(json_)
            except:
                pass
        else:
            try:
                json_ = int(json_)
            except:
                pass
    else:
        pass
    return json_


def str_to_timestamp(timestr, format):
    timestr = str(timestr) if not isinstance(timestr, str) else timestr
    date = datetime.datetime.strptime(timestr, format)
    timestamp = time.mktime(date.timetuple())
    return timestamp


def timestamp_to_str(timestamp, format):
    t = time.localtime(timestamp)
    return time.strftime(format, t)


def get_timestamp_ms():
    time_ = round(time.time() * 1000)
    return str(time_)


def md5(str_):
    # 创建md5对象
    hl = hashlib.md5()
    hl.update(str_.encode(encoding='utf-8'))
    return hl.hexdigest()


def read_yaml(path):
    with open(path, encoding='utf-8') as f:
        try:
            content = yaml.load(f, Loader=yaml.FullLoader)
            return content
        except Exception:
            raise RuntimeError('yaml 文件格式错误')


def assert_recursive(result, assert_):
    for key, value in assert_.items():
        if isinstance(value, dict):
            assert_recursive(result[key], value)
        else:
            assert result[key] == value, result


def get_root_path():
    return os.path.abspath(os.path.join(__file__, '../'))


if __name__ == '__main__':
    x = random_num(1.0, 10.0, isfloat=True) + random_num(1, 5, isfloat=True)
    print(x)
