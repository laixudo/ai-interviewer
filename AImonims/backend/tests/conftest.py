"""测试夹具。

所有测试都跑在临时库副本上，绝不碰 backend/interview.db。
"""

import os
import shutil
import sqlite3
import sys
import tempfile

import pytest

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

# 令牌密钥必须在 import main 之前就绪
os.environ.setdefault("APP_SECRET_KEY", "test-secret-key-for-pytest-only-0123456789abcdef")


def _seed(db_path):
    """建一个最小可用的库：两个用户 + 各自一场面试。"""
    sys.path.insert(0, BACKEND_DIR)
    from data.database import Database

    db = Database(db_path=db_path)
    alice = db.add_user("alice", "alice-pw-123", "alice@test.local")
    bob = db.add_user("bob", "bob-pw-123", "bob@test.local")
    root = db.add_user("root_admin", "root-pw-123", "root@test.local", role="admin")

    conn = sqlite3.connect(db_path)
    ids = {}
    for name, uid in (("alice", alice), ("bob", bob)):
        cur = conn.execute(
            "INSERT INTO interviews (user_id, position, round, job_type, phase, status) "
            "VALUES (?, 'Java工程师', '技术面', 'java_backend', 'ended', 'completed')",
            (uid,),
        )
        ids[name] = cur.lastrowid
    conn.commit()
    conn.close()
    return {"alice": alice, "bob": bob, "root_admin": root, "interviews": ids}


@pytest.fixture(scope="session")
def app_env():
    tmpdir = tempfile.mkdtemp(prefix="interview-tests-")
    db_path = os.path.join(tmpdir, "test.db")
    os.environ["INTERVIEW_DB_PATH"] = db_path
    seeded = _seed(db_path)

    import main  # noqa: E402  —— 必须在环境变量就绪后导入

    yield {"main": main, "db_path": db_path, "seed": seeded}
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture()
def client(app_env):
    from fastapi.testclient import TestClient

    return TestClient(app_env["main"].app)


def login(client, username, password):
    resp = client.post("/api/auth/login", json={"username": username, "password": password})
    data = resp.json()
    assert data.get("success") is True, "登录失败: %s" % data
    return {"Authorization": "Bearer %s" % data["token"]}, data


@pytest.fixture()
def alice_auth(client):
    headers, _ = login(client, "alice", "alice-pw-123")
    return headers


@pytest.fixture()
def admin_auth(client):
    headers, _ = login(client, "root_admin", "root-pw-123")
    return headers
