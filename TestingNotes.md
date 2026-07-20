# Multi Agent Mesh Research

## Testing Config

| Criteria          | Value           |
| ----------------- | --------------- |
| Model             | llama3.2:latest |
| Difficulty Levels | All             |
| No. of Test Cases | 1000            |
| Sync Protocol     | Direct Message  |
| Temperature       | 0.2             |

## Baseline system notes - Phase 0

## Quantitative Scores

| Metric                | Score |
| --------------------- | ----- |
| Average Score         | 78%   |
| Budget Pass Rate      | 65%   |
| Destination Pass Rate | 77%   |
| Duration Pass Rate    | 97%   |
| Constraint Pass Rate  | 66%   |

## Qualitative Notes

- Good performance for single stop destinations when budget has a good buffer.
- On no budget buffer, the system switches to alternatives without issue.
- Below budget the system does not inform about the insufficient budget or the inability to fulfill the request.

## Memory system notes - Phase 1

### Quantitative Scores - Conversational Memory

| Metric                | Score |
| --------------------- | ----- |
| Average Score         | 81%   |
| Budget Pass Rate      | 78.4% |
| Destination Pass Rate | 66.8% |
| Duration Pass Rate    | 96.8% |
| Constraint Pass Rate  | 71.7% |

## Qualitative Notes

-

### Quantitative Scores - Summary Memory

| Metric                | Score |
| --------------------- | ----- |
| Average Score         | 82.2% |
| Budget Pass Rate      | 80.1% |
| Destination Pass Rate | 69.4% |
| Duration Pass Rate    | 97.3% |
| Constraint Pass Rate  | 70.3% |

## Qualitative Notes

-

### Quantitative Scores - Agent Specific Memory

| Metric                | Score |
| --------------------- | ----- |
| Average Score         | 80.9% |
| Budget Pass Rate      | 76.9% |
| Destination Pass Rate | 69.1% |
| Duration Pass Rate    | 96.4% |
| Constraint Pass Rate  | 67.0% |

## Qualitative Notes

-

### Quantitative Scores

| Metric                | Score |
| --------------------- | ----- |
| Average Score         | --%   |
| Budget Pass Rate      | --%   |
| Destination Pass Rate | --%   |
| Duration Pass Rate    | --%   |
| Constraint Pass Rate  | --%   |

## Qualitative Notes

-
