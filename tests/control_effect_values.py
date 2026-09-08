# Copyright (c) 2026 Zhambyl Yermagambet
"""Shared values for confirmed control effect tests."""

from domain import ids as domain_ids

SHELL_ENTRY_TIME = 2.0
ASSIGNMENT_ENTRY_TIME = 3.0
TEST_SESSION_ID_TEXT = "session-one"
TEST_SESSION_ID = domain_ids.SessionId(TEST_SESSION_ID_TEXT)
TEST_ACTOR_ID_TEXT = "actor-one"
TEST_ACTOR_ID = domain_ids.ActorId(TEST_ACTOR_ID_TEXT)
TEST_WORKING_DIRECTORY = "/work"
TEST_REQUEST_ID_TEXT = "request-one"
TEST_REQUEST_ID = domain_ids.RequestId(TEST_REQUEST_ID_TEXT)
TEST_TURN_ID_TEXT = "turn-one"
TEST_TURN_ID = domain_ids.TurnId(TEST_TURN_ID_TEXT)
TEST_CHILD_ACTOR_ID_TEXT = "child-one"
TEST_LEAD_ACTOR_ID_TEXT = "session-one:lead"
ROLLOUT_SOURCE_NAME = "rollout.jsonl"
NEXT_PROMPT = "do this next"
