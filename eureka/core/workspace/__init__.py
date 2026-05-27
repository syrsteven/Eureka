"""The workspace is the central hub for the Agent's on disk resources."""
from eureka.core.workspace.base import Workspace
from eureka.core.workspace.simple import SimpleWorkspace, WorkspaceSettings

__all__ = [
    "SimpleWorkspace",
    "Workspace",
    "WorkspaceSettings",
]
