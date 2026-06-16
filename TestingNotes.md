# Multi Agent Mesh Research

## Testing Config

| Criteria          | Value          |
| ----------------- | -------------- |
| Model             | Qwen2.5:1.5B   |
| Difficulty Levels | All            |
| # Cases           | 100            |
| Memory System     | No Memory      |
| Sync Protocol     | Direct Message |
| Temperature       | 0.2            |

## Baseline system notes - Phase 0

## Quantitative Scores

- Avg Score: 92.3%
- Budget Pass Rate: 60%

## Qualitative Notes

- Good performance for single stop destinations when budget has a good buffer.
- On no budget buffer, the system switches to alternatives without issue.
- Below budget the system does not inform about the insufficient budget or the inability to fulfill the request.