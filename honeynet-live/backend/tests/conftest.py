import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("JWT_SECRET", "test-secret-test-secret-test-secret")
os.environ.setdefault("ADMIN_PASSWORD", "testpass")
os.environ.setdefault("DATA_MODE", "demo")
os.environ.setdefault("AUTO_BLOCK_MODE", "disabled")
