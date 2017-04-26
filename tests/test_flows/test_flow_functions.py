from collections import OrderedDict
import copy
import unittest

import openml
from openml.util import is_string


class TestFlowFunctions(unittest.TestCase):
    def _check_flow(self, flow):
        self.assertEqual(type(flow), dict)
        self.assertEqual(len(flow), 6)
        self.assertIsInstance(flow['id'], int)
        self.assertTrue(is_string(flow['name']))
        self.assertTrue(is_string(flow['full_name']))
        self.assertTrue(is_string(flow['version']))
        # There are some runs on openml.org that can have an empty external
        # version
        self.assertTrue(is_string(flow['external_version']) or
                        flow['external_version'] is None)

    def test_list_flows(self):
        # We can only perform a smoke test here because we test on dynamic
        # data from the internet...
        flows = openml.flows.list_flows()
        # 3000 as the number of flows on openml.org
        self.assertGreaterEqual(len(flows), 3000)
        for fid in flows:
            self._check_flow(flows[fid])

    def test_list_flows_by_tag(self):
        flows = openml.flows.list_flows(tag='weka')
        self.assertGreaterEqual(len(flows), 5)
        for did in flows:
            self._check_flow(flows[did])

    def test_list_flows_paginate(self):
        size = 10
        max = 100
        for i in range(0, max, size):
            flows = openml.flows.list_flows(offset=i, size=size)
            self.assertGreaterEqual(size, len(flows))
            for did in flows:
                self._check_flow(flows[did])

    def test_are_flows_equal(self):
        flow = openml.flows.OpenMLFlow(name='Test',
                                       description='Test flow',
                                       model=None,
                                       components=OrderedDict(),
                                       parameters=OrderedDict(),
                                       parameters_meta_info=OrderedDict(),
                                       external_version='1',
                                       tags=['abc', 'def'],
                                       language='English',
                                       dependencies='abc',
                                       class_name='Test',
                                       custom_name='Test')

        # Test most important values that can be set by a user
        openml.flows.functions.assert_flows_equal(flow, flow)
        for attribute, new_value in [('name', 'Tes'),
                                     ('description', 'Test flo'),
                                     ('external_version', '2'),
                                     ('tags', ['abc', 'de']),
                                     ('language', 'english'),
                                     ('dependencies', 'ab'),
                                     ('class_name', 'Tes'),
                                     ('custom_name', 'Tes')]:
            new_flow = copy.deepcopy(flow)
            setattr(new_flow, attribute, new_value)
            self.assertNotEqual(getattr(flow, attribute), getattr(new_flow, attribute))
            self.assertRaises(ValueError, openml.flows.functions.assert_flows_equal,
                              flow, new_flow)

        # Test that the API ignores several keys when comparing flows
        openml.flows.functions.assert_flows_equal(flow, flow)
        for attribute, new_value in [('flow_id', 1),
                                     ('uploader', 1),
                                     ('version', 1),
                                     ('upload_date', '18.12.1988'),
                                     ('binary_url', 'openml.org'),
                                     ('binary_format', 'gzip'),
                                     ('binary_md5', '12345'),
                                     ('model', [])]:
            new_flow = copy.deepcopy(flow)
            setattr(new_flow, attribute, new_value)
            self.assertNotEqual(getattr(flow, attribute), getattr(new_flow, attribute))
            openml.flows.functions.assert_flows_equal(flow, new_flow)

        # Now test for parameters
        flow.parameters['abc'] = 1.0
        flow.parameters['def'] = 2.0
        openml.flows.functions.assert_flows_equal(flow, flow)
        new_flow = copy.deepcopy(flow)
        new_flow.parameters['abc'] = 3.0
        self.assertRaises(ValueError, openml.flows.functions.assert_flows_equal,
                          flow, new_flow)

        # Now test for components (subflows)
        parent_flow = copy.deepcopy(flow)
        subflow = copy.deepcopy(flow)
        parent_flow.components['subflow'] = subflow
        openml.flows.functions.assert_flows_equal(parent_flow, parent_flow)
        self.assertRaises(ValueError,
                          openml.flows.functions.assert_flows_equal,
                          parent_flow, subflow)
        new_flow = copy.deepcopy(parent_flow)
        new_flow.components['subflow'].name = 'Subflow name'
        self.assertRaises(ValueError,
                          openml.flows.functions.assert_flows_equal,
                          parent_flow, new_flow)