# Multi Agent Mesh Research

## Testing Config

| Criteria          | Value           |
| ----------------- | --------------- |
| Model             | llama3.2:latest |
| Difficulty Levels | All             |
| No. of Test Cases | 1000            |
| Memory System     | No Memory       |
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
