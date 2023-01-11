# coding:utf-8

# Method：

# 三种分词模式
# jieba.cut("str")——默认是精确模式
# jieba.cut("str", cut_all=True)——全模式
# jieba.cut_for_search("str")——搜索引擎模式

# 词性标注
# pseg.cut(str)
# 词性标注tips：
# a:形容词 b:区别词（例：男、女、高级、中级） c:连词（例：且、及） d:副词  f:方位词（例：北） h:前缀 k:后缀 i:成语 j:简称（例：中、英、法） l:习语词（例：有期徒刑）
# m:数词（例：2021、六个月、七十二条） n:名词 o:拟声词 p:介词 q:量词 r:代词 s:处所词 t:时间词 u:助词 v:动词 x:标点符号 y:语气词 z:状态词

# 提取关键词
# jieba.analyse.extract_tags(str,topK,withWeight,allowPOS)——四个参数分别代表待提取的文本、提取关键词数量K（默认20）、提取关键词的权重、筛选指定词性
# jieba.analyse.textrank(str,topK,withWeight,allowPOS)

# 导入用户词典来提高分词精确率
# jieba.load_userdict("user.dict/txt")——参数为文件名

import jieba.posseg as pseg
import jieba
import json
import sys
import io


#保证后端得到的数据为utf-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.detach(),encoding="utf-8")

jieba.load_userdict("user.txt") # 经过大量数据测试后得出的该类型文件下容易出现分词不当的词汇 用户在检验结果时也可以向其中加入新的词汇 格式为：词汇 词性（例：犯罪 v）

def open_file(file_name):  # 此函数用于打开文件 用户需传入所需分词的文件名/地址 返回值为整个文件的字符串形式
    with open(file_name,'r') as file:
        text = '' # 用于储存整个文件字符串
        for line in file:
            line = ''.join(line.split())  # 去除文件每行中的空格
            text = text + line
        return text


def divide_words(text,file_name):  # 此函数用于处理文本字符串从而完成分词 传入参数为文本字符串以及文本名称 运行此函数会创建一个带有分词结果的json文件
    temp_noun = [] # 用于储存初步分词名词的列表
    temp_verb = [] # 用于储存初步分词动词的列表
    temp_adj = [] # 用于储存初步分词后形容词的列表
    list = pseg.lcut(text)  # 定义一个初步词性标注后以pair为元素的列表list
    #print(list)  # 便于用户检查词性进行人工筛选
    for i in list:
        noun_dict = {}
        verb_dict = {}
        adj_dict = {}
        if((i.flag == 'ns' or i.flag == 'nr' or i.flag == 'nt' or i.flag == 'nz'
                 or i.word == '某某') and (len(i.word) > 1) ):
           noun_dict[i.word] = i.flag
           temp_noun.append(noun_dict)
        if i.word == '男' or i .word == '女' or i.word == '中级' or i.word == '高级': # 对某些本次数据分析所需的词进行特判
            noun_dict[i.word] = i.flag
            temp_noun.append(noun_dict)
        if(i.flag.startswith('v')):
            verb_dict[i.word] = i.flag
            temp_verb.append(verb_dict)
        if(i.flag == 'a' or i.flag == 'ad'):
            adj_dict[i.word] = i.flag
            temp_adj.append(adj_dict)

    # 检索列表来合并系统分词无法准确区别（存在歧义）的词汇
    merge_place(temp_noun) # 合并不同地级的地区名词
    merge_name(temp_noun) # 合并未知的人名（例：X/某某）
    # 特殊词汇的合并
    merge_words(temp_noun,'人民法院','ns')
    merge_words(temp_noun,'人民检察院','ns')
    merge_words(temp_noun, '高级人民法院', 'ns')

    noun = [] # 用于储存名词最终分词结果的列表
    verb = [] # 用于储存动词最终分词结果的列表
    adj = [] # 用于储存形容词最终分词结果的列表

    # 字典转列表并进行去重
    dict_to_list(temp_noun,noun)
    dict_to_list(temp_verb,verb)
    dict_to_list(temp_adj,adj)

    # 地名的二次去重
    double_noun = []
    for i in noun:
        double_noun.append(i)  # 复制一份原列表
    for i in range(len(noun)):
        for j in range(len(double_noun)):
            if noun[i] in double_noun[j] and noun[i]!= double_noun[j] and len(noun[i]) < 6 and noun[i] != '男' and noun[i] != '女':
                noun[i] = ''

    final_noun = [] # 存储名词分词结果的最终列表
    for i in noun:
        if i != '' and \
                (i != '被告人' and i != '罪犯' and i != '检察官' and i != '监狱长' and i != '审判长' and i != '审判员'
                 and i != '书记员' and i != '刑期' and i != '服刑' and i != '刑罚' and i != '资料' and i != '审批表'
                 and i != '法定条件' and i != '证据' and i != '法律法规' and i != '刑事判决' and i != '政治权利' and i != '公诉机关'
                 and i != '法律效力' and i != '检察机关' and i != '案件' and i != '意见' and i != '规定' and i != '上述事实'):
            final_noun.append(i)   # 删除某些不重要的名词来进一步精简列表 用户可自行加入筛选需要过滤的词


    final_verb = [] # 用于存储动词分词结果的最终列表
    for i in verb:
        if len(i)>1 :
            final_verb.append(i)

    res = []  # 定义一个结果列表来储存所有分词结果
    res.append(final_noun)
    res.append(final_verb)
    res.append(adj)

    #将结果直接输出到控制台
    print(res)

    # 将最终获得的结果列表储存到json文件中
    # f_name = file_name+'分词结果.json'
    # with open(f_name,'w') as file:
    #     json.dump(res,file)
    # with open(f_name,'r') as file:
    #     print(json.load(file))  # 便于用户检查最终分词结果 结果以名词、动词、形容词的顺序分别存储在三个列表中 再将三个列表存储在结果列表中显示

# 上述函数中用到的嵌套函数
def merge_place(list):  #此函数用于合并不同地级的地区名词
    for i in range(len(list)):  # 遍历整个词表
        for o,j in list[i].items():
            temp_num = i
            if j == 'ns' and '省' not in o:  # 判断该元素是否为地名且非最高级别'省'
                new_key = o
                flag = True
                cnt = 0
                while (flag):
                    for k, m in list[temp_num - 1].items():
                        if m == 'ns' and temp_num > 0 and k not in new_key:
                            # 通过前一个词的词性判断是否前缀为地名 若是则将多级别地名合并 （例：江苏省/无锡市）
                            new_key = k + new_key
                            temp_num = temp_num - 1
                            cnt = cnt + 1
                        else:
                            flag = False
                        if cnt >= 3:
                            flag = False
                        if '省' in k:
                            flag = False
                if new_key != '':
                    new_dict = {new_key: 'ns'}
                    list.append(new_dict)  # 将最终合并的结果加入到原词表中

def merge_name(list):  # 此函数用于合并姓氏与'某某'被分开的情况（由于系统自动分词无法将姓氏和'某某'合并）
    for i in range(len(list)):  # 遍历整个词表
        for j in list[i].keys():
            if j == '某某':
                new_key = '某某'
                for k,v in list[i-1].items():
                    if(v=='nr' and len(k) == 1):
                        new_key = k + new_key
                if new_key != '某某':
                    new_dict = {new_key: 'nr'}
                    list.append(new_dict)  # 将最终合并的结果加入到原词表

def merge_words(list,key_word,word_attribute):  # 此函数用于合并某些由于系统自动分词而被错误分开来的专有名词（例：X省/X市/人民法院）
    for i in range(len(list)):  # 遍历整个词表
        for j in list[i].keys():
            if key_word in j:
                flag = True
                temp_num = i
                new_key = key_word
                cnt = 0
                while (flag):
                    for k,v in list[temp_num - 1].items():
                        if (v == word_attribute or v == 'b') and temp_num > 0 and k not in new_key:
                            # 通过前一个词的词性判断是否前缀为地名 若是则将地名与法院名合并
                                    new_key = k + new_key
                                    temp_num = temp_num - 1
                                    cnt = cnt + 1
                        else:
                            flag = False
                    if cnt >= 3 :
                        flag = False
                    if '省' in k:
                        flag = False
                if new_key != key_word:
                    new_dict = {new_key: word_attribute}
                    list.append(new_dict)  # 将最终合并的结果加入到原词表中

def dict_to_list(old_list,new_list):  # 此函数用于取出旧列表中的字典元素中的key值储存到结果列表中并可自动实现列表去重
    for i in old_list:
        for j in i.keys():
            if j not in new_list:
                new_list.append(j)

divide_words(sys.argv[1],'标注')


# 此处需要用户在第二个参数上自行删除文件地址的格式后缀以防止出现json文件格式错误
# 此函数打印的两行结果分别为初步分词后的结果以及文件最终被划分为名词、动词、形容词三大词性后的结果

