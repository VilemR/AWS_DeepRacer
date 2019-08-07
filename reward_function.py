# -*- coding: utf-8 -*-


import math
import traceback


class RewardEvaluator:

    # CALCULATION CONSTANTS - change for the performance fine tuning

    # Define minimum and maximum expected spped interval for the training. Both values should be corresponding to
    # parameters you are going to use for the Action space. Set MAX_SPEED equal to maximum speed defined there,
    # MIN_SPEED should be lower (just a bit) then expected minimum defined speed (e.g. Max speed set to 5 m/s,
    # speed granularity 3 => therefore MIN_SPEED should be less than 1.66 m/s.
    MAX_SPEED = float(5.0)
    MIN_SPEED = float(1.5)

    # Define maximum steering angle according to the Action space settings. Smooth steering angle treshold is used to
    # set a steering angle still considered as "smooth". The value must be higher than minumum steering angle determined
    # by the steering Action space. E.g Max steering 30 degrees, granularity 3 => SMOOTH_STEERING_ANGLE_TRESHOLD should be
    # higher than 10 degrees.
    MAX_STEERING_ANGLE = 30
    SMOOTH_STEERING_ANGLE_TRESHOLD = 15  # Vetsi nez min krok steering v prostoru

    # Constant value used to "ignore" turns in the corresponding distance (in meters). The car is supposed to drive
    # at MAX_SPEED (getting higher reward). In case within the distance is a turn, the car is rewarded when slowing down.
    SAFE_HORIZON_DISTANCE = 0.8  # meters, able to fully stop. See ANGLE_IS_CURVE.

    # Constand to define accepted distance of the car from the center line.
    CENTERLINE_FOLLOW_RATIO_TRESHOLD = 0.12

    # Constant to define a treshold (in degrees), representing max. angle within SAFE_HORIZON_DISTANCE. If the car is
    # supposed to start steering and the angle of the farest wayipont is above the treshold, the car is supposed to
    # slow down
    ANGLE_IS_CURVE = 3

    # A range the reward value mut fit in.
    PENALTY_MAX = 0.001
    REWARD_MAX = 89999  # 100000

    # params is a set of input values provided by the DeepRacer environment. For each calculation
    # this is provided
    params = None

    # Class properties - status values extracted from "params" input
    all_wheels_on_track = None
    x = None
    y = None
    distance_from_center = None
    is_left_of_center = None
    is_reversed = None
    heading = None
    progress = None
    steps = None
    speed = None
    steering_angle = None
    track_width = None
    waypoints = None
    closest_waypoints = None
    nearest_previous_waypoint_ind = None
    nearest_next_waypoint_ind = None

    log_message = ""

    # method used to extract class properties (status values) from input "params"
    def initSelf(self, params):
        self.all_wheels_on_track = params['all_wheels_on_track']
        self.x = params['x']
        self.y = params['y']
        self.distance_from_center = params['distance_from_center']
        self.is_left_of_center = params['is_left_of_center']
        self.is_reversed = params['is_reversed']
        self.heading = params['heading']
        self.progress = params['progress']
        self.steps = params['steps']
        self.speed = params['speed']
        self.steering_angle = params['steering_angle']
        self.track_width = params['track_width']
        self.waypoints = params['waypoints']
        self.closest_waypoints = params['closest_waypoints']
        self.nearest_previous_waypoint_ind = params['closest_waypoints'][0]
        self.nearest_next_waypoint_ind = params['closest_waypoints'][1]

    # RewardEvaluator Class constructor
    def __init__(self, params):
        self.params = params
        self.initSelf(params)

    # Method used to "print" status values and logged messages into AWS log. Be aware of additional cost Amazon will
    # charge you when logging is used heavily!!!
    def statusToString(self):
        status = self.params
        if 'waypoints' in status: del status['waypoints']
        status['debug_log'] = self.log_message
        print(status)

    # Gets ind'th wayipont from the list of all waypoints retrieved in params['waypoints']. Waypoints are circuit track
    # specific (everytime params is provided it is same list for particular circuit). If index is out of range (greater
    # than len(params['waypoints']) a waypoint from the beginning of the list ir returned.
    def getWayPoint(self, ind):
        if ind > (len(self.waypoints) - 1):
            return self.waypoints[ind - (len(self.waypoints))]
        elif ind < 0:
            return self.waypoints[len(self.waypoints) + ind]
        else:
            return self.waypoints[ind]

    # Calculates distance [m] between two waypoints [x1,y1] and [x2,y2]
    def getWayPointsDistance(self, prev_point, next_point):
        return math.sqrt(pow(next_point[1] - prev_point[1], 2) + pow(next_point[0] - prev_point[0], 2))

    # Calculates heading direction between two waypoints - angle in cartesian layout. Clockwise values
    # 0 to -180 degrees, anti clockwise 0 to +180 degrees
    def getHeadingBetweenWayPoints(self, prev_point, next_point):
        track_direction = math.atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0])
        return math.degrees(track_direction)

    # Calculates misalinmet of the heading of the car () compared to center line of the track (defined by previous and
    # the next waypoint (the car is between them)
    def getCarHeadingError(self):  # track direction vs heading (natoceni auta vuci trati)
        next_point = self.getWayPoint(self.closest_waypoints[1])
        prev_point = self.getWayPoint(self.closest_waypoints[0])
        track_direction = math.atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0])
        track_direction = math.degrees(track_direction)
        return (track_direction - self.heading)

    # Based on CarHeadingError (how much the car is misaligned with th direction of the track) and based on the "safe
    # horizon distance it is indicating the current speed (params['speed']) is/not optimal.
    def getOptimumSpeedRatio(self):
        if abs(self.getCarHeadingError()) >= self.MAX_STEERING_ANGLE:
            return float(0.34)
        if abs(self.getCarHeadingError()) >= (self.MAX_STEERING_ANGLE * 0.75):
            return float(0.67)
        pos = (self.x, self.y)
        currind = self.closest_waypoints[1]
        len = self.getWayPointsDistance((self.x, self.y), self.getWayPoint(currind))
        current_track_heading = self.getHeadingBetweenWayPoints(self.getWayPoint(currind),
                                                                self.getWayPoint(currind + 1))
        while True:
            from_point = self.getWayPoint(currind)
            to_point = self.getWayPoint(currind + 1)
            len = len + self.getWayPointsDistance(from_point, to_point)
            if len >= self.SAFE_HORIZON_DISTANCE:
                heading_to_horizont_point = self.getHeadingBetweenWayPoints(self.getWayPoint(self.closest_waypoints[1]), to_point)
                if abs(current_track_heading - heading_to_horizont_point) > (self.MAX_STEERING_ANGLE * 0.5):
                    return float(0.33)
                elif abs(current_track_heading - heading_to_horizont_point) > (self.MAX_STEERING_ANGLE * 0.25):
                    return float(0.66)
                else:
                    return float(1.0)
            currind = currind + 1

    # Calculates angle of the turn the car is right now (degrees). It is angle between previous and next segment of the
    # track (previous_waypoint - closest_waypoint and closest_waypoint - next_waypoint)
    def getCurveAngle(self):
        current_waypoint = self.closest_waypoints[0]
        angle_ahead = self.getHeadingBetweenWayPoints(self.getWayPoint(current_waypoint),
                                                      self.getWayPoint(current_waypoint + 1))
        angle_behind = self.getHeadingBetweenWayPoints(self.getWayPoint(current_waypoint - 1),
                                                       self.getWayPoint(current_waypoint))
        retval = angle_ahead - angle_behind
        if angle_ahead < -90 and angle_behind > 90:
            return 360 + retval
        elif retval > 180:
            return -180 + (retval - 180)
        elif retval < -180:
            return 180 - (retval + 180)
        else:
            return retval

    # Indicates the car is in turn
    def isInCurve(self):
        if abs(self.getCurveAngle()) >= self.ANGLE_IS_CURVE:
            return True
        else:
            return False
        return False

    # Indicates the car has reached final waypoint of the circuit track
    def reachedTarget(self):
        max_way_point_ind = len(self.waypoints) - 1
        if self.closest_waypoints[1] == max_way_point_ind:
            return True
        else:
            return False

    # Provides direction of the next turn in order to let you reward right position to the center line (before the left
    # turn position of the car sligthly right can be rewarded (and vice versa) - see isInOptimizedCorridor()
    def getExpectedTurnDirection(self):
        pos = (self.x, self.y)
        currind = self.closest_waypoints[1]
        len = self.getWayPointsDistance((self.x, self.y), self.getWayPoint(currind))
        while True:
            from_point = self.getWayPoint(currind)
            to_point = self.getWayPoint(currind + 1)
            len = len + self.getWayPointsDistance(from_point, to_point)
            if len >= self.SAFE_HORIZON_DISTANCE * 4.5:
                retval = self.getHeadingBetweenWayPoints(self.getWayPoint(self.closest_waypoints[1]), to_point)
                if retval > 2:
                    return "LEFT"
                elif retval < -2:
                    return "RIGHT"
                else:
                    return "STRAIGHT"
            currind = currind + 1

    # Based on the direction of the next turn it indicates the car is on the right side to the center line in order to
    # drive through smoothly - see getExpectedTurnDirection().
    def isInOptimizedCorridor(self):
        if self.isInCurve():
            curve_angle = self.getCurveAngle()
            if curve_angle > 0:  # Turning LEFT - better be by left side
                if (self.is_left_of_center == True and self.distance_from_center <= (
                        self.CENTERLINE_FOLLOW_RATIO_TRESHOLD * 2 * self.track_width) or
                        self.is_left_of_center == False and self.distance_from_center <= (
                                self.CENTERLINE_FOLLOW_RATIO_TRESHOLD / 2 * self.track_width)):
                    return True
                else:
                    return False
            else:  # Turning RIGHT - better be by right side
                if self.is_left_of_center == True and self.distance_from_center <= (self.CENTERLINE_FOLLOW_RATIO_TRESHOLD / 2 * self.track_width) or
                   self.is_left_of_center == False and self.distance_from_center <= (self.CENTERLINE_FOLLOW_RATIO_TRESHOLD * 2 * self.track_width):
                    return True
                else:
                    return False
        else:
            next_turn = self.getExpectedTurnDirection()
            if next_turn == "LEFT":  # Be more righ side before turn
                if self.is_left_of_center == True and self.distance_from_center <= (
                        self.CENTERLINE_FOLLOW_RATIO_TRESHOLD / 2 * self.track_width) or
                        self.is_left_of_center == False and self.distance_from_center <= (
                                self.CENTERLINE_FOLLOW_RATIO_TRESHOLD * 2 * self.track_width):
                    return True
                else:
                    return False
            elif next_turn == "RIGHT":  # Be more left side before turn:
                if self.is_left_of_center == True and self.distance_from_center <= (
                        self.CENTERLINE_FOLLOW_RATIO_TRESHOLD * 2 * self.track_width) or
                        self.is_left_of_center == False and self.distance_from_center <= (
                                self.CENTERLINE_FOLLOW_RATIO_TRESHOLD / 2 * self.track_width):
                    return True
                else:
                    return False
            else:  # Be aligned with center line:
                if self.distance_from_center <= (self.CENTERLINE_FOLLOW_RATIO_TRESHOLD * 2 * self.track_width):
                    return True
                else:
                    return False

    def isOptimumSpeed(self):
        if abs(self.speed - (self.getOptimumSpeedRatio() * self.MAX_SPEED)) < (self.MAX_SPEED * 0.15) and self.MIN_SPEED <= self.speed <= self.MAX_SPEED:
            return True
        else:
            return False

    # Accumulates all logging messages into one string which you may need to write to the log (uncomment line
    # self.statusToString() in evaluate() if you want to log status and calculation outputs.
    def logFeature(self, message):
        if message is None:
            message = 'NULL'
        self.log_message = self.log_message + str(message) + '|'

    # Here you can implement your logic to calculate reward value based on input parameters (params) and use
    # implemented features (as methods above)
    def evaluate(self):
        self.initSelf(self.params)
        retval = float(0.001)
        try:
            # No reward => Fatal behaviour, NOREWARD!  (out of track, reversed, sleeping)
            if self.all_wheels_on_track == False or self.is_reversed == True or (self.speed < (0.1 * self.MAX_SPEED)):
                self.logFeature("all_wheels_on_track or is_reversed issue")
                self.statusToString()
                return float(self.PENALTY_MAX)

            # REWARD 50 - EARLY Basic learning => easy factors accelerate learning
            # Right heading, no crazy steering
            if abs(self.getCarHeadingError()) <= self.SMOOTH_STEERING_ANGLE_TRESHOLD:
                self.logFeature("getCarHeadingOK")
                retval = retval + self.REWARD_MAX * 0.3

            if abs(self.steering_angle) <= self.SMOOTH_STEERING_ANGLE_TRESHOLD:
                self.logFeature("getSteeringAngleOK")
                retval = retval + self.REWARD_MAX * 0.15

            # REWARD100 - LATER ADVANCED complex learning
            # Ideal path, speed wherever possible, carefully in corners
            if self.isInOptimizedCorridor():
                self.logFeature("isInOptimizedCorridor")
                retval = retval + float(self.REWARD_MAX * 0.45)

            if not (self.isInCurve()) and (abs(self.speed - self.MAX_SPEED) < (0.1 * self.MAX_SPEED)) \
                    and abs(self.getCarHeadingError()) <= self.SMOOTH_STEERING_ANGLE_TRESHOLD:
                self.logFeature("isStraightOnMaxSpeed")
                retval = retval + float(self.REWARD_MAX * 1)

            if self.isInCurve() and self.isOptimumSpeed():
                self.logFeature("isOptimumSpeedinCurve")
                retval = retval + float(self.REWARD_MAX * 0.6)

            # REWAR - Progress bonus
            TOTAL_NUM_STEPS = 150
            if (self.steps % 100 == 0) and self.progress > (self.steps / TOTAL_NUM_STEPS):
                self.logFeature("progressingOk")
                retval = retval + self.REWARD_MAX * 0.4

            # Reach Max Waypoint - get extra reward
            if self.reachedTarget():
                self.logFeature("reachedTarget")
                retval = float(self.REWARD_MAX)

        except Exception as e:
            print("Error : " + str(e))
            print(traceback.format_exc())

        # Finally - check reward value does not exceed maximum value
        if retval > 900000:
            retval = 900000

        self.logFeature(retval)
        # self.statusToString()

        return float(retval)

"""
This is the core function called by the environment to calculate reward value for every point of time of the training. 
params : input values for the reward calculation (see above)

Usually this function contains all reward calculations an logic implemented. Instead, this code example is instantiating 
RewardEvaluator which has implemented set of features one can easily combine and use.
"""

def reward_function(params):
    re = RewardEvaluator(params)
    return float(re.evaluate())
