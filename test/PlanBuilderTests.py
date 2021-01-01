import inspect
import itertools
import re
from datetime import timedelta

from typing import List

from base.Pattern import Pattern
from base.PatternStructure import SeqOperator, PrimitiveEventStructure, NegationOperator, AndOperator
from condition.BaseRelationCondition import GreaterThanCondition, SmallerThanCondition, SmallerThanEqCondition, \
    GreaterThanEqCondition
from condition.CompositeCondition import AndCondition
from condition.Condition import Variable
from plan.UnifiedTreeBuilder import UnifiedTreeBuilder as UnifiedTreeBuilder
from plan.TreePlanBuilder import TreePlanBuilder
from plan.TreePlanBuilderFactory import TreePlanBuilderFactory
from plan.TreePlanBuilderOrders import TreePlanBuilderOrder
from plan.multi.MultiPatternUnifiedTreePlanApproaches import MultiPatternTreePlanUnionApproaches
from test.testUtils import *


def get_opening_price(x):
    return x["Opening Price"]


def get_peak_price(x):
    return x["Peak Price"]


def get_lowest_price(x):
    return x["Lowest Price"]


def split_union_approaches(string):
    return '{:10s}'.format(str(string).split("TREE_PLAN_")[1].replace("_", " "))


def print_result(string1, string2, string3):
    print("{:^50s} | {:^25s} | {:^15s}".format(string1, string2, string3))


def test_run(patterns: List[Pattern], expected: int,
             approach: MultiPatternTreePlanUnionApproaches = MultiPatternTreePlanUnionApproaches.TREE_PLAN_TRIVIAL_SHARING_LEAVES):
    actual = get_max_size_of_intersection_of_all_patterns(patterns, approach=approach)
    result = "SUCCESS" if actual == expected else f'\tFAILED \t expected: {expected}, actual: {actual}'
    print_result(inspect.stack()[1][3] ,split_union_approaches(approach),result)


def get_max_size_of_intersection_of_all_patterns(patterns: List[Pattern],
                                                 approach: MultiPatternTreePlanUnionApproaches):
    eval_mechanism_params = TreeBasedEvaluationMechanismParameters()
    tree_plan_builder = TreePlanBuilderFactory.create_tree_plan_builder(eval_mechanism_params.tree_plan_params)
    pattern_to_tree_plan_map = {pattern: tree_plan_builder.build_tree_plan(pattern) for pattern in patterns}
    builder = UnifiedTreeBuilder()
    _ = builder._union_tree_plans(pattern_to_tree_plan_map,
                                  approach)
    size_of_intersection = builder.trees_number_nodes_shared
    return size_of_intersection


def get_max_size_of_intersection_of_all_patterns_tmp(patterns: List[Pattern], approach):  # TODO remove
    pattern1, pattern2 = patterns[0], patterns[1]
    approach1, approach2 = TreePlanBuilderOrder.list()[:2]
    builder1 = UnifiedTreeBuilder.get_instance(tree_plan_order_approach=approach1)
    builder2 = UnifiedTreeBuilder.get_instance(tree_plan_order_approach=approach2)
    pattern_to_tree_plan_map = {pattern1: builder1.build_tree_plan(pattern1),
                                pattern2: builder2.build_tree_plan(pattern2)}

    builder = UnifiedTreeBuilder()
    _ = builder._union_tree_plans(pattern_to_tree_plan_map, tree_plan_union_approach=approach)
    size_of_intersection = builder.trees_number_nodes_shared
    return size_of_intersection


# tests for sharing leaves

def same_tests():
    pattern1 = Pattern(
        SeqOperator(PrimitiveEventStructure("AAPL", "a"),
                    PrimitiveEventStructure("AMZN", "b"),
                    PrimitiveEventStructure("GOOG", "c"),
                    PrimitiveEventStructure("GOOG", "e")),
        AndCondition(
            GreaterThanCondition(Variable("a", get_opening_price),
                                 Variable("b", get_opening_price)),
            GreaterThanCondition(Variable("c", get_peak_price), 503)
        ),
        timedelta(minutes=5)
    )

    pattern2 = Pattern(
        SeqOperator(PrimitiveEventStructure("AAPL", "a"),
                    PrimitiveEventStructure("AMZN", "b"),
                    PrimitiveEventStructure("GOOG", "c"),
                    PrimitiveEventStructure("GOOG", "e")),
        AndCondition(
            GreaterThanCondition(Variable("a", get_opening_price),
                                 Variable("b", get_opening_price)),
            GreaterThanCondition(Variable("c", get_peak_price), 503)
        ),
        timedelta(minutes=5)
    )

    test_run(patterns=[pattern1, pattern2], expected=4, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_TRIVIAL_SHARING_LEAVES)
    test_run(patterns=[pattern1, pattern2], expected=7, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_SUBTREES_UNION)
    test_run(patterns=[pattern1, pattern2], expected=7, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_CHANGE_TOPOLOGY_UNION)


def same_eventsType_different_names_tests():
    pattern1 = Pattern(
        SeqOperator(PrimitiveEventStructure("AAPL", "a"),
                    PrimitiveEventStructure("AMZN", "b"),
                    PrimitiveEventStructure("GOOG", "c"),
                    PrimitiveEventStructure("GOOG", "e")),
        AndCondition(
            GreaterThanCondition(Variable("a", get_opening_price),
                                 Variable("b", get_opening_price)),
            GreaterThanCondition(Variable("c", get_peak_price), 503)
        ),
        timedelta(minutes=5)
    )

    pattern2 = Pattern(
        SeqOperator(PrimitiveEventStructure("AAPL", "m"),
                    PrimitiveEventStructure("AMZN", "b"),
                    PrimitiveEventStructure("GOOG", "c"),
                    PrimitiveEventStructure("GOOG", "e")),
        AndCondition(
            GreaterThanCondition(Variable("m", get_opening_price),
                                 Variable("b", get_opening_price)),
            GreaterThanCondition(Variable("c", get_peak_price), 503)
        ),
        timedelta(minutes=5)
    )
    test_run(patterns=[pattern1, pattern2], expected=3, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_TRIVIAL_SHARING_LEAVES)
    test_run(patterns=[pattern1, pattern2], expected=3, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_SUBTREES_UNION)
    test_run(patterns=[pattern1, pattern2], expected=5, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_CHANGE_TOPOLOGY_UNION)


def same_events_different_condition_tests():
    pattern1 = Pattern(
        AndOperator(PrimitiveEventStructure("AAPL", "a"),
                    PrimitiveEventStructure("AMZN", "b"),
                    PrimitiveEventStructure("GOOG", "c"),
                    PrimitiveEventStructure("GOOG", "e")),
        AndCondition(
            GreaterThanCondition(Variable("a", get_opening_price),
                                 Variable("b", get_opening_price)),
            GreaterThanCondition(Variable("c", get_peak_price), 503)
        ),
        timedelta(minutes=5)
    )

    pattern2 = Pattern(
        AndOperator(PrimitiveEventStructure("AAPL", "a"),
                    PrimitiveEventStructure("AMZN", "b"),
                    PrimitiveEventStructure("GOOG", "c"),
                    PrimitiveEventStructure("GOOG", "e")),
        AndCondition(
            GreaterThanCondition(Variable("a", get_opening_price),
                                 Variable("b", get_opening_price)),
            GreaterThanCondition(Variable("c", get_peak_price), 500)
        ),
        timedelta(minutes=5)
    )

    test_run(patterns=[pattern1, pattern2], expected=3, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_TRIVIAL_SHARING_LEAVES)
    test_run(patterns=[pattern1, pattern2], expected=4, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_SUBTREES_UNION)
    test_run(patterns=[pattern1, pattern2], expected=4, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_CHANGE_TOPOLOGY_UNION)
    #TODO:third approach need to return 5 because AND is Commutative

def sameNames_different_eventTypes_tests():
    pattern1 = Pattern(
        SeqOperator(PrimitiveEventStructure("AAPL", "a"),
                    PrimitiveEventStructure("AMZN", "b"),
                    PrimitiveEventStructure("GOOG", "c"),
                    PrimitiveEventStructure("GOOG", "e")),
        AndCondition(
            GreaterThanCondition(Variable("a", get_opening_price),
                                 Variable("b", get_opening_price)),
            GreaterThanCondition(Variable("c", get_peak_price), 500)
        ),
        timedelta(minutes=5)
    )

    pattern2 = Pattern(
        SeqOperator(PrimitiveEventStructure("AAPL", "a"),
                    PrimitiveEventStructure("AMZN", "b"),
                    PrimitiveEventStructure("GOOG", "c"),
                    PrimitiveEventStructure("AMZN", "e")),  # no the same event as the first pattern
        AndCondition(
            GreaterThanCondition(Variable("a", get_opening_price),
                                 Variable("b", get_opening_price)),
            GreaterThanCondition(Variable("c", get_peak_price), 500)
        ),
        timedelta(minutes=5)
    )
    test_run(patterns=[pattern1, pattern2], expected=3, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_TRIVIAL_SHARING_LEAVES)
    test_run(patterns=[pattern1, pattern2], expected=5, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_SUBTREES_UNION)
    test_run(patterns=[pattern1, pattern2], expected=5, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_CHANGE_TOPOLOGY_UNION)


def same_events_different_function_test():
    pattern1 = Pattern(
        SeqOperator(PrimitiveEventStructure("AAPL", "a"),
                    PrimitiveEventStructure("AMZN", "b"),
                    PrimitiveEventStructure("GOOG", "c"),
                    PrimitiveEventStructure("GOOG", "e")),
        AndCondition(
            GreaterThanCondition(Variable("a", get_opening_price), 5),
            GreaterThanCondition(Variable("c", get_peak_price), 500)
        ),
        timedelta(minutes=5)
    )

    pattern2 = Pattern(
        SeqOperator(PrimitiveEventStructure("AAPL", "a"),
                    PrimitiveEventStructure("AMZN", "b"),
                    PrimitiveEventStructure("GOOG", "c"),
                    PrimitiveEventStructure("GOOG", "e")),
        AndCondition(
            GreaterThanCondition(Variable("a", get_opening_price), 7),  # different function from pattern 1
            GreaterThanCondition(Variable("c", get_peak_price), 500)
        ),
        timedelta(minutes=5)
    )
    test_run(patterns=[pattern1, pattern2], expected=3, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_TRIVIAL_SHARING_LEAVES)
    test_run(patterns=[pattern1, pattern2], expected=3, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_SUBTREES_UNION)
    test_run(patterns=[pattern1, pattern2], expected=5, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_CHANGE_TOPOLOGY_UNION)


def same_leaves_different_time_stamps_tests():
    pattern1 = Pattern(
        SeqOperator(PrimitiveEventStructure("AAPL", "a"),
                    PrimitiveEventStructure("AMZN", "b"),
                    PrimitiveEventStructure("GOOG", "c")),
        AndCondition(
            GreaterThanEqCondition(Variable("a", get_peak_price), 135),
            SmallerThanCondition(Variable("b", get_peak_price),
                                 Variable("c", get_peak_price))
        ),
        timedelta(minutes=5)
    )
    pattern2 = Pattern(
        SeqOperator(PrimitiveEventStructure("AAPL", "a"),
                    PrimitiveEventStructure("AMZN", "b"),
                    PrimitiveEventStructure("GOOG", "c")),
        AndCondition(
            GreaterThanEqCondition(Variable("a", get_peak_price), 135),
            SmallerThanCondition(Variable("b", get_peak_price),
                                 Variable("c", get_peak_price))
        ),
        timedelta(minutes=2)
    )

    test_run(patterns=[pattern1, pattern2], expected=3, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_TRIVIAL_SHARING_LEAVES)
    test_run(patterns=[pattern1, pattern2], expected=5, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_SUBTREES_UNION)
    test_run(patterns=[pattern1, pattern2], expected=5, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_CHANGE_TOPOLOGY_UNION)


def distinct_tests():
    pattern1 = Pattern(
        SeqOperator(PrimitiveEventStructure("GOOG", "a"),
                    PrimitiveEventStructure("GOOG", "b"),
                    PrimitiveEventStructure("GOOG", "c")),
        AndCondition(
            SmallerThanCondition(Variable("a", get_peak_price),
                                 Variable("b", get_peak_price)),
            SmallerThanCondition(Variable("b", get_peak_price),
                                 Variable("c", get_peak_price))
        ),
        timedelta(minutes=3)
    )
    pattern2 = Pattern(
        SeqOperator(PrimitiveEventStructure("AMZN", "x1"),
                    PrimitiveEventStructure("AMZN", "x2"),
                    PrimitiveEventStructure("AMZN", "x3")),
        AndCondition(
            SmallerThanEqCondition(Variable("x1", get_lowest_price), 75),
            GreaterThanEqCondition(Variable("x2", get_peak_price), 78),
            SmallerThanEqCondition(Variable("x3", get_lowest_price),
                                   Variable("x1", get_lowest_price))
        ),
        timedelta(days=1)
    )
    test_run(patterns=[pattern1, pattern2], expected=0, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_TRIVIAL_SHARING_LEAVES)
    test_run(patterns=[pattern1, pattern2], expected=0, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_SUBTREES_UNION)
    test_run(patterns=[pattern1, pattern2], expected=0, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_CHANGE_TOPOLOGY_UNION)


def partially_shared_tests():
    pattern1 = Pattern(
        SeqOperator(PrimitiveEventStructure("AAPL", "a"),
                    PrimitiveEventStructure("AMZN", "b"),
                    PrimitiveEventStructure("AAPL", "c"),
                    PrimitiveEventStructure("AAPL", "e")),
        AndCondition(
            GreaterThanCondition(Variable("a", get_opening_price),
                                 Variable("b", get_opening_price)),
            GreaterThanCondition(Variable("b", get_opening_price),
                                 Variable("c", get_opening_price))),
        timedelta(minutes=5)
    )

    pattern2 = Pattern(
        SeqOperator(PrimitiveEventStructure("AAPL", "a"),
                    PrimitiveEventStructure("AMZN", "b"),
                    PrimitiveEventStructure("GOOG", "c"),  # not the same event type  as the pattern 1
                    PrimitiveEventStructure("AMZN", "e")),  # not the same event type  as the pattern 1
        AndCondition(
            GreaterThanCondition(Variable("a", get_opening_price),
                                 Variable("b", get_opening_price)),
            GreaterThanCondition(Variable("b", get_opening_price),
                                 Variable("c", get_opening_price))
        ),
        timedelta(minutes=5)
    )
    test_run(patterns=[pattern1, pattern2], expected=2, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_TRIVIAL_SHARING_LEAVES)
    test_run(patterns=[pattern1, pattern2], expected=3, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_SUBTREES_UNION)
    test_run(patterns=[pattern1, pattern2], expected=3, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_CHANGE_TOPOLOGY_UNION)


def leaf_is_root_tests():
    pattern1 = Pattern(
        SeqOperator(PrimitiveEventStructure("AAPL", "a")),
        GreaterThanCondition(Variable("a", get_peak_price), 135),
        timedelta(minutes=5)
    )
    pattern2 = Pattern(
        SeqOperator(PrimitiveEventStructure("AAPL", "a"), NegationOperator(PrimitiveEventStructure("AMZN", "b")),
                    PrimitiveEventStructure("GOOG", "c")),
        AndCondition(
            GreaterThanCondition(Variable("a", get_opening_price),
                                 Variable("b", get_opening_price)),
            SmallerThanCondition(Variable("b", get_opening_price),
                                 Variable("c", get_opening_price))),
        timedelta(minutes=5)
    )

    test_run(patterns=[pattern1, pattern2], expected=0, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_TRIVIAL_SHARING_LEAVES)
    test_run(patterns=[pattern1, pattern2], expected=0, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_SUBTREES_UNION)
    test_run(patterns=[pattern1, pattern2], expected=0, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_CHANGE_TOPOLOGY_UNION)


def leaf_is_root_tests2():
    pattern1 = Pattern(
        SeqOperator(PrimitiveEventStructure("AAPL", "a")),
        GreaterThanCondition(Variable("a", get_peak_price), 135),
        timedelta(minutes=5)
    )
    pattern2 = Pattern(
        SeqOperator(PrimitiveEventStructure("AAPL", "a"), NegationOperator(PrimitiveEventStructure("AMZN", "b")),
                    PrimitiveEventStructure("GOOG", "c")),
        AndCondition(
            GreaterThanCondition(Variable("a", get_peak_price), 135),

            GreaterThanCondition(Variable("a", get_opening_price),
                                 Variable("b", get_opening_price)),
            SmallerThanCondition(Variable("b", get_opening_price),
                                 Variable("c", get_opening_price))),
        timedelta(minutes=5)
    )

    test_run(patterns=[pattern1, pattern2], expected=1, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_TRIVIAL_SHARING_LEAVES)
    test_run(patterns=[pattern1, pattern2], expected=1, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_SUBTREES_UNION)
    test_run(patterns=[pattern1, pattern2], expected=1, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_CHANGE_TOPOLOGY_UNION)




def three_patterns_no_sharing_tests():
    pattern1 = Pattern(
        AndOperator(PrimitiveEventStructure("AAPL", "a"),
                    PrimitiveEventStructure("AMZN", "b"),
                    PrimitiveEventStructure("GOOG", "c")),
        AndCondition(
            SmallerThanCondition(Variable("a", get_peak_price), Variable("b", get_peak_price)),
            SmallerThanCondition(Variable("b", get_peak_price), Variable("c", get_peak_price))
        ),
        timedelta(minutes=1)
    )
    pattern2 = Pattern(
        SeqOperator(PrimitiveEventStructure("MSFT", "a"),
                    PrimitiveEventStructure("DRIV", "b"),
                    PrimitiveEventStructure("MSFT", "c"),
                    PrimitiveEventStructure("DRIV", "d"),
                    PrimitiveEventStructure("MSFT", "e")),
        AndCondition(
            SmallerThanCondition(Variable("a", get_peak_price), Variable("b", get_peak_price)),
            SmallerThanCondition(Variable("b", get_peak_price), Variable("c", get_peak_price)),
            SmallerThanCondition(Variable("c", get_peak_price), Variable("d", get_peak_price)),
            SmallerThanCondition(Variable("d", get_peak_price), Variable("e", get_peak_price))
        ),
        timedelta(minutes=10)
    )
    pattern3 = Pattern(
        SeqOperator(PrimitiveEventStructure("AAPL", "a"),
                    PrimitiveEventStructure("AMZN", "b"),
                    PrimitiveEventStructure("GOOG", "c")),
        AndCondition(
            GreaterThanCondition(Variable("a", get_opening_price), 7),
            GreaterThanCondition(Variable("b", get_opening_price), 8),
            GreaterThanCondition(Variable("c", get_opening_price), 99)),
        timedelta(minutes=5)
    )

    test_run(patterns=[pattern1, pattern2, pattern3], expected=0, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_TRIVIAL_SHARING_LEAVES)
    test_run(patterns=[pattern1, pattern2, pattern3], expected=0, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_SUBTREES_UNION)
    test_run(patterns=[pattern1, pattern2, pattern3], expected=0, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_SUBTREES_UNION)




def three_patterns_partial_sharing_tests():
    pattern1 = Pattern(
        AndOperator(PrimitiveEventStructure("AAPL", "a"),
                    PrimitiveEventStructure("AMZN", "b"),
                    PrimitiveEventStructure("GOOG", "c")),
        SmallerThanCondition(Variable("a", get_peak_price), Variable("b", get_peak_price)),
        timedelta(minutes=1)
    )
    pattern2 = Pattern(
        SeqOperator(PrimitiveEventStructure("MSFT", "a"),
                    PrimitiveEventStructure("DRIV", "b"),
                    PrimitiveEventStructure("MSFT", "c"),
                    PrimitiveEventStructure("DRIV", "d"),
                    PrimitiveEventStructure("MSFT", "e")),
        AndCondition(
            SmallerThanCondition(Variable("a", get_peak_price), Variable("b", get_peak_price)),
            SmallerThanCondition(Variable("b", get_peak_price), Variable("c", get_peak_price)),
            SmallerThanCondition(Variable("c", get_peak_price), Variable("d", get_peak_price)),
            SmallerThanCondition(Variable("d", get_peak_price), Variable("e", get_peak_price))
        ),
        timedelta(minutes=10)
    )
    pattern3 = Pattern(
        AndOperator(PrimitiveEventStructure("AAPL", "a"),
                    PrimitiveEventStructure("AMZN", "b"),
                    PrimitiveEventStructure("GOOG", "c")),
        SmallerThanCondition(Variable("a", get_peak_price), Variable("b", get_peak_price)),
        timedelta(minutes=5)
    )

    test_run(patterns=[pattern1, pattern2, pattern3], expected=3, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_TRIVIAL_SHARING_LEAVES)
    test_run(patterns=[pattern1, pattern2, pattern3], expected=5, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_SUBTREES_UNION)
    test_run(patterns=[pattern1, pattern2,pattern3], expected=5, approach=MultiPatternTreePlanUnionApproaches.TREE_PLAN_CHANGE_TOPOLOGY_UNION)




if __name__ == '__main__':
    print_result("TEST", "UNION APPROACH", "RESULT")
    print("==============================================================================================")
    same_tests()
    same_eventsType_different_names_tests()
    same_events_different_condition_tests()
    sameNames_different_eventTypes_tests()
    same_events_different_function_test()
    same_leaves_different_time_stamps_tests()
    distinct_tests()
    partially_shared_tests()
    leaf_is_root_tests()
    leaf_is_root_tests2()
    three_patterns_no_sharing_tests()
    three_patterns_partial_sharing_tests()
