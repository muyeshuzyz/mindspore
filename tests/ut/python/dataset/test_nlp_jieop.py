# Copyright 2020 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import numpy as np
import mindspore.dataset as ds
from mindspore.dataset.transforms.text.c_transforms import JiebaTokenizer
from mindspore.dataset.transforms.text.utils import JiebaMode, as_text

DATA_FILE = "../data/dataset/testJiebaDataset/3.txt"
DATA_ALL_FILE = "../data/dataset/testJiebaDataset/*"

HMM_FILE = "../data/dataset/jiebadict/hmm_model.utf8"
MP_FILE = "../data/dataset/jiebadict/jieba.dict.utf8"


def test_jieba_1():
    """Test jieba tokenizer with MP mode"""
    data = ds.TextFileDataset(DATA_FILE)
    jieba_op = JiebaTokenizer(HMM_FILE, MP_FILE, mode=JiebaMode.MP)
    data = data.map(input_columns=["text"],
                    operations=jieba_op, num_parallel_workers=1)
    expect = ['今天天气', '太好了', '我们', '一起', '去', '外面', '玩吧']
    ret = []
    for i in data.create_dict_iterator():
        ret = as_text(i["text"])
        for index, item in enumerate(ret):
            assert item == expect[index]


def test_jieba_1_1():
    """Test jieba tokenizer with HMM mode"""
    data = ds.TextFileDataset(DATA_FILE)
    jieba_op = JiebaTokenizer(HMM_FILE, MP_FILE, mode=JiebaMode.HMM)
    data = data.map(input_columns=["text"],
                    operations=jieba_op, num_parallel_workers=1)
    expect = ['今天', '天气', '太', '好', '了', '我们', '一起', '去', '外面', '玩', '吧']
    for i in data.create_dict_iterator():
        ret = as_text(i["text"])
        for index, item in enumerate(ret):
            assert item == expect[index]


def test_jieba_1_2():
    """Test jieba tokenizer with HMM MIX"""
    data = ds.TextFileDataset(DATA_FILE)
    jieba_op = JiebaTokenizer(HMM_FILE, MP_FILE, mode=JiebaMode.MIX)
    data = data.map(input_columns=["text"],
                    operations=jieba_op, num_parallel_workers=1)
    expect = ['今天天气', '太好了', '我们', '一起', '去', '外面', '玩吧']
    for i in data.create_dict_iterator():
        ret = as_text(i["text"])
        for index, item in enumerate(ret):
            assert item == expect[index]


def test_jieba_2():
    """Test add_word"""
    DATA_FILE4 = "../data/dataset/testJiebaDataset/4.txt"
    data = ds.TextFileDataset(DATA_FILE4)
    jieba_op = JiebaTokenizer(HMM_FILE, MP_FILE, mode=JiebaMode.MP)
    jieba_op.add_word("男默女泪")
    expect = ['男默女泪', '市', '长江大桥']
    data = data.map(input_columns=["text"],
                    operations=jieba_op, num_parallel_workers=2)
    for i in data.create_dict_iterator():
        ret = as_text(i["text"])
        for index, item in enumerate(ret):
            assert item == expect[index]


def test_jieba_2_1():
    """Test add_word with freq"""
    DATA_FILE4 = "../data/dataset/testJiebaDataset/4.txt"
    data = ds.TextFileDataset(DATA_FILE4)
    jieba_op = JiebaTokenizer(HMM_FILE, MP_FILE, mode=JiebaMode.MP)
    jieba_op.add_word("男默女泪", 10)
    data = data.map(input_columns=["text"],
                    operations=jieba_op, num_parallel_workers=2)
    expect = ['男默女泪', '市', '长江大桥']
    for i in data.create_dict_iterator():
        ret = as_text(i["text"])
        for index, item in enumerate(ret):
            assert item == expect[index]


def test_jieba_2_2():
    """Test add_word with invalid None Input"""
    jieba_op = JiebaTokenizer(HMM_FILE, MP_FILE, mode=JiebaMode.MP)
    try:
        jieba_op.add_word(None)
    except ValueError:
        pass


def test_jieba_2_3():
    """Test add_word with freq, the value of freq affects the result of segmentation"""
    DATA_FILE4 = "../data/dataset/testJiebaDataset/6.txt"
    data = ds.TextFileDataset(DATA_FILE4)
    jieba_op = JiebaTokenizer(HMM_FILE, MP_FILE, mode=JiebaMode.MP)
    jieba_op.add_word("江大桥", 20000)
    data = data.map(input_columns=["text"],
                    operations=jieba_op, num_parallel_workers=2)
    expect = ['江州', '市长', '江大桥', '参加', '了', '长江大桥', '的', '通车', '仪式']
    for i in data.create_dict_iterator():
        ret = as_text(i["text"])
        for index, item in enumerate(ret):
            assert item == expect[index]


def test_jieba_3():
    """Test add_dict with dict"""
    DATA_FILE4 = "../data/dataset/testJiebaDataset/4.txt"
    user_dict = {
        "男默女泪": 10
    }
    data = ds.TextFileDataset(DATA_FILE4)
    jieba_op = JiebaTokenizer(HMM_FILE, MP_FILE, mode=JiebaMode.MP)
    jieba_op.add_dict(user_dict)
    data = data.map(input_columns=["text"],
                    operations=jieba_op, num_parallel_workers=1)
    expect = ['男默女泪', '市', '长江大桥']
    for i in data.create_dict_iterator():
        ret = as_text(i["text"])
        for index, item in enumerate(ret):
            assert item == expect[index]


def test_jieba_3_1():
    """Test add_dict with dict"""
    DATA_FILE4 = "../data/dataset/testJiebaDataset/4.txt"
    user_dict = {
        "男默女泪": 10,
        "江大桥": 20000
    }
    data = ds.TextFileDataset(DATA_FILE4)
    jieba_op = JiebaTokenizer(HMM_FILE, MP_FILE, mode=JiebaMode.MP)
    jieba_op.add_dict(user_dict)
    data = data.map(input_columns=["text"],
                    operations=jieba_op, num_parallel_workers=1)
    expect = ['男默女泪', '市长', '江大桥']
    for i in data.create_dict_iterator():
        ret = as_text(i["text"])
        for index, item in enumerate(ret):
            assert item == expect[index]


def test_jieba_4():
    DATA_FILE4 = "../data/dataset/testJiebaDataset/3.txt"
    DICT_FILE = "../data/dataset/testJiebaDataset/user_dict.txt"

    data = ds.TextFileDataset(DATA_FILE4)
    jieba_op = JiebaTokenizer(HMM_FILE, MP_FILE, mode=JiebaMode.MP)
    jieba_op.add_dict(DICT_FILE)
    data = data.map(input_columns=["text"],
                    operations=jieba_op, num_parallel_workers=1)
    expect = ['今天天气', '太好了', '我们', '一起', '去', '外面', '玩吧']
    for i in data.create_dict_iterator():
        ret = as_text(i["text"])
        for index, item in enumerate(ret):
            assert item == expect[index]


def test_jieba_4_1():
    """Test add dict with invalid file path"""
    DICT_FILE = ""
    jieba_op = JiebaTokenizer(HMM_FILE, MP_FILE, mode=JiebaMode.MP)
    try:
        jieba_op.add_dict(DICT_FILE)
    except ValueError:
        pass


def test_jieba_5():
    """Test add dict with file path"""
    DATA_FILE4 = "../data/dataset/testJiebaDataset/6.txt"

    data = ds.TextFileDataset(DATA_FILE4)
    jieba_op = JiebaTokenizer(HMM_FILE, MP_FILE, mode=JiebaMode.MP)
    jieba_op.add_word("江大桥", 20000)
    data = data.map(input_columns=["text"],
                    operations=jieba_op, num_parallel_workers=1)
    expect = ['江州', '市长', '江大桥', '参加', '了', '长江大桥', '的', '通车', '仪式']
    for i in data.create_dict_iterator():
        ret = as_text(i["text"])
        for index, item in enumerate(ret):
            assert item == expect[index]


def gen():
    text = np.array("今天天气太好了我们一起去外面玩吧".encode("UTF8"), dtype='S')
    yield text,


def pytoken_op(input_data):
    te = str(as_text(input_data))
    tokens = []
    tokens.append(te[:5].encode("UTF8"))
    tokens.append(te[5:10].encode("UTF8"))
    tokens.append(te[10:].encode("UTF8"))
    return np.array(tokens, dtype='S')


def test_jieba_6():
    data = ds.GeneratorDataset(gen, column_names=["text"])
    data = data.map(input_columns=["text"],
                    operations=pytoken_op, num_parallel_workers=1)
    expect = ['今天天气太', '好了我们一', '起去外面玩吧']
    for i in data.create_dict_iterator():
        ret = as_text(i["text"])
        for index, item in enumerate(ret):
            assert item == expect[index]


if __name__ == "__main__":
    test_jieba_1()
    test_jieba_1_1()
    test_jieba_1_2()
    test_jieba_2()
    test_jieba_2_1()
    test_jieba_2_2()
    test_jieba_3()
    test_jieba_3_1()
    test_jieba_4()
    test_jieba_4_1()
    test_jieba_5()
    test_jieba_5()
    test_jieba_6()
