# -*- coding: utf-8 -*-

import math
import unittest

from tests.parms.parms import getCopyOfParm as getParm
from reward_function import RewardEvaluator


class RewardEvaluatorTestCase(unittest.TestCase):

    def test_getWayPoint(self):
        prmTest = getParm()
        prmTest['waypoints'] = [(0, 0), (1, 0), (2, 0), (3, 3)]
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.getWayPoint(0), (0, 0))
        self.assertEqual(re.getWayPoint(1), (1, 0))
        self.assertEqual(re.getWayPoint(2), (2, 0))
        self.assertEqual(re.getWayPoint(3), (3, 3))
        self.assertEqual(re.getWayPoint(4), (0, 0))
        self.assertEqual(re.getWayPoint(5), (1, 0))
        self.assertEqual(re.getWayPoint(-1), (3, 3))
        self.assertEqual(re.getWayPoint(-2), (2, 0))
        self.assertEqual(re.getWayPoint(-3), (1, 0))

    def test_getWayPontsDistance(self):
        prmTest = getParm()
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.getWayPointsDistance((0, 0), (2, 0)), 2)
        self.assertEqual(re.getWayPointsDistance((0, 0), (2, 2)), math.sqrt(8))
        self.assertEqual(re.getWayPointsDistance((-2, 4), (-4, 2)), math.sqrt(8))
        self.assertEqual(re.getWayPointsDistance((0, 0), (1, 0)), 1)

    def test_getHeadingBetweenWayPoints(self):
        prmTest = getParm()
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.getHeadingBetweenWayPoints((0, 0), (2, 0)), 0)
        self.assertEqual(re.getHeadingBetweenWayPoints((0, 0), (0, 2)), 90)
        self.assertEqual(re.getHeadingBetweenWayPoints((0, 0), (0, -2)), -90)
        self.assertEqual(re.getHeadingBetweenWayPoints((0, 0), (2, 2)), 45)
        self.assertEqual(re.getHeadingBetweenWayPoints((0, 0), (-2, -2)), -135)

    def test_getCarHeadingError(self):
        prmTest = getParm()
        prmTest['heading'] = 0
        prmTest['waypoints'] = [(0, 0), (2, 0), (2, 2), (0, 2), (0, 0), (2, 2), (4, 0)]
        prmTest['closest_waypoints'] = [0, 1]
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.getCarHeadingError(), 0)
        prmTest['closest_waypoints'] = [1, 2]
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.getCarHeadingError(), 90)
        prmTest['closest_waypoints'] = [2, 3]
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.getCarHeadingError(), 180)
        prmTest['closest_waypoints'] = [3, 4]
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.getCarHeadingError(), -90)
        prmTest['closest_waypoints'] = [4, 5]
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.getCarHeadingError(), 45)
        prmTest['closest_waypoints'] = [5, 6]
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.getCarHeadingError(), -45)

    def test_getOptimumSpeedRatio(self):
        prmTest = getParm()
        prmTest['heading'] = 0
        prmTest['distance_from_center'] = 0
        prmTest['steering_angle'] = 0
        prmTest['closest_waypoints'] = (0, 1)
        prmTest['x'] = prmTest['waypoints'][prmTest['closest_waypoints'][0]][0]
        prmTest['y'] = prmTest['waypoints'][prmTest['closest_waypoints'][0]][1]
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.getOptimumSpeedRatio(), 1.0)
        prmTest['closest_waypoints'] = (9, 10)
        prmTest['x'] = prmTest['waypoints'][prmTest['closest_waypoints'][0]][0]
        prmTest['y'] = prmTest['waypoints'][prmTest['closest_waypoints'][0]][1]
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.getOptimumSpeedRatio(), 0.66)
        prmTest['closest_waypoints'] = (10, 11)
        prmTest['x'] = prmTest['waypoints'][prmTest['closest_waypoints'][0]][0]
        prmTest['y'] = prmTest['waypoints'][prmTest['closest_waypoints'][0]][1]
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.getOptimumSpeedRatio(), 0.33)

        prmTest = getParm()
        prmTest['distance_from_center'] = 0
        prmTest['steering_angle'] = 0
        prmTest['closest_waypoints'] = (0, 1)
        prmTest['x'] = prmTest['waypoints'][prmTest['closest_waypoints'][0]][0]
        prmTest['y'] = prmTest['waypoints'][prmTest['closest_waypoints'][0]][1]
        prmTest['heading'] = 1.1 * re.MAX_STEERING_ANGLE
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.getOptimumSpeedRatio(), 0.34)
        prmTest['heading'] = 1.1 * (re.MAX_STEERING_ANGLE * 0.75)
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.getOptimumSpeedRatio(), 0.67)
        # self.print_getOptimumSpeedRatio()

    def test_isInOptimizedCorridor(self):
        prmTest = getParm()
        prmTest['heading'] = 0
        prmTest['track_width'] = 2
        prmTest['distance_from_center'] = 0
        prmTest['is_left_of_center'] = True
        prmTest['steering_angle'] = 0
        prmTest['closest_waypoints'] = (0, 1)
        prmTest['x'] = prmTest['waypoints'][prmTest['closest_waypoints'][0]][0]
        prmTest['y'] = prmTest['waypoints'][prmTest['closest_waypoints'][0]][1]

        # Center line - in corridor (left and right)
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.isInOptimizedCorridor(), True)
        prmTest['is_left_of_center'] = False
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.isInOptimizedCorridor(), True)

        # Center line - out of corridor (left and right)
        prmTest['distance_from_center'] = re.CENTERLINE_FOLLOW_RATIO_TRESHOLD * 2.2 * re.track_width
        prmTest['is_left_of_center'] = True
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.isInOptimizedCorridor(), False)
        prmTest['is_left_of_center'] = False
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.isInOptimizedCorridor(), False)

        # BEFORE TURN LEFT  - in corridor more right
        prmTest['closest_waypoints'] = (8, 9)
        prmTest['distance_from_center'] = re.CENTERLINE_FOLLOW_RATIO_TRESHOLD * 2.2 * re.track_width
        prmTest['is_left_of_center'] = True
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.isInOptimizedCorridor(), False)
        prmTest['is_left_of_center'] = False
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.isInOptimizedCorridor(), False)

        prmTest['distance_from_center'] = re.CENTERLINE_FOLLOW_RATIO_TRESHOLD * 0.4 * re.track_width
        prmTest['is_left_of_center'] = True
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.isInOptimizedCorridor(), True)
        prmTest['is_left_of_center'] = False
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.isInOptimizedCorridor(), True)

        prmTest['distance_from_center'] = re.CENTERLINE_FOLLOW_RATIO_TRESHOLD * 0.8 * re.track_width
        prmTest['is_left_of_center'] = True
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.isInOptimizedCorridor(), False)
        prmTest['is_left_of_center'] = False
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.isInOptimizedCorridor(), True)

        # TEST IN CURVE - vnitrni strana
        prmTest['closest_waypoints'] = (15, 16)
        prmTest['distance_from_center'] = re.CENTERLINE_FOLLOW_RATIO_TRESHOLD * 2.2 * re.track_width
        prmTest['is_left_of_center'] = True
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.isInOptimizedCorridor(), False)
        prmTest['is_left_of_center'] = False
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.isInOptimizedCorridor(), False)

        prmTest['distance_from_center'] = re.CENTERLINE_FOLLOW_RATIO_TRESHOLD * 0.4 * re.track_width
        prmTest['is_left_of_center'] = True
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.isInOptimizedCorridor(), True)
        prmTest['is_left_of_center'] = False
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.isInOptimizedCorridor(), True)

        # Prujezd zatacka vnitrni strana
        prmTest['distance_from_center'] = re.CENTERLINE_FOLLOW_RATIO_TRESHOLD * 0.8 * re.track_width
        prmTest['is_left_of_center'] = True
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.isInOptimizedCorridor(), True)
        prmTest['is_left_of_center'] = False
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.isInOptimizedCorridor(), False)

    def print_getOptimumSpeedRatio(self):
        prmTest = getParm()
        prmTest['distance_from_center'] = 0
        prmTest['steering_angle'] = 0
        ind = 0
        for w in prmTest['waypoints']:
            prmTest['closest_waypoints'][0] = ind
            prmTest['closest_waypoints'][1] = ind + 1
            prmTest['x'] = w[0]
            prmTest['y'] = w[1]
            re = RewardEvaluator(prmTest)
            prmTest['heading'] = re.getHeadingBetweenWayPoints(w, re.getWayPoint(ind + 1))
            # prmTest['heading'] = prmTest['heading'] + 1
            re.initSelf(prmTest)
            print(str(ind) + " speed ratio : " + str(re.getOptimumSpeedRatio()))
            ind = ind + 1
        print(" ")

    def print_isInCurve(self):
        prmTest = getParm()
        prmTest['distance_from_center'] = 0
        prmTest['steering_angle'] = 0
        ind = 0
        for w in prmTest['waypoints']:
            prmTest['closest_waypoints'][0] = ind
            prmTest['closest_waypoints'][1] = ind + 1
            re = RewardEvaluator(prmTest)
            re.initSelf(prmTest)
            print(str(ind) + " isInCurve : " + str(re.isInCurve()))
            ind = ind + 1
        print(" ")

    def test_isInCurve(self):
        prmTest = getParm()
        prmTest['heading'] = 0
        prmTest['waypoints'] = [(0, 0), (1, 0), (2, 0), (3, 1), (4, 1), (5, 1), (6, -6), (-1, -6), (-1, 0)]
        prmTest['closest_waypoints'] = (0, 1)
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.isInCurve(), False)
        prmTest['closest_waypoints'] = (1, 2)
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.isInCurve(), False)
        prmTest['closest_waypoints'] = (2, 3)
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.isInCurve(), True)
        prmTest['closest_waypoints'] = (5, 6)
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.isInCurve(), True)

    def print_getCurveAngle(self):
        prmTest = getParm()
        prmTest['distance_from_center'] = 0
        prmTest['steering_angle'] = 0
        ind = 0
        for w in prmTest['waypoints']:
            prmTest['closest_waypoints'][0] = ind
            prmTest['closest_waypoints'][1] = ind + 1
            re = RewardEvaluator(prmTest)
            re.initSelf(prmTest)
            print(str(ind) + " getCurveAngle : {0:.1f}".format(re.getCurveAngle()))
            ind = ind + 1
        print(" ")

    def print_getExpectedTurnDirection(self):
        prmTest = getParm()
        prmTest['distance_from_center'] = 0
        prmTest['steering_angle'] = 0
        ind = 0
        for w in prmTest['waypoints']:
            prmTest['closest_waypoints'][0] = ind
            prmTest['closest_waypoints'][1] = ind + 1
            re = RewardEvaluator(prmTest)
            re.initSelf(prmTest)
            print(str(ind) + " getCurveDirectio : " + re.getExpectedTurnDirection())
            ind = ind + 1
        print(" ")

    def test_getCurveAngle(self):
        prmTest = getParm()
        prmTest['heading'] = 0
        prmTest['waypoints'] = [(0, 0), (1, 0), (2, 0), (3, 1), (4, 1), (5, 1), (6, -6), (-1, -6), (-1, 0)]
        prmTest['closest_waypoints'] = (0, 1)
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.getCurveAngle(), 0)
        prmTest['closest_waypoints'] = (1, 2)
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.getCurveAngle(), 0)
        prmTest['closest_waypoints'] = (2, 3)
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.getCurveAngle(), 45)
        prmTest['closest_waypoints'] = (5, 6)
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.getCurveAngle(), -81.86989764584403)

    def test_reachedTarget(self):
        prmTest = getParm()
        maxWayPointInd = len(prmTest['waypoints']) - 1
        prmTest['closest_waypoints'] = (maxWayPointInd - 1, maxWayPointInd)
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.reachedTarget(), True)
        maxWayPointInd = len(prmTest['waypoints']) - 5
        prmTest['closest_waypoints'] = (maxWayPointInd - 1, maxWayPointInd)
        re = RewardEvaluator(prmTest)
        self.assertEqual(re.reachedTarget(), False)

    def test_Evaluation(self):
        prmTest = getParm()
        prmTest['heading'] = 0
        prmTest['track_width'] = 10
        prmTest['distance_from_center'] = 0
        prmTest['is_left_of_center'] = True
        prmTest['steering_angle'] = 0
        prmTest['closest_waypoints'] = (0, 1)
        prmTest['speed'] = 3
        prmTest['x'] = prmTest['waypoints'][prmTest['closest_waypoints'][0]][0]
        prmTest['y'] = prmTest['waypoints'][prmTest['closest_waypoints'][0]][1]
        re = RewardEvaluator(prmTest)
        re.evaluate()

        prmTest = getParm()
        prmTest['heading'] = 0
        prmTest['track_width'] = 10
        prmTest['distance_from_center'] = 0
        prmTest['is_left_of_center'] = True
        prmTest['steering_angle'] = 0
        prmTest['closest_waypoints'] = (69, 70)
        prmTest['speed'] = 3
        prmTest['x'] = prmTest['waypoints'][prmTest['closest_waypoints'][0]][0]
        prmTest['y'] = prmTest['waypoints'][prmTest['closest_waypoints'][0]][1]
        re = RewardEvaluator(prmTest)
        re.evaluate()

        # self.print_isInCurve()
        # self.print_getCurveAngle()
        # self.print_getExpectedTurnDirection()


if __name__ == '__main__':
    unittest.main()
