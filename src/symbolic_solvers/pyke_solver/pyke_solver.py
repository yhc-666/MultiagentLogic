import os
from pyke import knowledge_engine
import re

class Pyke_Program:
    """
    Main Functions:
    1. 解析包含谓词、事实、规则和查询的逻辑程序
    2. 将逻辑程序转换为Pyke引擎可理解的格式
    3. 执行推理并返回答案
    
    Supported datasets: ProntoQA, ProofWriter
    """
    
    def __init__(self, logic_program: str, dataset_name='ProntoQA') -> None:
        """
        初始化Pyke程序
        
        Args:
            logic_program (str): 包含逻辑程序的字符串，格式包含Predicates、Facts、Rules、Query等部分
            dataset_name (str): 数据集名称，支持'ProntoQA'和'ProofWriter'
        """
        self.logic_program = logic_program
        self.flag = self.parse_logic_program()  # 解析逻辑程序，返回是否成功
        self.dataset_name = dataset_name
        
        # 创建缓存目录用于保存Pyke程序文件
        cache_dir = os.path.join(os.path.dirname(__file__), '.cache_program')
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        self.cache_dir = cache_dir

        # 准备事实和规则文件
        try:
            self.create_fact_file(self.Facts)  # 创建事实文件(.kfb格式)
            self.create_rule_file(self.Rules)  # 创建规则文件(.krb格式)
            self.flag = True
        except:
            self.flag = False

        # 不同数据集的答案映射函数
        self.answer_map = {'ProntoQA': self.answer_map_prontoqa, 
                           'ProofWriter': self.answer_map_proofwriter}

    def parse_logic_program(self):
        """
        解析逻辑程序字符串，提取各个组件
        
        逻辑程序格式示例：
        Predicates: ... (谓词定义)
        Facts: ... (事实)
        Rules: ... (规则)
        Query: ... (查询)
        
        Returns:
            bool: 解析是否成功
        """
        keywords = ['Query:', 'Rules:', 'Facts:', 'Predicates:']
        program_str = self.logic_program
        
        # 逐个解析各个部分
        for keyword in keywords:
            try:
                program_str, segment_list = self._parse_segment(program_str, keyword)
                # 将解析结果设置为类属性（去掉冒号）
                setattr(self, keyword[:-1], segment_list)
            except:
                setattr(self, keyword[:-1], None)

        return self.validate_program()

    def _parse_segment(self, program_str, key_phrase):
        """
        解析程序中的特定段落
        
        Args:
            program_str (str): 程序字符串
            key_phrase (str): 关键短语（如'Facts:'）
            
        Returns:
            tuple: (剩余程序字符串, 解析出的段落列表)
        """
        remain_program_str, segment = program_str.split(key_phrase)
        segment_list = segment.strip().split('\n')
        
        # 清理每行，移除注释部分（:::后的内容）
        for i in range(len(segment_list)):
            segment_list[i] = segment_list[i].split(':::')[0].strip()
        return remain_program_str, segment_list

    def validate_program(self):
        """
        验证程序是否有效；如果无效，尝试修复
        
        Returns:
            bool: 程序是否有效
        """
        # 检查规则和事实是否存在且非空
        if not self.Rules is None and not self.Facts is None:
            if not self.Rules[0] == '' and not self.Facts[0] == '':
                return True
                
        # 尝试修复程序：重新分类规则和事实
        tmp_rules = []
        tmp_facts = []
        statements = self.Facts if self.Facts is not None else self.Rules
        if statements is None:
            return False
        
        # 根据是否包含'>>>'来区分规则和事实
        for fact in statements:
            if fact.find('>>>') >= 0:  # 包含'>>>'的是规则
                tmp_rules.append(fact)
            else:
                tmp_facts.append(fact)
        self.Rules = tmp_rules
        self.Facts = tmp_facts
        return False
    
    def create_fact_file(self, facts):
        """
        创建Pyke事实文件(.kfb格式)
        
        Args:
            facts (list): 事实列表
        """
        with open(os.path.join(self.cache_dir, 'facts.kfb'), 'w') as f:
            for fact in facts:
                # 过滤掉包含变量$x的无效事实
                if not fact.find('$x') >= 0:
                    f.write(fact + '\n')

    def create_rule_file(self, rules):
        """
        创建Pyke规则文件(.krb格式)
        
        Args:
            rules (list): 规则列表
        """
        pyke_rules = []
        for idx, rule in enumerate(rules):
            # 将每个规则转换为Pyke格式
            pyke_rules.append(self.parse_forward_rule(idx + 1, rule))

        with open(os.path.join(self.cache_dir, 'rules.krb'), 'w') as f:
            f.write('\n\n'.join(pyke_rules))

    def parse_forward_rule(self, f_index, rule):
        """
        解析前向推理规则，转换为Pyke格式
        
        示例规则: Furry($x, True) && Quite($x, True) >>> White($x, True)
        转换为Pyke的foreach-assert格式
        
        Args:
            f_index (int): 规则索引
            rule (str): 原始规则字符串
            
        Returns:
            str: Pyke格式的规则
        """
        premise, conclusion = rule.split('>>>')
        premise = premise.strip()
        
        # 将前提条件按'&&'分割成多个条件
        premise = premise.split('&&')
        premise_list = [p.strip() for p in premise]

        conclusion = conclusion.strip()
        # 将结论按'&&'分割成多个结论
        conclusion = conclusion.split('&&')
        conclusion_list = [c.strip() for c in conclusion]

        # 创建Pyke规则格式
        pyke_rule = f'''rule{f_index}\n\tforeach'''
        # 添加前提条件
        for p in premise_list:
            pyke_rule += f'''\n\t\tfacts.{p}'''
        pyke_rule += f'''\n\tassert'''
        # 添加结论
        for c in conclusion_list:
            pyke_rule += f'''\n\t\tfacts.{c}'''
        return pyke_rule
    
    def check_specific_predicate(self, subject_name, predicate_name, engine):
        """
        检查特定主体的特定谓词值
        
        示例: 检查Marvin是否来自火星
        Query: FromMars(Marvin, $label)
        
        Args:
            subject_name (str): 主体名称
            predicate_name (str): 谓词名称
            engine: Pyke推理引擎
            
        Returns:
            推理结果（True/False/None）
        """
        results = []
        
        # 在事实库中查找
        with engine.prove_goal(f'facts.{predicate_name}({subject_name}, $label)') as gen:
            for vars, plan in gen:
                results.append(vars['label'])

        # 在规则库中查找
        with engine.prove_goal(f'rules.{predicate_name}({subject_name}, $label)') as gen:
            for vars, plan in gen:
                results.append(vars['label'])

        # 处理结果
        if len(results) == 1:
            return results[0]
        elif len(results) == 2:
            return results[0] and results[1]
        elif len(results) == 0:
            return None

    def parse_query(self, query):
        """
        解析查询语句
        
        输入示例: Metallic(Wren, False)
        
        Args:
            query (str): 查询字符串
            
        Returns:
            tuple: (函数名, 参数1, 参数2的布尔值)
        """
        pattern = r'(\w+)\(([^,]+),\s*([^)]+)\)'
        match = re.match(pattern, query)
        if match:
            function_name = match.group(1)
            arg1 = match.group(2)
            arg2 = match.group(3)
            arg2 = True if arg2 == 'True' else False
            return function_name, arg1, arg2
        else:
            raise ValueError(f'Invalid query: {query}')

    def execute_program(self):
        """
        执行逻辑程序，进行推理
        
        Returns:
            tuple: (答案, 错误信息)
        """
        # 删除编译的krb目录，避免缓存问题
        complied_krb_dir = './models/compiled_krb'
        if os.path.exists(complied_krb_dir):
            print('removing compiled_krb')
            os.system(f'rm -rf {complied_krb_dir}/*')

        try:
            # 初始化Pyke推理引擎
            engine = knowledge_engine.engine(self.cache_dir)
            engine.reset()
            engine.activate('rules')  # 激活规则
            engine.get_kb('facts')    # 加载事实

            # 解析查询并执行推理
            predicate, subject, value_to_check = self.parse_query(self.Query[0])
            result = self.check_specific_predicate(subject, predicate, engine)
            
            # 根据数据集类型映射答案
            answer = self.answer_map[self.dataset_name](result, value_to_check)
        except Exception as e:
            return None, e
        
        return answer, ""

    def answer_mapping(self, answer):
        """答案映射函数（基础版本）"""
        return answer
        
    def answer_map_prontoqa(self, result, value_to_check):
        """
        ProntoQA数据集的答案映射
        
        Args:
            result: 推理结果
            value_to_check: 要检查的值
            
        Returns:
            str: 'A'（正确）或'B'（错误）
        """
        if result == value_to_check:
            return 'A'
        else:
            return 'B'

    def answer_map_proofwriter(self, result, value_to_check):
        """
        ProofWriter数据集的答案映射
        
        Args:
            result: 推理结果  
            value_to_check: 要检查的值
            
        Returns:
            str: 'A'（正确）、'B'（错误）或'C'（未知）
        """
        if result is None:
            return 'C'  # 未知
        elif result == value_to_check:
            return 'A'  # 正确
        else:
            return 'B'  # 错误


if __name__ == "__main__":
    # test pyke solver

    logic_program = """Predicates:
    Round($x, bool) ::: Is x round?
    Red($x, bool) ::: Is x red?
    Smart($x, bool) ::: Is x smart?
    Furry($x, bool) ::: Is x furry?
    Rough($x, bool) ::: Is x rough?
    Big($x, bool) ::: Is x big?
    White($x, bool) ::: Is x white?
    
    Facts:
    Round(Anne, True) ::: Anne is round.
    Red(Bob, True) ::: Bob is red.
    Smart(Bob, True) ::: Bob is smart.
    Furry(Erin, True) ::: Erin is furry.
    Red(Erin, True) ::: Erin is red.
    Rough(Erin, True) ::: Erin is rough.
    Smart(Erin, True) ::: Erin is smart.
    Big(Fiona, True) ::: Fiona is big.
    Furry(Fiona, True) ::: Fiona is furry.
    Smart(Fiona, True) ::: Fiona is smart.
    
    Rules:
    Smart($x, True) >>> Furry($x, True) ::: All smart things are furry.
    Furry($x, True) >>> Red($x, True) ::: All furry things are red.
    Round($x, True) >>> Rough($x, True) ::: All round things are rough.
    White(Bob, True) >>> Furry(Bob, True) ::: If Bob is white then Bob is furry.
    Red($x, True) && Rough($x, True) >>> Big($x, True) ::: All red, rough things are big.
    Rough($x, True) >>> Smart($x, True) ::: All rough things are smart.
    Furry(Fiona, True) >>> Red(Fiona, True) ::: If Fiona is furry then Fiona is red.
    Round(Bob, True) && Big(Bob, True) >>> Furry(Bob, True) ::: If Bob is round and Bob is big then Bob is furry.
    Red(Fiona, True) && White(Fiona, True) >>> Smart(Fiona, True) ::: If Fiona is red and Fiona is white then Fiona is smart.
    
    Query:
    White(Bob, False) ::: Bob is not white."""

    # Answer: A
    logic_program1 = "Predicates:\nCold($x, bool) ::: Is x cold?\nQuiet($x, bool) ::: Is x quiet?\nRed($x, bool) ::: Is x red?\nSmart($x, bool) ::: Is x smart?\nKind($x, bool) ::: Is x kind?\nRough($x, bool) ::: Is x rough?\nRound($x, bool) ::: Is x round?\n\nFacts:\nCold(Bob, True) ::: Bob is cold.\nQuiet(Bob, True) ::: Bob is quiet.\nRed(Bob, True) ::: Bob is red.\nSmart(Bob, True) ::: Bob is smart.\nKind(Charlie, True) ::: Charlie is kind.\nQuiet(Charlie, True) ::: Charlie is quiet.\nRed(Charlie, True) ::: Charlie is red.\nRough(Charlie, True) ::: Charlie is rough.\nCold(Dave, True) ::: Dave is cold.\nKind(Dave, True) ::: Dave is kind.\nSmart(Dave, True) ::: Dave is smart.\nQuiet(Fiona, True) ::: Fiona is quiet.\n\nRules:\nQuiet($x, True) && Cold($x, True) >>> Smart($x, True) ::: If something is quiet and cold then it is smart.\nRed($x, True) && Cold($x, True) >>> Round($x, True) ::: Red, cold things are round.\nKind($x, True) && Rough($x, True) >>> Red($x, True) ::: If something is kind and rough then it is red.\nQuiet($x, True) >>> Rough($x, True) ::: All quiet things are rough.\nCold($x, True) && Smart($x, True) >>> Red($x, True) ::: Cold, smart things are red.\nRough($x, True) >>> Cold($x, True) ::: If something is rough then it is cold.\nRed($x, True) >>> Rough($x, True) ::: All red things are rough.\nSmart(Dave, True) && Kind(Dave, True) >>> Quiet(Dave, True) ::: If Dave is smart and Dave is kind then Dave is quiet.\n\nQuery:\nKind(Charlie, True) ::: Charlie is kind."

    # Answer: B
    logic_program2 = "Predicates:\nFurry($x, bool) ::: Is x furry?\nNice($x, bool) ::: Is x nice?\nSmart($x, bool) ::: Is x smart?\nYoung($x, bool) ::: Is x young?\nGreen($x, bool) ::: Is x green?\nBig($x, bool) ::: Is x big?\nRound($x, bool) ::: Is x round?\n\nFacts:\nFurry(Anne, True) ::: Anne is furry.\nNice(Anne, True) ::: Anne is nice.\nSmart(Anne, True) ::: Anne is smart.\nYoung(Bob, True) ::: Bob is young.\nNice(Erin, True) ::: Erin is nice.\nSmart(Harry, True) ::: Harry is smart.\nYoung(Harry, True) ::: Harry is young.\n\nRules:\nYoung($x, True) >>> Furry($x, True) ::: Young things are furry.\nNice($x, True) && Furry($x, True) >>> Green($x, True) ::: Nice, furry things are green.\nGreen($x, True) >>> Nice($x, True) ::: All green things are nice.\nNice($x, True) && Green($x, True) >>> Big($x, True) ::: Nice, green things are big.\nGreen($x, True) >>> Smart($x, True) ::: All green things are smart.\nBig($x, True) && Young($x, True) >>> Round($x, True) ::: If something is big and young then it is round.\nGreen($x, True) >>> Big($x, True) ::: All green things are big.\nYoung(Harry, True) >>> Furry(Harry, True) ::: If Harry is young then Harry is furry.\nFurry($x, True) && Smart($x, True) >>> Nice($x, True) ::: Furry, smart things are nice.\n\nQuery:\nGreen(Harry, False) ::: Harry is not green."

    # Answer: C
    logic_program3 = "Predicates:\nChases($x, $y, bool) ::: Does x chase y?\nRough($x, bool) ::: Is x rough?\nYoung($x, bool) ::: Is x young?\nNeeds($x, $y, bool) ::: Does x need y?\nGreen($x, bool) ::: Is x green?\nLikes($x, $y, bool) ::: Does x like y?\nBlue($x, bool) ::: Is x blue?\nRound($x, bool) ::: Is x round?\n\nFacts:\nChases(Cat, Lion, True) ::: The cat chases the lion.\nRough(Cat, True) ::: The cat is rough.\nYoung(Cat, True) ::: The cat is young.\nNeeds(Cat, Lion, True) ::: The cat needs the lion.\nNeeds(Cat, Rabbit, True) ::: The cat needs the rabbit.\nGreen(Dog, True) ::: The dog is green.\nYoung(Dog, True) ::: The dog is young.\nLikes(Dog, Cat, True) ::: The dog likes the cat.\nBlue(Lion, True) ::: The lion is blue.\nGreen(Lion, True) ::: The lion is green.\nChases(Rabbit, Lion, True) ::: The rabbit chases the lion.\nBlue(Rabbit, True) ::: The rabbit is blue.\nRough(Rabbit, True) ::: The rabbit is rough.\nLikes(Rabbit, Dog, True) ::: The rabbit likes the dog.\nNeeds(Rabbit, Dog, True) ::: The rabbit needs the dog.\nNeeds(Rabbit, Lion, True) ::: The rabbit needs the lion.\n\nRules:\nChases($x, Lion, True) >>> Round($x, True) ::: If someone chases the lion then they are round.\nNeeds(Lion, Rabbit, True) && Chases(Rabbit, Dog, True) >>> Likes(Lion, Dog, True) ::: If the lion needs the rabbit and the rabbit chases the dog then the lion likes the dog.\nRound($x, True) && Chases($x, Lion, True) >>> Needs($x, Cat, True) ::: If someone is round and they chase the lion then they need the cat.\nNeeds($x, Cat, True) && Chases($x, Dog, True) >>> Likes($x, Rabbit, True) ::: If someone needs the cat and they chase the dog then they like the rabbit.\nChases($x, Lion, True) && Blue(Lion, True) >>> Round(Lion, True) ::: If someone chases the lion and the lion is blue then the lion is round.\nChases($x, Rabbit, True) >>> Rough($x, True) ::: If someone chases the rabbit then they are rough.\nRough($x, True) && Likes($x, Rabbit, True) >>> Young(Rabbit, True) ::: If someone is rough and they like the rabbit then the rabbit is young.\nChases(Rabbit, Cat, True) && Needs(Cat, Lion, True) >>> Young(Rabbit, True) ::: If the rabbit chases the cat and the cat needs the lion then the rabbit is young.\nRound($x, True) && Needs($x, Cat, True) >>> Chases($x, Dog, True) ::: If someone is round and they need the cat then they chase the dog.\n\nQuery:\nLikes(Lion, Cat, False) ::: The lion does not like the cat."

    # Answer: A
    logic_program4 = "Predicates:\nFurry($x, bool) ::: Is x furry?\nNice($x, bool) ::: Is x nice?\n\nFacts:\nFurry(Anne, True) ::: Anne is furry.\n\nRules:\nFurry($x, True) >>> Nice($x, True) ::: All furry things are nice.\n\nQuery:\nNice(Anne, True) ::: Anne is nice."

    # Answer: B
    logic_program5 = "Predicates:\nFurry($x, bool) ::: Is x furry?\nNice($x, bool) ::: Is x nice?\n\nFacts:\nFurry(Anne, True) ::: Anne is furry.\n\nRules:\nFurry($x, True) >>> Nice($x, True) ::: All furry things are nice.\n\nQuery:\nNice(Anne, False) ::: Anne is not nice."

    # Answer: C
    logic_program6 = "Predicates:\nFurry($x, bool) ::: Is x furry?\nNice($x, bool) ::: Is x nice?\n\nFacts:\nFurry(Anne, True) ::: Anne is furry.\n\nRules:\nFurry($x, False) >>> Nice($x, True) ::: All non-furry things are nice.\n\nQuery:\nNice(Anne, True) ::: Anne is nice."

    # Answer: B
    logic_program7 = """Predicates:
Furry($x, bool) ::: Is x furry?
Nice($x, bool) ::: Is x nice?
Smart($x, bool) ::: Is x smart?
Young($x, bool) ::: Is x young?
Green($x, bool) ::: Is x green?
Big($x, bool) ::: Is x big?
Round($x, bool) ::: Is x round?

Facts:
Furry(Anne, True) ::: Anne is furry.
Nice(Anne, True) ::: Anne is nice.
Smart(Anne, True) ::: Anne is smart.
Young(Bob, True) ::: Bob is young.
Nice(Erin, True) ::: Erin is nice.
Smart(Harry, True) ::: Harry is smart.
Young(Harry, True) ::: Harry is young.

Rules:
Young($x, True) >>> Furry($x, True) ::: Young things are furry.
Nice($x, True) && Furry($x, True) >>> Green($x, True) ::: Nice, furry things are green.
Green($x, True) >>> Nice($x, True) ::: All green things are nice.
Nice($x, True) && Green($x, True) >>> Big($x, True) ::: Nice, green things are big.
Green($x, True) >>> Smart($x, True) ::: All green things are smart.
Big($x, True) && Young($x, True) >>> Round($x, True) ::: If something is big and young then it is round.
Green($x, True) >>> Big($x, True) ::: All green things are big.
Young(Harry, True) >>> Furry(Harry, True) ::: If Harry is young then Harry is furry.
Furry($x, True) && Smart($x, True) >>> Nice($x, True) ::: Furry, smart things are nice.

Query:
Green(Harry, False) ::: Harry is not green."""

    # tests = [logic_program1, logic_program2, logic_program3, logic_program4, logic_program5, logic_program6]

    tests = [logic_program7]
    
    for test in tests:
        pyke_program = Pyke_Program(test, 'ProofWriter')
        print(pyke_program.flag)
        # print(pyke_program.Rules)
        # print(pyke_program.Facts)
        # print(pyke_program.Query)
        # print(pyke_program.Predicates)

        result, error_message = pyke_program.execute_program()
        print(result, error_message)

    complied_krb_dir = './compiled_krb'
    if os.path.exists(complied_krb_dir):
        print('removing compiled_krb')
        os.system(f'rm -rf {complied_krb_dir}')