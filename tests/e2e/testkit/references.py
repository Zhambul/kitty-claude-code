# Copyright (c) 2026 Zhambyl Yermagambet
"""Named immutable references carried by one scenario."""

from __future__ import annotations

from api.application.models.files.upload_response import UploadResponse
from api.application.models.harnesses.harness_catalog_response import HarnessCatalogResponse
from api.application.models.harnesses.harness_description_response import HarnessDescriptionResponse
from api.application.models.insights.application_insights_response import ApplicationInsightsResponse
from api.application.models.resume.resumable_session_response import ResumableSessionResponse
from sdk.client import ActionReceipt, GlobalStreamUpdate, SessionRef
from tests.e2e.testkit.reference_attention import (
    BrowserActionRef as BrowserActionRef,
    BrowserSessionFormRef as BrowserSessionFormRef,
    PlanRef as PlanRef,
    QuestionRef as QuestionRef,
)
from tests.e2e.testkit.reference_continuity import (
    AccountSelectionRef as AccountSelectionRef,
    JourneyOrigin as JourneyOrigin,
    SessionContinuationRef as SessionContinuationRef,
    SessionJourneyRef as SessionJourneyRef,
    SessionSpec as SessionSpec,
    ShellRef as ShellRef,
    TurnRef as TurnRef,
)
from tests.e2e.testkit.reference_entries import (
    ActorMessageRef as ActorMessageRef,
    FileOperationRef as FileOperationRef,
    ReasoningTraceRef as ReasoningTraceRef,
    SearchRef as SearchRef,
    SkillRef as SkillRef,
    WebFetchRef as WebFetchRef,
    WorktreeChangeRef as WorktreeChangeRef,
)
from tests.e2e.testkit.reference_events import (
    ApplicationRestartRef as ApplicationRestartRef,
    CompactionRef as CompactionRef,
    FeedSnapshotRef as FeedSnapshotRef,
    SessionStreamUpdateRef as SessionStreamUpdateRef,
    StreamCheckpointRef as StreamCheckpointRef,
    TaskRef as TaskRef,
)
from tests.e2e.testkit.reference_work import (
    ActorRef as ActorRef,
    AssignmentRef as AssignmentRef,
    AttachmentBundleRef as AttachmentBundleRef,
    WorkerControlRef as WorkerControlRef,
    WorkerKind as WorkerKind,
    WorkerRef as WorkerRef,
    WorkRef as WorkRef,
)


class References[ReferenceT]:
    """Represent references."""

    def __init__(self, noun: str) -> None:
        """Initialize the object."""
        self.noun = noun
        self._references: dict[str, ReferenceT] = {}

    def bind(self, name: str, reference: ReferenceT) -> ReferenceT:
        """Store a reference under a new name.

        Returns:
            The supplied reference.

        Raises:
            AssertionError: If the name already has a reference.

        """
        if name in self._references:
            message = f"{self.noun} name {name!r} is already bound"
            raise AssertionError(message)
        self._references[name] = reference
        return reference

    def replace(self, name: str, reference: ReferenceT) -> ReferenceT:
        """Replace the reference for an existing name.

        Returns:
            The supplied reference.

        Raises:
            AssertionError: If the name has no reference.

        """
        if name not in self._references:
            message = f"unknown {self.noun} {name!r}; available names: {sorted(self._references)}"
            raise AssertionError(message)
        self._references[name] = reference
        return reference

    def get(self, name: str) -> ReferenceT:
        """Read the reference for a name.

        Returns:
            The reference stored under the supplied name.

        Raises:
            AssertionError: If the name has no reference.

        """
        try:
            return self._references[name]
        except KeyError as error:
            message = f"unknown {self.noun} {name!r}; available names: {sorted(self._references)}"
            raise AssertionError(message) from error

    def __getitem__(self, name: str) -> ReferenceT:
        """Return the reference for one required name.

        Returns:
            The reference for one required name.

        """
        return self.get(name)

    def all_references(self) -> tuple[ReferenceT, ...]:
        """Return all references.

        Returns:
            All references.

        """
        return tuple(self._references.values())


SessionSpecs = References[SessionSpec]
AccountSelections = References[AccountSelectionRef]
ApplicationRestarts = References[ApplicationRestartRef]
Sessions = References[SessionRef]
SessionContinuations = References[SessionContinuationRef]
SessionJourneys = References[SessionJourneyRef]
Turns = References[TurnRef]
Shells = References[ShellRef]
Actors = References[ActorRef]
Assignments = References[AssignmentRef]
Works = References[WorkRef]
WorkerControls = References[WorkerControlRef]
ActorMessages = References[ActorMessageRef]
FileOperations = References[FileOperationRef]
Searches = References[SearchRef]
WebFetches = References[WebFetchRef]
ReasoningTraces = References[ReasoningTraceRef]
WorktreeChanges = References[WorktreeChangeRef]
Skills = References[SkillRef]
Questions = References[QuestionRef]
Plans = References[PlanRef]
BrowserActions = References[BrowserActionRef]
BrowserSessionForms = References[BrowserSessionFormRef]
Tasks = References[TaskRef]
Compactions = References[CompactionRef]
FeedSnapshots = References[FeedSnapshotRef]
StreamCheckpoints = References[StreamCheckpointRef]
SessionStreamUpdates = References[SessionStreamUpdateRef]
GlobalStreamUpdates = References[GlobalStreamUpdate]
Controls = References[ActionReceipt]
HarnessLists = References[tuple[HarnessDescriptionResponse, ...]]
HarnessCatalogs = References[HarnessCatalogResponse]
InsightsSnapshots = References[ApplicationInsightsResponse]
ResumableLists = References[tuple[ResumableSessionResponse, ...]]
StagedAttachments = References[UploadResponse]
AttachmentBundles = References[AttachmentBundleRef]
