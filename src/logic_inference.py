import argparse
import json
import os

from symbolic_solvers.pyke_solver.pyke_solver import Pyke_Program
from symbolic_solvers.fol_solver.prover9_solver import FOL_Prover9_Program
from symbolic_solvers.csp_solver.csp_solver import CSP_Program
from symbolic_solvers.z3_solver.sat_problem_solver import LSAT_Z3_Program
from backup_answer_generation import Backup_Answer_Generator

# currently 4 SLs are from different datasets for MVP, the mapping will be adjusted in the future
PROGRAM_CLASS = {
    'LP': (Pyke_Program, 'ProntoQA'),
    'FOL': (FOL_Prover9_Program, 'FOLIO'),
    'CSP': (CSP_Program, 'LogicalDeduction'),
    'SAT': (LSAT_Z3_Program, 'AR-LSAT'),
}


class LogicInferenceEngine:
    def __init__(self, args):
        self.args = args
        self.dataset = self.load_logic_programs(args.input_file)
        self.output_file = args.output_file

        # optional, use LLMwCOT & random guess as backup answers in case solver fails
        self.backup_strategy = args.backup_strategy
        self.backup_LLM_result_path = args.backup_LLM_result_path
        self.backup_generators = {
            key: Backup_Answer_Generator(name, self.backup_strategy, self.backup_LLM_result_path)
            for key, (_, name) in PROGRAM_CLASS.items()
        }

    def load_logic_programs(self, input_file):
        with open(input_file, 'r') as f:
            dataset = json.load(f)
        print(f"Loaded {len(dataset)} examples from {input_file}")
        return dataset

    def save_results(self, outputs):
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        with open(self.output_file, 'w') as f:
            json.dump(outputs, f, indent=2, ensure_ascii=False)

    def safe_execute_program(self, key, logic_program, example_id):
        cls, dataset_name = PROGRAM_CLASS[key]
        program = cls(logic_program, dataset_name)

        if not getattr(program, 'flag', True): # flag 表示是否成功parse逻辑程序SL, 不代表execute成功与否
            answer = self.backup_generators[key].get_backup_answer(example_id)
            return answer, 'parsing error', ''

        answer, err = program.execute_program()
        if answer is None:
            answer = self.backup_generators[key].get_backup_answer(example_id)
            return answer, 'execution error', err

        mapped = program.answer_mapping(answer)
        return mapped, 'success', ''

    def inference_on_dataset(self):
        outputs = []
        for example in self.dataset:
            result = {
                'id': example.get('id'),
                'context': example.get('context'),
                'question': example.get('question'),
                'option': example.get('options'),
                'answer': example.get('answer'),
            }
            for key in ['LP', 'FOL', 'CSP', 'SAT']:
                logic_str = example[key][0]
                predicted, status_code, _ = self.safe_execute_program(key, logic_str, example['id'])
                result[f'{key}_status_code'] = status_code
                result[f'{key}_predicted_answer'] = predicted
            outputs.append(result)

        self.save_results(outputs)
        self.cleanup()

    def cleanup(self):
        """
        remove the compiled krb directory
        """
        cache_program_dir = 'src/symbolic_solvers/pyke_solver/.cache_program'
        compiled_dir = 'src/compiled_krb'
        if os.path.exists(cache_program_dir):
            print('removing cache_program')
            os.system(f'rm -rf {cache_program_dir}')
        if os.path.exists(compiled_dir):
            print('removing compiled_krb')
            os.system(f'rm -rf {compiled_dir}')

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', type=str, default=os.path.join('sample_data', 'sample_input.json'))
    parser.add_argument('--output_file', type=str, default=os.path.join('sample_data', 'sample_output.json'))
    parser.add_argument('--backup_strategy', type=str, default='random', choices=['random', 'LLM'])
    parser.add_argument('--backup_LLM_result_path', type=str, default='') # path to the LLMwCOT result
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    engine = LogicInferenceEngine(args)
    engine.inference_on_dataset()
