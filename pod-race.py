import sys
import math

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

LIMIT_ANGLE_POWER = 80
LIMIT_ANGLE_BOOST = 30
LIMIT_DISTANCE_BOOST = 9000
POD_RADIUS = 400

THRUST_OFF_DIST = 1000
THRUST_OFF_ANGLE = 1110
THRUST_OFF_CLOSING_VEL = 50
BRAKET_ANGLE = 20

DIST_FUT_SHIELD = 850
MAX_THRUST = 200

class Map:
    def __init__(self):
        self.checkpoints = {}
        self.ithpoint = {}
        self.num_points = None
        self.current_index = 0
        self.current_xy = None

    def add(self, x, y):
        if self.current_xy == (x,y):
            return
        self.current_xy = (x,y)
        if (x, y) in self.checkpoints:
            if not self.num_points:
                self.num_points = self.current_index
            return
        self.current_index += 1
        self.checkpoints[(x,y)] = self.current_index
        self.ithpoint[self.current_index] = (x,y)

    def next_next(self, next_id):
        nextnext_i = next_id % self.num_points
        nextnext_i += 1
        return self.ithpoint[nextnext_i]

def angle_between_vectors(vx, vy, dx, dy):
    dot_product = vx * dx + vy * dy
    magnitude_v = math.sqrt(vx**2 + vy**2)
    magnitude_d = math.sqrt(dx**2 + dy**2)
    if magnitude_v == 0 or magnitude_d == 0:
        return 0
        raise ValueError("One of the vectors has zero length.")
    cos_theta = dot_product / (magnitude_v * magnitude_d)
    cos_theta = max(min(cos_theta, 1.0), -1.0)
    angle_radians = math.acos(cos_theta)
    sin_theta = (vx * dy - vy * dx) / (magnitude_v * magnitude_d)
    if sin_theta < 0:
        angle_radians = -angle_radians
    angle_degrees = math.degrees(angle_radians)
    return angle_degrees

def rotate(origin, point, angle):
    angle *= 0.01745329251
    ox, oy = origin.x, origin.y
    px, py = point.x, point.y

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return Pos(int(qx), int(qy))

track = Map()

class Pos():
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

    def dist(self, other):
        return math.sqrt((self.x-other.x)**2+(self.y-other.y)**2)

    def __repr__(self):
        return f"({self.x:04d},{self.y:04d})"

    def __add__(self, other):
        return Pos(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Pos(self.x - other.x, self.y - other.y)

    def __mul__(self, fac):
        return Pos(self.x * fac, self.y * fac)

    def __len__(self):
        return int(math.sqrt((self.x)**2+(self.y)**2))

    def dot(self, other):
        return self.x * other.x + self.y * other.y

laps = int(input())
checkpointCount = int(input())
checkpoints = []
for cp in range(checkpointCount):
    cpx, cpy=input().split()
    checkpoints.append(Pos(int(cpx), int(cpy)))
    track.add(int(cpx), int(cpy))
    track.num_points = checkpointCount

LIMIT_DISTANCE_BOOST = 0
for i in range(checkpointCount):
    d = (checkpoints+checkpoints)[i].dist((checkpoints+checkpoints)[i+1])
    if d > LIMIT_DISTANCE_BOOST:
        LIMIT_DISTANCE_BOOST = d

LIMIT_DISTANCE_BOOST -= 2000
print(f"{LIMIT_DISTANCE_BOOST=}", file=sys.stderr, flush=True)

class Pod:
    BOOST_AVAIL = 1
    
    def __init__(self, id: int):
        self.prev_dist = 0
        self.prev_angle = 0
        self.id = id
        self.nbr_cp = 0
        self.dev_extra = 0
        self.shield_no_thrust = 0
        self.is_bumper = False
        self.boost_avail = 1

    def can_boost(self, is_sim=False):
        return  self.boost_avail > 0 and self.BOOST_AVAIL > 0

    def update(self, in_str):
        x, y, vx, vy, angle, next_checkpoint_id = [int(i) for i in in_str.split()]
        self.next_id = next_checkpoint_id
        self.pos = Pos(x, y)
        self.vel = Pos(vx, vy)
        self.angle = (angle + 180) % 360 -180
        self.thrust = MAX_THRUST
        self.acc = rotate(Pos(0, 0), Pos(self.thrust, 0), self.angle)

        n = self.next_checkpoint()
        self.target = Pos(n.x, n.y)

        if self.next_id == (self.nbr_cp + 1) % checkpointCount:
            pass
        else:
            self.nbr_cp += 1

    def next_checkpoint(self, plus = 0):
        id = (self.next_id+plus) % checkpointCount
        return checkpoints[id]
    
    def next_dist(self):
        return int(self.next_checkpoint().dist(self.pos))

    def angle_to(self, to_pos):
        return int(angle_between_vectors(1,0 , to_pos.x-self.pos.x, to_pos.y-self.pos.y) + 180) % 360 - 180

    def angle_vel(self, to_pos):
        return int(angle_between_vectors(self.vel.x, self.vel.y, to_pos.x-self.pos.x, to_pos.y-self.pos.y) + 180) % 360 - 180

    def angle_aim_to_target(self):
        return int(self.angle_to(self.target) - self.angle + 180) % 360 - 180

    def angle_aim_to(self, to_pos):
        return int(self.angle_to(to_pos) - self.angle + 180) % 360 - 180

    def closing(self):
        return self.prev_dist - self.next_dist()

    def angle_closing(self, to_pos):
        return abs(self.angle_vel(to_pos)) - abs(self.prev_angle)

    def time_to_collision(self, other, radius=POD_RADIUS) -> float:
        pos1, vel1, acc1 = self.pos, self.vel, self.acc
        pos2, vel2, acc2 = other.pos, other.vel, other.acc
        rel_pos = pos2 - pos1
        rel_vel = vel2 - vel1
        rel_vel += (acc2 - acc1) * 0.5
        a = rel_vel.x ** 2 + rel_vel.y ** 2
        b = 2 * (rel_pos.x * rel_vel.x + rel_pos.y * rel_vel.y)
        c = rel_pos.x ** 2 + rel_pos.y ** 2 - (2 * radius) ** 2

        if a == 0:
            return None  # Parallel velocities
        
        discriminant = b ** 2 - 4 * a * c
        if discriminant < 0:
            return None  # No real roots, no collision
        
        t1 = (-b - math.sqrt(discriminant)) / (2 * a)
        t2 = (-b + math.sqrt(discriminant)) / (2 * a)
        
        if t1 >= 0 and t2 >= 0:
            return round(min(t1, t2), 2)
        elif t1 >= 0:
            return t1
        elif t2 >= 0:
            return t2
        else:
            return None  # No collision in the future


    def end_turn(self):
        self.prev_dist = self.next_dist()
        self.prev_angle = self.angle
        self.dev_extra = int(self.dev_extra * 0.9)
        if self.shield_no_thrust:
            self.shield_no_thrust -= 1
        if self.target == 'SHIELD':
            self.shield_no_thrust = 3

    def __repr__(self):
        return f"""id={self.id} nbr_cp={self.nbr_cp} next={self.next_id} pos={self.pos} vel={self.vel} acc={self.acc} a={self.angle:03} t={self.thrust} dev={self.dev_extra}"""

    def adjust_target(self):
        delta_to_target = self.angle_vel(self.target)
        # print(f"{delta_to_target=}", file=sys.stderr, flush=True)
        if abs(delta_to_target) >= 0:
            delta_rot = delta_to_target #* 0.5
            delta_rot = min(max(delta_rot, -BRAKET_ANGLE), BRAKET_ANGLE)
            # print(f"{delta_rot=} {self.pos=} {self.target=}", file=sys.stderr, flush=True)
            self.target = rotate(self.pos, self.target, delta_rot + self.dev_extra)
            # print(f"{self.target=}", file=sys.stderr, flush=True)

    def try_to_boost(self, is_sim=False):
        if self.can_boost():
            self.boost_avail -= 1
            if not is_sim:
                self.BOOST_AVAIL -= 1
            print(f"{self.id=} BOOOOOOOOOOOOOOOOOOOOOOOOOOOST {is_sim=}", file=sys.stderr, flush=True)
            return "BOOST"
        return MAX_THRUST

    def try_thrust(self, desired=MAX_THRUST):
        if self.shield_no_thrust:
            print(f"{self.id=} CANNOT THRUST {self.shield_no_thrust=}", file=sys.stderr, flush=True)
            return 0
        return desired
            
    def adjust_thrust(self, is_sim=False):
        # if self.is_bumper:
        #     if abs(self.angle_aim_to_target()) > 160 and turn != 0:
        #         self.thrust = 10
        #     return
        if abs(self.angle_aim_to_target()) > LIMIT_ANGLE_POWER and turn != 0:
            self.thrust = 10
        elif abs(self.angle_aim_to_target()) > LIMIT_ANGLE_POWER * 0.85 and turn != 0:
            self.thrust = self.try_thrust(MAX_THRUST // 2)

        if not self.is_bumper and self.id > 0:
            if abs(self.angle_aim_to_target()) < LIMIT_ANGLE_BOOST and (
                self.next_dist() > LIMIT_DISTANCE_BOOST or self.nbr_cp >= checkpointCount * laps - 1
                ):
                self.thrust = self.try_to_boost(is_sim=is_sim)

    def compute_bumper(self):
        other = pod1 if self.id == 2 else pod2
        pursuit = bad2 if bad2.nbr_cp-bad2.simulate(3).next_dist()*1e-6 > bad1.nbr_cp-bad1.simulate(3).next_dist()*1e-6 else bad1
        print(f"PURSUIT {self.id} -> {pursuit.id}", file=sys.stderr, flush=True)

        self.thrust = MAX_THRUST
        badnext = pursuit.next_checkpoint(plus=0)
        if pursuit.simulate(2).pos.dist(badnext) < self.simulate(2).pos.dist(badnext) * 1:
            self.target = pursuit.next_checkpoint(plus=1)
        else:
            self.target = badnext

        for i, fut in enumerate(self.sim_gen(6, thrust=0)):
            if fut.pos.dist(other.simulate(i).pos) < 3000:
                # self.target = rotate(self.pos, self.target, 90 if self.angle_aim_to_target() > 0 else -90)
                break
            if fut.pos.dist(self.target) < 3000:
                self.thrust=0
                self.target = pursuit.simulate(3).pos
                print(f"proximity {i=} {self.target=} {self.thrust=}", file=sys.stderr, flush=True)
                break

        if pursuit.simulate(2).pos.dist(badnext) > self.simulate(2).pos.dist(badnext) * 1.1:
            self.target = pursuit.simulate(4).pos
        # can we collide?
        for i, (futme, futpur) in enumerate(zip(
            self.sim_gen(6, target=pursuit.simulate(3, target=pursuit.next_checkpoint()).pos, thrust=MAX_THRUST), 
            pursuit.sim_gen(6)
            )):
            ft = i + 1
            t_col = futme.time_to_collision(futpur)
            print(f"{ft=} {t_col=} {self.id} -> {pursuit.id}  {self.vel=} {pursuit.vel=}", file=sys.stderr, flush=True)
            if t_col:
                taim = ft + int(t_col)
                print(f"PURSUIT collision? {ft=} {self.id}->{pursuit.id} in {t_col:.2f} {taim}", file=sys.stderr, flush=True)
                self.thrust = self.try_to_boost()
                self.target = pursuit.simulate(taim).pos
                break
        # if pursuit.pos.dist(badnext) > self.pos.dist(badnext) * 2:
        #     self.thrust = 0
        
        # avoid pod1
        # for i in range(0,3):
        #     if pod1.simulate(i).pos.dist(self.simulate(i).pos) < DIST_FUT_SHIELD:
        #         self.thrust = 0

        next_step = 1
        fut = self.simulate(next_step)
        for bad in [bad1, bad2]:
            t_col = self.time_to_collision(bad)
            if t_col:
                print(f"collision? {self.id}->{bad.id} in {t_col:.2f}", file=sys.stderr, flush=True)
            if t_col and t_col <= 1:
                # print(f"{fut.pos.dist(futbad1.pos)=}", file=sys.stderr, flush=True)
                self.thrust = 'SHIELD'

        fut_other = other.simulate(next_step)
        if fut.pos.dist(fut_other.pos) < DIST_FUT_SHIELD:
            self.target = rotate(self.pos, self.target, 90)

    def compute(self):
        if self.is_bumper:
           # pursuit of bad1/2 the first
            self.compute_bumper()
            self.adjust_target()
            self.adjust_thrust()
            return

        nxt_cp_dist = self.next_dist()
        nxt_cp_angle = self.angle_aim_to_target()
        print(f"{self.id} a{self.angle:03} {nxt_cp_dist=} {nxt_cp_angle=}", file=sys.stderr, flush=True)

        other = pod1 if self.id == 2 else pod2
        
        closing = self.closing()
        if nxt_cp_dist < THRUST_OFF_DIST + 10 * closing and closing > THRUST_OFF_CLOSING_VEL and self.nbr_cp < checkpointCount*laps-1:
            if nnxy := checkpoints[(self.next_id+1) % checkpointCount]:
                for i, fut in enumerate(self.sim_gen(nbr_of_turns=10, target=nnxy)):
                    dist_fut = fut.pos.dist(self.next_checkpoint())
                    print(f"{nnxy=}, d{int(dist_fut)} a{fut.angle}  A{fut.acc} V{fut.vel} P{fut.pos} T={fut.thrust}", file=sys.stderr, flush=True)
                    # print(f"{nnxy=}, {fut}", file=sys.stderr, flush=True)
                    if dist_fut < 500:
                        # no collisions
                        t_cols = [self.time_to_collision(p) for p in [other, bad1, bad2]]
                        t_col_min = min([t or 99 for t in t_cols])
                        t_fut = i #+ 1
                        if t_col_min <= t_fut:
                            print(f"AVOIDING TURN {self.id}, {t_fut=} {t_cols=}", file=sys.stderr, flush=True)
                        else:
                            print(f"NEW TARGET {nnxy.x, nnxy.y}", file=sys.stderr, flush=True)
                            self.target.x, self.target.y = nnxy.x, nnxy.y
                            break


        self.adjust_target()
        self.adjust_thrust()
        nxt_cp_dist = self.next_dist()
        nxt_cp_angle = self.angle_aim_to_target()
        print(f"{self.id} a{self.angle:03} {nxt_cp_dist=} {nxt_cp_angle=}", file=sys.stderr, flush=True)

        if self.id == 1111:
            found = False
            target = Pos(self.target.x, self.target.y)
            ncp = self.next_checkpoint()
            lowestlowest = 999999
            bestangle = 0
            for delta_rot in [0,-10,10,-15,15,-25,25,-45,45,-60,60-90,90][::-1]:
                self.target = rotate(self.pos, target, delta_rot)
                lowest = 999999
                for fut in self.sim_gen(10, delta_angle=delta_rot):
                    prox = fut.pos.dist(ncp)
                    if prox > lowest:
                        break
                    lowest = prox
                    if prox < lowestlowest:
                        lowestlowest = prox
                        bestangle = delta_rot
                    if prox  < 500:
                        found=True
                        break
                if found == True:
                    print(f"{delta_rot=} {prox=}", file=sys.stderr, flush=True)
                    break
            if not found:
                print(f"{bestangle=} {prox=}", file=sys.stderr, flush=True)
                self.target = rotate(self.pos, target, bestangle)
            # print(f"{self.target=}", file=sys.stderr, flush=True)

        # if self.closing() > 200 and self.next_dist() < 2000 and self.closing_other_pod() > 200:
        #     self.thrust = 'SHIELD'


        next_step = 1
        fut = self.simulate(next_step)
        for bad in [bad1, bad2]:
            futbad = bad.simulate(next_step)
            t_col = self.time_to_collision(bad)
            if t_col:
                print(f"collision? {self.id}->{bad.id} in {t_col:.2f}  {self.angle_aim_to(futbad.pos)=}", file=sys.stderr, flush=True)
            if t_col and t_col <= 2:
                badangle = self.angle_aim_to(futbad.pos)
                if abs(badangle) < 20 + abs(self.dev_extra):
                    if abs(bad.angle_aim_to(fut.pos)) < 30 + self.dev_extra:
                        print(f"frontal collision", file=sys.stderr, flush=True)
                        self.dev_extra += 20 * (-1 if badangle > 0 else 1)
                # else:
                #     self.thrust = 'SHIELD'
                print(f"{len(fut.vel - futbad.vel)=}", file=sys.stderr, flush=True)
                if len(fut.vel - futbad.vel) > 400:
                    self.thrust = 'SHIELD'

        fut_other = other.simulate(next_step)
        if fut.pos.dist(fut_other.pos) < DIST_FUT_SHIELD:
            if len(self.vel - other.vel) > 200: 
                self.thrust = 'SHIELD'

    def simulate(self, nbr_of_turns=1, thrust=None, delta_angle=0, target=None):
        if nbr_of_turns == 0:
            return self
        fut = Pod(self.id * 10)
        fut.nbr_cp = self.nbr_cp
        fut.next_id = self.next_id
        fut.prev_angle = self.prev_angle
        fut.pos = self.pos
        fut.vel = self.vel
        fut.angle = self.angle
        fut.thrust = MAX_THRUST if thrust is None else thrust
        fut.target = target or self.target
        fut.shield_no_thrust = self.shield_no_thrust
        fut.is_bumper = self.is_bumper
        fut.boost_avail = self.boost_avail

        # adjust
        original_target = fut.target
        fut.adjust_target()
        fut.adjust_thrust(is_sim=True)

        if fut.thrust == "BOOST":
            fut.thrust = 650
        if fut.thrust == "SHIELD":
            fut.thrust = 0

        ## sim
        # print(f"{fut.angle_aim_to_target()=}", file=sys.stderr, flush=True)
        desired_rot = fut.angle_aim_to_target()
        desired_rot += delta_angle
        desired_rot = (desired_rot + 180) % 360 -180

        rot = min(18, max(-18, desired_rot))
        fut.angle += rot
        fut.angle = (fut.angle + 180) % 360 -180
        fut.acc = rotate(Pos(0, 0), Pos(fut.thrust, 0), fut.angle)
        fut.pos += fut.vel + fut.acc * 0.5 *0
        fut.vel += fut.acc
        fut.vel *= 0.85

        fut.end_turn()

        if nbr_of_turns > 1:
            return fut.simulate(nbr_of_turns=nbr_of_turns - 1, thrust=thrust, delta_angle=delta_angle, target=target)
        # print(f"{fut.id} {nbr_of_turns} {fut}", file=sys.stderr, flush=True)
        return fut

    def sim_gen(self, nbr_of_turns=1, thrust=None, delta_angle=0, target=None):
        fut = self
        for i in range(nbr_of_turns):
            fut = fut.simulate(nbr_of_turns=1, thrust=thrust, delta_angle=delta_angle, target=target)
            yield fut



pod1 = Pod(1)
pod2 = Pod(2)
bad1 = Pod(-1)
bad2 = Pod(-2)

turn = 0

while True:
    pod1.update(input())
    pod2.update(input())
    bad1.update(input())
    bad2.update(input())

    # future1 = [pod.simulate(nbr_of_turns=1) for pod in [pod1, pod2, bad1, bad2]]

    # pod2.is_bumper = True
    # make one a bumper ?
    second = pod2 if pod1.nbr_cp-pod1.simulate(3).next_dist()*1e-6 > pod2.nbr_cp-pod2.simulate(3).next_dist()*1e-6 else pod1
    other = pod1 if second.id == pod2.id else pod2
    if turn == 50 or abs(pod1.nbr_cp - pod2.nbr_cp) >= 2:
        if not other.is_bumper:
            second.is_bumper = True
            print(f"{second.id} is BUMPER {second.is_bumper}", file=sys.stderr, flush=True)

    print(f"{pod1=}", file=sys.stderr, flush=True)
    print(f"{pod2=}", file=sys.stderr, flush=True)
    print(f"{bad1=}", file=sys.stderr, flush=True)
    print(f"{bad2=}", file=sys.stderr, flush=True)

    pod1.compute()
    pod2.compute()

    if turn == 0:
        pod1.thrust = pod1.try_to_boost()
    
    print(f"{pod1.target.x} {pod1.target.y} {pod1.thrust}")
    print(f"{pod2.target.x} {pod2.target.y} {pod2.thrust}")

    pod1.end_turn()
    pod2.end_turn()

    turn += 1


