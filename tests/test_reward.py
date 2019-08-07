# -*- coding: utf-8 -*-

import math
import unittest

from parms.parms import get_copy_of_params as get_test_params
from reward_function import RewardEvaluator


class RewardEvaluatorTestCase(unittest.TestCase):

    def test_get_waypoint(self):
        params_test = get_test_params()
        params_test['waypoints'] = [(0, 0), (1, 0), (2, 0), (3, 3)]
        re = RewardEvaluator(params_test)
        self.assertEqual(re.get_way_point(0), (0, 0))
        self.assertEqual(re.get_way_point(1), (1, 0))
        self.assertEqual(re.get_way_point(2), (2, 0))
        self.assertEqual(re.get_way_point(3), (3, 3))
        self.assertEqual(re.get_way_point(4), (0, 0))
        self.assertEqual(re.get_way_point(5), (1, 0))
        self.assertEqual(re.get_way_point(-1), (3, 3))
        self.assertEqual(re.get_way_point(-2), (2, 0))
        self.assertEqual(re.get_way_point(-3), (1, 0))

    def test_get_way_points_distance(self):
        params_test = get_test_params()
        re = RewardEvaluator(params_test)
        self.assertEqual(re.get_way_points_distance((0, 0), (2, 0)), 2)
        self.assertEqual(re.get_way_points_distance((0, 0), (2, 2)), math.sqrt(8))
        self.assertEqual(re.get_way_points_distance((-2, 4), (-4, 2)), math.sqrt(8))
        self.assertEqual(re.get_way_points_distance((0, 0), (1, 0)), 1)

    def test_get_heading_between_waypoints(self):
        params_test = get_test_params()
        re = RewardEvaluator(params_test)
        self.assertEqual(re.get_heading_between_waypoints((0, 0), (2, 0)), 0)
        self.assertEqual(re.get_heading_between_waypoints((0, 0), (0, 2)), 90)
        self.assertEqual(re.get_heading_between_waypoints((0, 0), (0, -2)), -90)
        self.assertEqual(re.get_heading_between_waypoints((0, 0), (2, 2)), 45)
        self.assertEqual(re.get_heading_between_waypoints((0, 0), (-2, -2)), -135)

    def test_get_car_heading_error(self):
        params_test = get_test_params()
        params_test['heading'] = 0
        params_test['waypoints'] = [(0, 0), (2, 0), (2, 2), (0, 2), (0, 0), (2, 2), (4, 0)]
        params_test['closest_waypoints'] = [0, 1]
        re = RewardEvaluator(params_test)
        self.assertEqual(re.get_car_heading_error(), 0)
        params_test['closest_waypoints'] = [1, 2]
        re = RewardEvaluator(params_test)
        self.assertEqual(re.get_car_heading_error(), 90)
        params_test['closest_waypoints'] = [2, 3]
        re = RewardEvaluator(params_test)
        self.assertEqual(re.get_car_heading_error(), 180)
        params_test['closest_waypoints'] = [3, 4]
        re = RewardEvaluator(params_test)
        self.assertEqual(re.get_car_heading_error(), -90)
        params_test['closest_waypoints'] = [4, 5]
        re = RewardEvaluator(params_test)
        self.assertEqual(re.get_car_heading_error(), 45)
        params_test['closest_waypoints'] = [5, 6]
        re = RewardEvaluator(params_test)
        self.assertEqual(re.get_car_heading_error(), -45)

    def test_get_optimum_speed_ratio(self):
        params_test = get_test_params()
        params_test['heading'] = 0
        params_test['distance_from_center'] = 0
        params_test['steering_angle'] = 0
        params_test['closest_waypoints'] = (0, 1)
        params_test['x'] = params_test['waypoints'][params_test['closest_waypoints'][0]][0]
        params_test['y'] = params_test['waypoints'][params_test['closest_waypoints'][0]][1]
        re = RewardEvaluator(params_test)
        self.assertEqual(re.get_optimum_speed_ratio(), 1.0)
        params_test['closest_waypoints'] = (9, 10)
        params_test['x'] = params_test['waypoints'][params_test['closest_waypoints'][0]][0]
        params_test['y'] = params_test['waypoints'][params_test['closest_waypoints'][0]][1]
        re = RewardEvaluator(params_test)
        self.assertEqual(re.get_optimum_speed_ratio(), 0.66)
        params_test['closest_waypoints'] = (10, 11)
        params_test['x'] = params_test['waypoints'][params_test['closest_waypoints'][0]][0]
        params_test['y'] = params_test['waypoints'][params_test['closest_waypoints'][0]][1]
        re = RewardEvaluator(params_test)
        self.assertEqual(re.get_optimum_speed_ratio(), 0.33)

        params_test = get_test_params()
        params_test['distance_from_center'] = 0
        params_test['steering_angle'] = 0
        params_test['closest_waypoints'] = (0, 1)
        params_test['x'] = params_test['waypoints'][params_test['closest_waypoints'][0]][0]
        params_test['y'] = params_test['waypoints'][params_test['closest_waypoints'][0]][1]
        params_test['heading'] = 1.1 * re.MAX_STEERING_ANGLE
        re = RewardEvaluator(params_test)
        self.assertEqual(re.get_optimum_speed_ratio(), 0.34)
        params_test['heading'] = 1.1 * (re.MAX_STEERING_ANGLE * 0.75)
        re = RewardEvaluator(params_test)
        self.assertEqual(re.get_optimum_speed_ratio(), 0.67)
        # self.print_get_optimum_speed_ratio()

    def test_is_in_optimized_corridor(self):
        params_test = get_test_params()
        params_test['heading'] = 0
        params_test['track_width'] = 2
        params_test['distance_from_center'] = 0
        params_test['is_left_of_center'] = True
        params_test['steering_angle'] = 0
        params_test['closest_waypoints'] = (0, 1)
        params_test['x'] = params_test['waypoints'][params_test['closest_waypoints'][0]][0]
        params_test['y'] = params_test['waypoints'][params_test['closest_waypoints'][0]][1]

        # Center line - in corridor (left and right)
        re = RewardEvaluator(params_test)
        self.assertEqual(re.is_in_optimized_corridor(), True)
        params_test['is_left_of_center'] = False
        re = RewardEvaluator(params_test)
        self.assertEqual(re.is_in_optimized_corridor(), True)

        # Center line - out of corridor (left and right)
        params_test['distance_from_center'] = re.CENTERLINE_FOLLOW_RATIO_TRESHOLD * 2.2 * re.track_width
        params_test['is_left_of_center'] = True
        re = RewardEvaluator(params_test)
        self.assertEqual(re.is_in_optimized_corridor(), False)
        params_test['is_left_of_center'] = False
        re = RewardEvaluator(params_test)
        self.assertEqual(re.is_in_optimized_corridor(), False)

        # BEFORE TURN LEFT  - in corridor more right
        params_test['closest_waypoints'] = (8, 9)
        params_test['distance_from_center'] = re.CENTERLINE_FOLLOW_RATIO_TRESHOLD * 2.2 * re.track_width
        params_test['is_left_of_center'] = True
        re = RewardEvaluator(params_test)
        self.assertEqual(re.is_in_optimized_corridor(), False)
        params_test['is_left_of_center'] = False
        re = RewardEvaluator(params_test)
        self.assertEqual(re.is_in_optimized_corridor(), False)

        params_test['distance_from_center'] = re.CENTERLINE_FOLLOW_RATIO_TRESHOLD * 0.4 * re.track_width
        params_test['is_left_of_center'] = True
        re = RewardEvaluator(params_test)
        self.assertEqual(re.is_in_optimized_corridor(), True)
        params_test['is_left_of_center'] = False
        re = RewardEvaluator(params_test)
        self.assertEqual(re.is_in_optimized_corridor(), True)

        params_test['distance_from_center'] = re.CENTERLINE_FOLLOW_RATIO_TRESHOLD * 0.8 * re.track_width
        params_test['is_left_of_center'] = True
        re = RewardEvaluator(params_test)
        self.assertEqual(re.is_in_optimized_corridor(), False)
        params_test['is_left_of_center'] = False
        re = RewardEvaluator(params_test)
        self.assertEqual(re.is_in_optimized_corridor(), True)

        # TEST IN CURVE - vnitrni strana
        params_test['closest_waypoints'] = (15, 16)
        params_test['distance_from_center'] = re.CENTERLINE_FOLLOW_RATIO_TRESHOLD * 2.2 * re.track_width
        params_test['is_left_of_center'] = True
        re = RewardEvaluator(params_test)
        self.assertEqual(re.is_in_optimized_corridor(), False)
        params_test['is_left_of_center'] = False
        re = RewardEvaluator(params_test)
        self.assertEqual(re.is_in_optimized_corridor(), False)

        params_test['distance_from_center'] = re.CENTERLINE_FOLLOW_RATIO_TRESHOLD * 0.4 * re.track_width
        params_test['is_left_of_center'] = True
        re = RewardEvaluator(params_test)
        self.assertEqual(re.is_in_optimized_corridor(), True)
        params_test['is_left_of_center'] = False
        re = RewardEvaluator(params_test)
        self.assertEqual(re.is_in_optimized_corridor(), True)

        # Prujezd zatacka vnitrni strana
        params_test['distance_from_center'] = re.CENTERLINE_FOLLOW_RATIO_TRESHOLD * 0.8 * re.track_width
        params_test['is_left_of_center'] = True
        re = RewardEvaluator(params_test)
        self.assertEqual(re.is_in_optimized_corridor(), True)
        params_test['is_left_of_center'] = False
        re = RewardEvaluator(params_test)
        self.assertEqual(re.is_in_optimized_corridor(), False)

    def print_get_optimum_speed_ratio(self):
        params_test = get_test_params()
        params_test['distance_from_center'] = 0
        params_test['steering_angle'] = 0
        ind = 0
        for w in params_test['waypoints']:
            params_test['closest_waypoints'][0] = ind
            params_test['closest_waypoints'][1] = ind + 1
            params_test['x'] = w[0]
            params_test['y'] = w[1]
            re = RewardEvaluator(params_test)
            params_test['heading'] = re.get_heading_between_waypoints(w, re.get_way_point(ind + 1))
            # params_test['heading'] = params_test['heading'] + 1
            re.init_self(params_test)
            print(str(ind) + " speed ratio : " + str(re.get_optimum_speed_ratio()))
            ind = ind + 1
        print(" ")

    def print_is_in_turn(self):
        params_test = get_test_params()
        params_test['distance_from_center'] = 0
        params_test['steering_angle'] = 0
        ind = 0
        for w in params_test['waypoints']:
            params_test['closest_waypoints'][0] = ind
            params_test['closest_waypoints'][1] = ind + 1
            re = RewardEvaluator(params_test)
            re.init_self(params_test)
            print(str(ind) + " is_in_turn : " + str(re.is_in_turn()))
            ind = ind + 1
        print(" ")

    def test_is_in_turn(self):
        params_test = get_test_params()
        params_test['heading'] = 0
        params_test['waypoints'] = [(0, 0), (1, 0), (2, 0), (3, 1), (4, 1), (5, 1), (6, -6), (-1, -6), (-1, 0)]
        params_test['closest_waypoints'] = (0, 1)
        re = RewardEvaluator(params_test)
        self.assertEqual(re.is_in_turn(), False)
        params_test['closest_waypoints'] = (1, 2)
        re = RewardEvaluator(params_test)
        self.assertEqual(re.is_in_turn(), False)
        params_test['closest_waypoints'] = (2, 3)
        re = RewardEvaluator(params_test)
        self.assertEqual(re.is_in_turn(), True)
        params_test['closest_waypoints'] = (5, 6)
        re = RewardEvaluator(params_test)
        self.assertEqual(re.is_in_turn(), True)

    def print_get_turn_angle(self):
        params_test = get_test_params()
        params_test['distance_from_center'] = 0
        params_test['steering_angle'] = 0
        ind = 0
        for w in params_test['waypoints']:
            params_test['closest_waypoints'][0] = ind
            params_test['closest_waypoints'][1] = ind + 1
            re = RewardEvaluator(params_test)
            re.init_self(params_test)
            print(str(ind) + " get_turn_angle : {0:.1f}".format(re.get_turn_angle()))
            ind = ind + 1
        print(" ")

    def print_get_expected_turn_direction(self):
        params_test = get_test_params()
        params_test['distance_from_center'] = 0
        params_test['steering_angle'] = 0
        ind = 0
        for w in params_test['waypoints']:
            params_test['closest_waypoints'][0] = ind
            params_test['closest_waypoints'][1] = ind + 1
            re = RewardEvaluator(params_test)
            re.init_self(params_test)
            print(str(ind) + " getCurveDirectio : " + re.get_expected_turn_direction())
            ind = ind + 1
        print(" ")

    def test_get_turn_angle(self):
        params_test = get_test_params()
        params_test['heading'] = 0
        params_test['waypoints'] = [(0, 0), (1, 0), (2, 0), (3, 1), (4, 1), (5, 1), (6, -6), (-1, -6), (-1, 0)]
        params_test['closest_waypoints'] = (0, 1)
        re = RewardEvaluator(params_test)
        self.assertEqual(re.get_turn_angle(), 0)
        params_test['closest_waypoints'] = (1, 2)
        re = RewardEvaluator(params_test)
        self.assertEqual(re.get_turn_angle(), 0)
        params_test['closest_waypoints'] = (2, 3)
        re = RewardEvaluator(params_test)
        self.assertEqual(re.get_turn_angle(), 45)
        params_test['closest_waypoints'] = (5, 6)
        re = RewardEvaluator(params_test)
        self.assertEqual(re.get_turn_angle(), -81.86989764584403)

    def test_reached_target(self):
        params_test = get_test_params()
        max_way_point_index = len(params_test['waypoints']) - 1
        params_test['closest_waypoints'] = (max_way_point_index - 1, max_way_point_index)
        re = RewardEvaluator(params_test)
        self.assertEqual(re.reached_target(), True)
        max_way_point_index = len(params_test['waypoints']) - 5
        params_test['closest_waypoints'] = (max_way_point_index - 1, max_way_point_index)
        re = RewardEvaluator(params_test)
        self.assertEqual(re.reached_target(), False)

    def test_evaluation(self):
        params_test = get_test_params()
        params_test['heading'] = 0
        params_test['track_width'] = 10
        params_test['distance_from_center'] = 0
        params_test['is_left_of_center'] = True
        params_test['steering_angle'] = 0
        params_test['closest_waypoints'] = (0, 1)
        params_test['speed'] = 3
        params_test['x'] = params_test['waypoints'][params_test['closest_waypoints'][0]][0]
        params_test['y'] = params_test['waypoints'][params_test['closest_waypoints'][0]][1]
        re = RewardEvaluator(params_test)
        re.evaluate()

        params_test = get_test_params()
        params_test['heading'] = 0
        params_test['track_width'] = 10
        params_test['distance_from_center'] = 0
        params_test['is_left_of_center'] = True
        params_test['steering_angle'] = 0
        params_test['closest_waypoints'] = (69, 70)
        params_test['speed'] = 3
        params_test['x'] = params_test['waypoints'][params_test['closest_waypoints'][0]][0]
        params_test['y'] = params_test['waypoints'][params_test['closest_waypoints'][0]][1]
        re = RewardEvaluator(params_test)
        re.evaluate()

        # self.print_is_in_turn()
        # self.print_get_turn_angle()
        # self.print_get_expected_turn_direction()


if __name__ == '__main__':
    unittest.main()
