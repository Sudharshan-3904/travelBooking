# Multi Agent Mesh Testing Notes

## Testing Config

| Criteria          | Value           |
| ----------------- | --------------- |
| Model             | llama3.2:latest |
| Difficulty Levels | All             |
| No. of Test Cases | 1000            |
| Sync Protocol     | Direct Message  |
| Temperature       | 0.2             |

## Memory system notes - Phase 1

### No Memory

#### Quantitative Scores

| Metric                | Score  |
| --------------------- | ------ |
| Average Score         | 76.25% |
| Budget Pass Rate      | 65%    |
| Destination Pass Rate | 77%    |
| Duration Pass Rate    | 97%    |
| Constraint Pass Rate  | 66%    |

#### Qualitative Notes

- Good performance for single stop destinations when budget has a good buffer.
- On no budget buffer, the system switches to alternatives without issue.
- Below budget the system does not inform about the insufficient budget or the inability to fulfill the request.

### Conversational Memory

#### Quantitative Scores

| Metric                | Score  |
| --------------------- | -----: |
| Average Score         | 78.43% |
| Budget Pass Rate      | 78.4%  |
| Destination Pass Rate | 66.8%  |
| Duration Pass Rate    | 96.8%  |
| Constraint Pass Rate  | 71.7%  |

#### Qualitative Notes

- Retains previously discussed preferences and constraints across the conversation, improving the handling of budget-related requirements.
- Performs well when the user progressively provides additional travel constraints instead of providing all requirements in a single request.
- Can occasionally over-rely on previously discussed information, resulting in incorrect destination selection when the current request changes the destination.
- Handles budget limitations better than the baseline and is more likely to select an alternative that remains within the available budget.
- Duration handling remains consistent with the baseline, indicating limited impact of conversational memory on temporal constraints.
- Constraint handling improves when constraints are introduced across multiple turns, but conflicting or updated constraints can still cause incorrect decisions.

### Summary Memory

#### Quantitative Scores

| Metric                | Score  |
| --------------------- | -----: |
| Average Score         | 79.28% |
| Budget Pass Rate      | 80.1%  |
| Destination Pass Rate | 69.4%  |
| Duration Pass Rate    | 97.3%  |
| Constraint Pass Rate  | 70.3%  |

#### Qualitative Notes

- Performs well when previous conversation information can be compressed into a concise representation of the user's requirements.
- Shows stronger budget handling compared to the baseline, particularly when multiple constraints affect the available spending limit.
- Summarized information is generally sufficient for continuing a travel plan without repeatedly requesting previously provided requirements.
- Can lose destination-specific details when the conversation contains multiple destinations or frequent changes in user preferences.
- Handles duration requirements consistently and shows little variation from the baseline.
- Constraint handling improves overall, although information lost during summarization can occasionally result in incorrect constraint interpretation.

### Agent Specific Memory

#### Quantitative Scores

| Metric                | Score  |
| --------------------- | -----: |
| Average Score         | 77.35% |
| Budget Pass Rate      | 76.9%  |
| Destination Pass Rate | 69.1%  |
| Duration Pass Rate    | 96.4%  |
| Constraint Pass Rate  | 67.0%  |

#### Qualitative Notes

- Performs well when information is relevant only to a specific specialist agent, reducing the need for unrelated agents to process the complete conversation history.
- Budget-related information is retained effectively by the budget agent and contributes to better budget compliance.
- Specialist agents can make better decisions when their memory contains information directly related to their assigned task.
- Destination selection can degrade when information required by multiple agents is distributed across separate memories.
- Cross-agent constraints are not always propagated correctly, resulting in inconsistent decisions between specialist agents.
- Duration handling remains stable but shows no significant improvement compared with the baseline.
- Overall constraint handling improves only slightly because shared information may be unavailable to the agent that needs it.

### Episodic Memory

#### Quantitative Scores

| Metric                | Score  |
| --------------------- | -----: |
| Average Score         | 79.25% |
| Budget Pass Rate      | 80.0%  |
| Destination Pass Rate | 69.0%  |
| Duration Pass Rate    | 97.0%  |
| Constraint Pass Rate  | 71.0%  |

#### Qualitative Notes

- Performs well when previous travel experiences or completed planning episodes are relevant to the current request.
- Can reuse information from similar previous planning situations, particularly when budget and constraint patterns are repeated.
- Shows better continuity across related planning tasks where previous decisions provide useful context for the current request.
- Can retrieve information from previous episodes that is no longer relevant, resulting in incorrect destination or preference selection.
- Performance remains dependent on correctly identifying which previous episode is relevant to the current request.
- Duration handling remains consistent with the other memory configurations and shows limited sensitivity to the memory architecture.
- Constraint handling benefits from previously encountered planning patterns, particularly when similar combinations of constraints appear across different requests.
