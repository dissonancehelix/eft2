"""Deterministic EFT2 core-loop rule model.

This is a small simulation kernel for the already-playable core loop. It is
not a bot system, not reinforcement learning, and not a real-map runtime. The
model exists to exercise the same rule slice that `game/eft2/` currently owns:
automatic pickup, carrier slowdown, tackle/fumble, knockdown/recovery, retarget,
score, and reset.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import hypot
from typing import Any


BASE_SPEED = 350.0
CARRIER_SPEED = 262.5
CHARGE_THRESHOLD = 300.0
KNOCKDOWN_DURATION = 2.75
PICKUP_RADIUS = 58.0
TACKLE_RADIUS = 54.0
FUMBLE_HORIZONTAL_MULTIPLIER = 1.75
FUMBLE_VERTICAL_POP = 128.0
PREVIOUS_CARRIER_PICKUP_IMMUNITY = 1.0


class Team(str, Enum):
    red_rhinos = "red_rhinos"
    blue_bulls = "blue_bulls"


@dataclass(frozen=True)
class Vec2:
    x: float
    y: float

    def __add__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vec2":
        return Vec2(self.x * scalar, self.y * scalar)

    def length(self) -> float:
        return hypot(self.x, self.y)

    def normalized(self) -> "Vec2":
        length = self.length()
        if length <= 1e-6:
            return Vec2(0.0, 0.0)
        return Vec2(self.x / length, self.y / length)

    def distance(self, other: "Vec2") -> float:
        return (self - other).length()


@dataclass
class Player:
    name: str
    team: Team
    position: Vec2
    velocity: Vec2 = field(default_factory=lambda: Vec2(0.0, 0.0))
    is_carrier: bool = False
    knockdown_remaining: float = 0.0

    @property
    def is_knocked_down(self) -> bool:
        return self.knockdown_remaining > 0.0

    @property
    def speed(self) -> float:
        return self.velocity.length()

    @property
    def is_charging(self) -> bool:
        return not self.is_carrier and not self.is_knocked_down and self.speed >= CHARGE_THRESHOLD

    @property
    def can_pickup(self) -> bool:
        return not self.is_knocked_down


@dataclass
class Ball:
    position: Vec2
    velocity: Vec2 = field(default_factory=lambda: Vec2(0.0, 0.0))
    carrier: str | None = None
    blocked_player: str | None = None
    blocked_until: float = 0.0

    @property
    def is_loose(self) -> bool:
        return self.carrier is None


@dataclass
class TelemetryEvent:
    tick: int
    time_s: float
    event: str
    payload: dict[str, Any]


@dataclass
class CoreLoopResult:
    score: dict[str, int]
    events: list[TelemetryEvent]
    final_ball_owner: str | None
    final_ball_position: Vec2


class CoreLoopModel:
    """Scriptable deterministic model for the first EFT2 rule slice."""

    def __init__(self, tick_rate: float = 50.0) -> None:
        self.tick_rate = tick_rate
        self.dt = 1.0 / tick_rate
        self.tick = 0
        self.time_s = 0.0
        self.score = {Team.red_rhinos.value: 0, Team.blue_bulls.value: 0}
        self.players = {
            "red_0": Player("red_0", Team.red_rhinos, Vec2(-180.0, 0.0)),
            "blue_0": Player("blue_0", Team.blue_bulls, Vec2(420.0, 0.0)),
        }
        self.ball = Ball(Vec2(0.0, 0.0))
        self.events: list[TelemetryEvent] = []

    def emit(self, event: str, **payload: Any) -> None:
        self.events.append(TelemetryEvent(self.tick, round(self.time_s, 4), event, payload))

    def step(self) -> None:
        self.tick += 1
        self.time_s = self.tick * self.dt
        for player in self.players.values():
            if player.knockdown_remaining > 0.0:
                player.knockdown_remaining = max(0.0, player.knockdown_remaining - self.dt)
                if player.knockdown_remaining == 0.0:
                    self.emit("PlayerRecovered", player=player.name)
        if self.ball.carrier:
            self.ball.position = self.players[self.ball.carrier].position
        elif self.ball.velocity.length() > 0.0:
            self.ball.position = self.ball.position + self.ball.velocity * self.dt
            self.ball.velocity = self.ball.velocity * 0.94

    def move_toward(self, player_name: str, target: Vec2, seconds: float, speed: float | None = None) -> None:
        player = self.players[player_name]
        steps = max(1, int(seconds * self.tick_rate))
        for _ in range(steps):
            if player.is_knocked_down:
                player.velocity = Vec2(0.0, 0.0)
                self.step()
                continue
            target_speed = speed if speed is not None else (CARRIER_SPEED if player.is_carrier else BASE_SPEED)
            direction = (target - player.position).normalized()
            player.velocity = direction * target_speed
            player.position = player.position + player.velocity * self.dt
            self.step()
            self.try_pickup(player)

    def try_pickup(self, player: Player) -> bool:
        if not self.ball.is_loose or not player.can_pickup:
            return False
        if self.ball.blocked_player == player.name and self.time_s < self.ball.blocked_until:
            return False
        if player.position.distance(self.ball.position) > PICKUP_RADIUS:
            return False
        self.ball.carrier = player.name
        player.is_carrier = True
        self.ball.velocity = Vec2(0.0, 0.0)
        self.ball.blocked_player = None
        self.emit("PossessionTransfer", player=player.name, team=player.team.value)
        return True

    def tackle(self, attacker_name: str, target_name: str) -> bool:
        attacker = self.players[attacker_name]
        target = self.players[target_name]
        if attacker.team == target.team or not attacker.is_charging or target.is_knocked_down:
            return False
        if attacker.position.distance(target.position) > TACKLE_RADIUS:
            return False
        caused_fumble = target.is_carrier
        self.emit("TackleResolve", attacker=attacker.name, target=target.name, fumble=caused_fumble)
        if caused_fumble:
            self.fumble(target, attacker)
        target.is_carrier = False
        target.knockdown_remaining = KNOCKDOWN_DURATION
        self.emit("PlayerKnockdown", player=target.name, attacker=attacker.name)
        return True

    def fumble(self, previous_carrier: Player, attacker: Player) -> None:
        previous_carrier.is_carrier = False
        self.ball.carrier = None
        self.ball.position = previous_carrier.position
        source = previous_carrier.velocity if previous_carrier.velocity.length() > 1.0 else attacker.velocity
        self.ball.velocity = source * FUMBLE_HORIZONTAL_MULTIPLIER
        self.ball.blocked_player = previous_carrier.name
        self.ball.blocked_until = self.time_s + PREVIOUS_CARRIER_PICKUP_IMMUNITY
        self.emit(
            "BallLoose",
            previous_carrier=previous_carrier.name,
            attacker=attacker.name,
            horizontal_multiplier=FUMBLE_HORIZONTAL_MULTIPLIER,
            vertical_pop=FUMBLE_VERTICAL_POP,
        )

    def score_goal(self, carrier_name: str) -> None:
        carrier = self.players[carrier_name]
        if not carrier.is_carrier:
            return
        self.score[carrier.team.value] += 1
        self.emit("GoalScored", player=carrier.name, team=carrier.team.value, score=dict(self.score))
        self.reset_ball("goal_scored")

    def reset_ball(self, reason: str) -> None:
        for player in self.players.values():
            player.is_carrier = False
        self.ball = Ball(Vec2(0.0, 0.0))
        self.emit("BallReset", reason=reason)

    def run_scripted_core_loop(self) -> CoreLoopResult:
        self.move_toward("red_0", self.ball.position, 0.7)
        carrier = self.players["red_0"]
        self.move_toward("red_0", Vec2(310.0, 0.0), 1.1, CARRIER_SPEED)
        self.players["blue_0"].position = Vec2(carrier.position.x + TACKLE_RADIUS - 4.0, carrier.position.y)
        self.players["blue_0"].velocity = Vec2(-CHARGE_THRESHOLD, 0.0)
        self.tackle("blue_0", "red_0")
        for _ in range(int((KNOCKDOWN_DURATION + 0.1) * self.tick_rate)):
            self.players["blue_0"].velocity = Vec2(0.0, 0.0)
            self.step()
        self.players["blue_0"].position = self.ball.position
        self.try_pickup(self.players["blue_0"])
        self.move_toward("blue_0", Vec2(-720.0, 0.0), 1.0, CARRIER_SPEED)
        self.score_goal("blue_0")
        return CoreLoopResult(
            score=dict(self.score),
            events=list(self.events),
            final_ball_owner=self.ball.carrier,
            final_ball_position=self.ball.position,
        )


def result_to_dict(result: CoreLoopResult) -> dict[str, Any]:
    return {
        "score": result.score,
        "final_ball_owner": result.final_ball_owner,
        "final_ball_position": {"x": result.final_ball_position.x, "y": result.final_ball_position.y},
        "events": [
            {
                "tick": event.tick,
                "time_s": event.time_s,
                "event": event.event,
                "payload": event.payload,
            }
            for event in result.events
        ],
    }
