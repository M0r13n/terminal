"""
The server collects some metrics about user's and their progress.
Collected Metrics:
--------------------
- UUID
- Number of solved challenges
- Wrong submitted solutions
- Correct solutions
- Time spend solving the challenge (timespans greater than 10 minutes between submissions are excluded because the user is considered to be idle)
- User first seen
- User last seen
- GameMode which is either ControlGroup, Badge or Progressbar
--------------------
"""

import datetime
import logging
import re
import typing
from enum import Enum, IntEnum
from random import choice
from uuid import uuid4

from sqlalchemy import inspect
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import FlushError

from server.crud import CRUDMixin
from server.extensions import db

logger = logging.getLogger(__name__)


class GameModes(Enum):
    ControlGroup = "DEFAULT"
    BADGE = "BADGE"
    PROGRESSBAR = "PROGRESSBAR"


class MotivationFeedback(IntEnum):
    SD = 0
    D = 1
    ND = 2
    A = 3
    SA = 4

    @property
    def name(self):
        tbl = {
            0: "Strongly disagree",
            1: "Disagree",
            2: "Neither agree nor disagree",
            3: "Agree",
            4: "Strongly agree",
        }
        return tbl[self]


class BadgeConditions(Enum):
    SOLVED_FIRST_CHALLENGE = "SOLVED_FIRST_CHALLENGE"
    CHAIN_3_TOGETHER = "CHAIN_3_TOGETHER"
    WRONG_10_TIMES = "WRONG_10_TIMES"
    ALL_SOLVED = "ALL_SOLVED"
    SOLVED_12 = "SOLVED_12"

    def is_solved(self, user, cmd: str) -> bool:
        tbl = {
            'SOLVED_FIRST_CHALLENGE': user.correct_command_count > 0,
            'CHAIN_3_TOGETHER': len(re.split(r"[&;>|]", cmd)) >= 3,
            'WRONG_10_TIMES': user.wrong_command_count >= 10,
            'ALL_SOLVED': len(user.solved_challenges) == Challenge.query.count(),
            'SOLVED_12': "12_find_all_env_files_with_secrets" in map(lambda c: c.solved_challenge.identifier, user.solved_challenges)
        }
        return tbl.get(self.value)


badges_user_association_table = db.Table('badges_user_association_table',
                                         db.Column('user_id', db.String(255), db.ForeignKey('user.uuid')),
                                         db.Column('badge_id', db.Integer, db.ForeignKey('badge.id'))
                                         )


class SolvedChallenges(db.Model):
    __tablename__ = 'solved_challenges'
    user_id = db.Column(db.String(255), db.ForeignKey('user.uuid'), primary_key=True)
    challenge_id = db.Column(db.String(255), db.ForeignKey('challenge.identifier'), primary_key=True)
    time_solved = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    user = relationship("User", back_populates="solved_challenges")
    solved_challenge = relationship("Challenge", back_populates="users")


class User(db.Model, CRUDMixin):
    __tablename__ = "user"

    uuid = db.Column(db.String(255), primary_key=True)
    first_seen = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    mode = db.Column(db.Enum(GameModes), nullable=False)

    # demographics
    age = db.Column(db.String(255))
    gender = db.Column(db.String(255))
    english_skills = db.Column(db.String(255))
    bash_experience = db.Column(db.String(255))

    # Relations
    commands = relationship("SubmittedCommand", back_populates="user")
    badges = relationship(
        "Badge",
        secondary=badges_user_association_table,
        back_populates="users")

    solved_challenges = relationship("SolvedChallenges", back_populates="user")

    feedback = relationship("FinalFeedback", back_populates="user")

    def __repr__(self):
        return f"<User: {self.uuid}>"

    @property
    def correct_command_count(self):
        return SubmittedCommand.query.filter(SubmittedCommand.user_uuid == self.uuid, SubmittedCommand.solved_challenge == True).count()

    @property
    def wrong_command_count(self):
        return SubmittedCommand.query.filter(SubmittedCommand.user_uuid == self.uuid, SubmittedCommand.solved_challenge == False).count()

    @property
    def last_seen(self):
        try:
            return SubmittedCommand.query.filter(SubmittedCommand.user_uuid == self.uuid).order_by(SubmittedCommand.time_submitted.desc()).first().time_submitted
        except AttributeError:
            return self.first_seen

    @classmethod
    def create_user(cls):
        return cls.create(
            uuid=str(uuid4()),
            mode=choice(list(GameModes))
        )

    def add_new_badges(self, applicable_badges: typing.Set):
        new_badges = applicable_badges - set(self.badges)
        if new_badges:
            [self.badges.append(badge) for badge in new_badges]
            self.save()
            logger.debug(f"User earned new badges: {new_badges}")

    def to_dict(self):
        return dict(
            uuid=self.uuid,
            first_seen=self.first_seen,
            last_seen=self.last_seen,
            mode=self.mode.value
        )

    def add_solved_challenge(self, challenge):
        try:
            a = SolvedChallenges(challenge_id=challenge.identifier)
            self.solved_challenges.append(a)
            self.save()
        except FlushError:
            pass

    def add_command(self, command_string: str, challenge_id: str, solved: bool):
        SubmittedCommand.create(command_string=command_string, challenge_id=challenge_id, solved_challenge=solved, user=self)
        if solved:
            challenge = Challenge.query.get(challenge_id)
            self.add_solved_challenge(challenge)


class SubmittedCommand(db.Model, CRUDMixin):
    __tablename__ = "submitted_command"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time_submitted = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    command_string = db.Column(db.Text)
    challenge_id = db.Column(db.String(255))
    solved_challenge = db.Column(db.Boolean, default=False)

    # Relations
    user_uuid = db.Column(db.String(255), db.ForeignKey('user.uuid'))
    user = relationship("User", back_populates="commands")

    def __repr__(self):
        return f"<Submission for {self.challenge_id}>"


class Challenge(db.Model, CRUDMixin):
    """ Challenge model"""
    __tablename__ = "challenge"

    identifier = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)

    help = db.Column(db.Text, nullable=True)
    external_link = db.Column(db.String(255), nullable=True)

    # Relations
    users = relationship("SolvedChallenges", back_populates="solved_challenge")

    def __repr__(self):
        return self.name or ""

    def to_dict(self):
        return dict(
            identifier=self.identifier,
            name=self.name,
            description=self.description,
            help=self.help,
            external_link=self.external_link
        )

    @classmethod
    def json_list(cls):
        return dict(list(map(lambda x: (x.identifier, x.to_dict()), cls.query.all())))


class Badge(db.Model, CRUDMixin):
    """ Badges that can be earned """
    __tablename__ = "badge"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    src_filename = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    condition = db.Column(db.Enum(BadgeConditions))

    # Relations
    users = relationship(
        "User",
        secondary=badges_user_association_table,
        back_populates="badges")

    def __repr__(self):
        return self.name

    def to_dict(self) -> dict:
        return dict(
            id=self.id,
            name=self.name,
            src_filename=self.src_filename,
            description=self.description
        )

    @classmethod
    def active_badges(cls) -> typing.Iterable:
        return cls.query.filter(cls.condition != None).all()

    @classmethod
    def json_list(cls):
        return dict(list(map(lambda badge: (badge.name, badge.to_dict()), cls.query.all())))

    @classmethod
    def earned_through_action(cls, user: User, command: str) -> typing.Set:
        return {badge for badge in cls.active_badges() if badge.condition.is_solved(user, command)}


class FinalFeedback(db.Model, CRUDMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    motivation = db.Column(db.Enum(MotivationFeedback), nullable=False)

    user_uuid = db.Column(db.String(255), db.ForeignKey('user.uuid'))
    user = relationship("User", back_populates="feedback")


class CommandCache(db.Model, CRUDMixin):
    __tablename__ = "command_cache"

    hash = db.Column(db.String(255), primary_key=True)
    challenge_identifier = db.Column(db.String(64), primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

    cmd_correct = db.Column(db.Boolean, default=False, nullable=False)
    cmd_output = db.Column(db.Text)

    @classmethod
    def get_by_pks(cls, **kwargs):
        return cls.query.get(
            tuple(
                kwargs[key.name]
                for key in inspect(cls).primary_key
            )
        )
