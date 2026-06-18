# Multi Agent Mesh Research

## Testing Config

| Criteria          | Value          |
| ----------------- | -------------- |
| Model             | llama3.2:3b    |
| Difficulty Levels | All            |
| # Cases           | 100            |
| Memory System     | No Memory      |
| Sync Protocol     | Direct Message |
| Temperature       | 0.2            |

## Baseline system notes - Phase 0

## Quantitative Scores

- Avg Score: 77.6%
- Budget Pass Rate: 65%
- Destination Pass Rate: 77%
- Duration Pass Rate: 97%
- Constraint Pass Rate: 66%

## Qualitative Notes

- Good performance for single stop destinations when budget has a good buffer.
- On no budget buffer, the system switches to alternatives without issue.
- Below budget the system does not inform about the insufficient budget or the inability to fulfill the request.