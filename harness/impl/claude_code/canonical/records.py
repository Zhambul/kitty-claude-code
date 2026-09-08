# Copyright (c) 2026 Zhambyl Yermagambet
"""Expose Claude Code foreign record models."""

from harness.impl.claude_code.canonical import (
    record_attachments as attachment_records,
    record_content_blocks as content_records,
    record_content_extra as content_extra_records,
    record_documents as document_records,
    record_facade_foundation as foundation_records,
    record_otel_base as otel_records,
)

# Keep tool, transcript, and usage records separate from shared content records.
# isort: split

from harness.impl.claude_code.canonical import (
    record_tool_response as tool_response_records,
    record_tool_response_base as tool_response_base_records,
    record_transcript_common as transcript_common_records,
    record_transcript_entries as transcript_entry_records,
    record_usage as usage_records,
    record_usage_base as usage_base_records,
)

FOREIGN = foundation_records.FOREIGN
OPEN_FOREIGN = foundation_records.OPEN_FOREIGN
ForeignMetadata = foundation_records.ForeignMetadata
PermissionRule = foundation_records.PermissionRule
PermissionUpdate = foundation_records.PermissionUpdate
ImageSource = foundation_records.ImageSource
TranscriptRecordHeader = foundation_records.TranscriptRecordHeader
ShellArguments = foundation_records.ShellArguments
QuestionOption = foundation_records.QuestionOption
Question = foundation_records.Question
QuestionAnswers = foundation_records.QuestionAnswers
ToolArguments = foundation_records.ToolArguments
TextBlock = content_records.TextBlock
DirectCaller = content_records.DirectCaller
ToolUseBlock = content_records.ToolUseBlock
InnerContentBlock = content_records.InnerContentBlock
ToolResultBlock = content_records.ToolResultBlock
ThinkingBlock = content_records.ThinkingBlock
ImageBlock = content_records.ImageBlock
MessageContentBlock = content_extra_records.MessageContentBlock
FallbackBlock = content_extra_records.FallbackBlock
UsageOutputTokensDetails = usage_base_records.UsageOutputTokensDetails
UsageServerToolUse = usage_base_records.UsageServerToolUse
UsageCacheCreation = usage_base_records.UsageCacheCreation
UsageIterationType = usage_base_records.UsageIterationType
UsageIteration = usage_base_records.UsageIteration
UsageServiceTier = usage_base_records.UsageServiceTier
UsageSpeed = usage_base_records.UsageSpeed
UsageInferenceGeo = usage_records.UsageInferenceGeo
MessageUsage = usage_records.MessageUsage
MessageObject = usage_records.MessageObject
TranscriptDocument = transcript_common_records.TranscriptDocument
PreservedCompactSegment = transcript_common_records.PreservedCompactSegment
PreservedCompactMessages = transcript_common_records.PreservedCompactMessages
CompactMetadata = transcript_common_records.CompactMetadata
HookSummaryInfo = transcript_common_records.HookSummaryInfo
Origin = transcript_common_records.Origin
TeammateIdleNotificationDocument = transcript_entry_records.TeammateIdleNotificationDocument
TeammateMessageBodyHeader = transcript_entry_records.TeammateMessageBodyHeader
UserRecord = transcript_entry_records.UserRecord
AssistantRecord = transcript_entry_records.AssistantRecord
SystemRecord = transcript_entry_records.SystemRecord
GoalStatusAttachment = attachment_records.GoalStatusAttachment
QueuedCommandAttachment = attachment_records.QueuedCommandAttachment
AttachmentHeader = attachment_records.AttachmentHeader
AttachmentRecord = attachment_records.AttachmentRecord
QueueOperationRecord = attachment_records.QueueOperationRecord
TitleRecord = attachment_records.TitleRecord
PatchHunk = tool_response_base_records.PatchHunk
ToolResponseBlocks = tool_response_base_records.ToolResponseBlocks
ToolResponseImageDimensions = tool_response_base_records.ToolResponseImageDimensions
ToolResponseFile = tool_response_base_records.ToolResponseFile
WebSearchLink = tool_response_base_records.WebSearchLink
WebSearchResultSet = tool_response_base_records.WebSearchResultSet
ToolResponse = tool_response_records.ToolResponse
ToolCallNative = tool_response_records.ToolCallNative
HookEffort = tool_response_records.HookEffort
HookPayload = tool_response_records.HookPayload
OTelAttributeValue = otel_records.OTelAttributeValue
OTelAttribute = otel_records.OTelAttribute
OTelDataPoint = otel_records.OTelDataPoint
OTelSum = otel_records.OTelSum
OTelMetric = otel_records.OTelMetric
OTelScopeMetrics = otel_records.OTelScopeMetrics
OTelResourceMetrics = otel_records.OTelResourceMetrics
OTelMetricsDocument = document_records.OTelMetricsDocument
LaunchSelectionDocument = document_records.LaunchSelectionDocument
AgentMetaFile = document_records.AgentMetaFile
TaskFile = document_records.TaskFile
TaskListDocument = document_records.TaskListDocument
TaskSnapshot = document_records.TaskSnapshot
