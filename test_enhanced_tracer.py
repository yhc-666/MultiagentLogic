#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from csp_solver import CSP_Program
from tracer import trace_to_text

def test_enhanced_tracer():
    """测试增强版tracer的失败原因功能"""
    
    print("=== 测试增强版CSP追踪功能 ===\n")
    
    # 测试用例：书籍排列问题
    logic_program = """Domain:
1: leftmost
5: rightmost
Variables:
green_book [IN] [1, 2, 3, 4, 5]
blue_book [IN] [1, 2, 3, 4, 5]
white_book [IN] [1, 2, 3, 4, 5]
purple_book [IN] [1, 2, 3, 4, 5]
yellow_book [IN] [1, 2, 3, 4, 5]
Constraints:
blue_book > yellow_book ::: The blue book is to the right of the yellow book.
white_book < yellow_book ::: The white book is to the left of the yellow book.
blue_book == 4 ::: The blue book is the second from the right.
purple_book == 2 ::: The purple book is the second from the left.
AllDifferentConstraint([green_book, blue_book, white_book, purple_book, yellow_book]) ::: All books have different values.
Query:
A) green_book == 2 ::: The green book is the second from the left.
B) blue_book == 2 ::: The blue book is the second from the left.
C) white_book == 2 ::: The white book is the second from the left.
D) purple_book == 2 ::: The purple book is the second from the left.
E) yellow_book == 2 ::: The yellow book is the second from the left."""

    # 创建CSP程序并执行
    csp_program = CSP_Program(logic_program, 'LogicalDeduction')
    ans, err_msg, reasoning = csp_program.execute_program()
    
    print("📊 **求解结果：**")
    print(f"Answer: {ans}")
    print(f"Error: {err_msg}")
    print(f"Final answer: {csp_program.answer_mapping(ans)}")
    
    print("\n🔍 **详细推理过程（含失败原因）：**")
    if reasoning:
        print(trace_to_text(reasoning))
    else:
        print("No reasoning trace available")
    
    print("\n📈 **失败原因分析：**")
    if reasoning and "trace" in reasoning:
        fail_reasons = {}
        for event_type, depth, data in reasoning["trace"]:
            if event_type == "FAIL":
                reason = data.get('reason', 'unknown')
                fail_reasons[reason] = fail_reasons.get(reason, 0) + 1
        
        print("失败原因统计：")
        for reason, count in fail_reasons.items():
            print(f"  - {reason}: {count} 次")
    
    print("\n✅ **测试完成！**")

if __name__ == "__main__":
    test_enhanced_tracer() 