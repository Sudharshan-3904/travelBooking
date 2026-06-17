# TravelNet: A Peer-to-Peer Multi-Agent Travel Booking Research Platform

## Overview

TravelNet is a research-focused multi-agent system designed to investigate how autonomous AI agents collaborate to solve complex travel planning and booking tasks in a decentralized environment.

Unlike traditional multi-agent architectures that rely on a central orchestrator, TravelNet explores a peer-to-peer communication model where agents directly interact with one another to exchange information, negotiate decisions, and collectively construct travel plans.

The project uses a travel booking environment as a controlled experimental domain while investigating three major research areas:

1. Memory Systems in Multi-Agent Environments
2. Adaptive Agent Orchestration
3. Multi-Agent Synchronization

The platform is intended for experimentation, benchmarking, academic research, and portfolio development rather than production deployment.

Testing Dataset: ["Travel Planning Benchmark dataset"](https://huggingface.co/datasets/osunlp/TravelPlanner)

---

# Research Objectives

The primary goal is to understand how architectural decisions influence:

- Task completion quality
- Booking accuracy
- Personalization
- System latency
- Resource utilization
- Agent coordination efficiency
- Conflict resolution effectiveness
- Scalability of decentralized agent systems

The project progressively evolves from a simple baseline architecture to a highly autonomous distributed agent network.

---

# Technology Stack

## Core Frameworks

- Python
- LangChain
- LangGraph
- MLflow

## Memory Systems

- ChromaDB
- FAISS (CPU)

## Messaging & Synchronization

### Phase 0 – Direct Communication

- Python AsyncIO
- Queue
- Threading
- Multiprocessing

### Chapter 3 Experiments

- AsyncIO Event Bus
- Local Publish-Subscribe Framework
- Shared State Manager
- SQLite Event Store
- File-Based Event Log
- Custom Message Broker (Research Implementation)

## Evaluation

- MLflow Tracking
- Pandas
- NumPy
- Matplotlib

---

# System Architecture

## Domain

Travel Planning and Booking

Supported Planning Components:

- Flights
- Hotels
- Local Transportation
- Activity Planning
- Budget Management
- Package Optimization

---

## Agents

### Planner Agent

Responsible for:

- Goal decomposition
- Requirement extraction
- Task delegation
- Final itinerary generation

---

### Flight Specialist Agent

Responsible for:

- Flight search
- Route optimization
- Airline selection
- Travel constraints

---

### Hotel Specialist Agent

Responsible for:

- Accommodation selection
- Location analysis
- Hotel recommendation

---

### Budget Agent

Responsible for:

- Budget allocation
- Cost tracking
- Financial feasibility analysis

---

### Negotiation Agent

Responsible for:

- Conflict resolution
- Alternative recommendation generation
- Trade-off optimization

---

# Project Development Roadmap

---

# Phase 0: Baseline System

## Objective

Create a minimal decentralized travel-planning system that serves as the benchmark for all future experiments.

---

## Architecture

Static communication flow.

```text
Planner
 ├── Flight Agent
 ├── Hotel Agent
 ├── Budget Agent
 └── Negotiation Agent
```

---

## Features

### Direct Agent Communication

Agents communicate directly without shared memory.

### Stateless Execution

Every request is processed independently.

### Fixed Routing

All agents participate in every task.

### MLflow Experiment Tracking

Track:

- Latency
- Token usage
- Agent calls
- Task completion

---

## Deliverables

- Working travel planner
- Benchmark dataset
- Baseline metrics dashboard

## Getting Started

Run the Phase 0 baseline system with:

```bash
python phase0_baseline.py --origin "Seattle" --destination "San Francisco" --departure 2026-09-15 --return 2026-09-19 --travelers 1 --budget "$1500"
```

If `mlflow` is installed, the run will also log baseline metrics to the default MLflow tracking store.

---

# Chapter 1: Memory Systems

## Research Question

How does memory influence decision quality, personalization, efficiency, and collaboration in decentralized agent systems?

---

# Stage 1.1 No Memory

## Goal

Establish a baseline.

### Characteristics

- Stateless agents
- No historical information retained
- Every interaction processed independently

### Metrics

- Accuracy
- Cost
- Latency

---

# Stage 1.2 Conversation Memory

## Goal

Evaluate the impact of conversational history.

### Characteristics

Store:

- Previous messages
- Context windows
- User interactions

### Experiments

- Last 5 messages
- Last 10 messages
- Last 20 messages

### Evaluation

- Context retention
- Response quality
- Token consumption

---

# Stage 1.3 Summary Memory

## Goal

Reduce memory size while preserving context.

### Characteristics

Store:

- Compressed conversation summaries
- Key user preferences

### Evaluation

- Token reduction
- Accuracy retention

---

# Stage 1.4 Agent-Specific Memory

## Goal

Study localized intelligence.

### Characteristics

Each agent maintains its own memory.

Examples:

Flight Agent:

- Preferred airlines
- Flight patterns

Hotel Agent:

- Accommodation preferences

### Evaluation

- Memory specialization
- Agent autonomy

---

# Stage 1.5 Shared Memory

## Goal

Enable collaborative intelligence.

### Characteristics

All agents access a common memory repository.

### Evaluation

- Knowledge reuse
- Coordination efficiency

---

# Stage 1.6 Hybrid Memory

## Goal

Combine strengths of all memory systems.

### Architecture

```text
Agent Memory
     +
Shared Memory
     +
Episodic Memory
     +
Semantic Memory
```

### Evaluation

- Overall performance
- Resource consumption
- Scalability

---

# Chapter 1 Deliverables

- Memory Benchmark Suite
- Memory Performance Report
- Memory Impact Visualization Dashboard

---

# Chapter 2: Adaptive Agent Orchestration

## Research Question

How should decentralized agents decide who performs work and when?

---

# Stage 2.1 Static Routing

## Goal

Create orchestration baseline.

### Characteristics

Fixed communication paths.

Every request activates every agent.

---

# Stage 2.2 Conditional Routing

## Goal

Reduce unnecessary computation.

### Characteristics

Agent activation based on task requirements.

Example:

Hotel-only request:

```text
Planner → Hotel Agent
```

---

# Stage 2.3 Confidence-Based Routing

## Goal

Enable self-awareness.

### Characteristics

Agents report confidence scores.

Low confidence triggers consultation.

### Evaluation

- Error reduction
- Collaboration frequency

---

# Stage 2.4 Skill-Based Routing

## Goal

Match tasks to specialists.

### Characteristics

Agents advertise capabilities.

Tasks dynamically routed to best specialist.

---

# Stage 2.5 Auction-Based Routing

## Goal

Explore market-driven coordination.

### Characteristics

Agents bid for tasks.

Selection based on:

- Confidence
- Cost
- Expertise

### Evaluation

- Routing efficiency
- Agent utilization

---

# Stage 2.6 Reputation-Based Routing

## Goal

Use historical performance.

### Characteristics

Agents accumulate reputation scores.

Routing decisions influenced by:

- Accuracy
- Reliability
- Success rate

---

# Stage 2.7 Reinforcement Learning Routing

## Goal

Learn optimal orchestration policies.

### Characteristics

Routing evolves through rewards.

Optimization targets:

- Accuracy
- Latency
- Cost

---

# Stage 2.8 Emergent Routing

## Goal

Remove centralized planning entirely.

### Characteristics

Agents decide autonomously:

- Who should act next
- Who should receive information

### Significance

Represents a fully decentralized peer-to-peer network.

---

# Chapter 2 Deliverables

- Routing Benchmark Framework
- Orchestration Performance Report
- Routing Visualization Dashboard

---

# Chapter 3: Multi-Agent Synchronization

## Research Question

How do decentralized agents maintain consistent understanding and coordination?

---

# Stage 3.1 Direct Message Passing

## Goal

Establish synchronization baseline.

### Characteristics

Agents exchange messages directly.

No shared state.

---

# Stage 3.2 Shared Blackboard

## Goal

Enable collaborative state management.

### Characteristics

Shared workspace accessible by all agents.

### Evaluation

- Read frequency
- Write frequency
- State consistency

---

# Stage 3.3 Event-Driven Synchronization

## Goal

Reduce coupling between agents.

### Characteristics

Agents react to events.

Examples:

- FlightSelected
- BudgetExceeded
- HotelChanged

---

# Stage 3.4 Publish-Subscribe Architecture

## Goal

Investigate scalable communication.

### Technologies

- Redis
- Kafka
- NATS

### Evaluation

- Throughput
- Scalability
- Message delivery reliability

---

# Stage 3.5 State Versioning

## Goal

Prevent stale information usage.

### Characteristics

Every update receives a version identifier.

### Evaluation

- Conflict detection rate
- Synchronization latency

---

# Stage 3.6 Distributed Memory Synchronization

## Goal

Synchronize independently maintained memories.

### Characteristics

Each agent maintains local memory.

Synchronization strategies:

- Strong Consistency
- Eventual Consistency

---

# Chapter 3 Deliverables

- Synchronization Benchmark Suite
- Conflict Analysis Report
- Distributed Coordination Dashboard

---

# Evaluation Framework

## Functional Metrics

- Booking Accuracy
- Itinerary Quality
- Budget Adherence
- Personalization Score

---

## Performance Metrics

- Latency
- Token Usage
- Memory Consumption
- Agent Utilization

---

## Coordination Metrics

- Agent Collaboration Frequency
- Routing Efficiency
- Conflict Rate
- Consensus Time

---

## Research Metrics

- Memory Impact
- Routing Impact
- Synchronization Impact
- Combined System Performance

---

# MLflow Experiment Structure

Example:

```text
Experiment:
Memory = Hybrid

Routing = Auction-Based

Synchronization = Event-Driven
```

Tracked Metrics:

```text
Accuracy
Latency
Token Cost
Agent Calls
Memory Hits
Conflict Count
Consensus Time
Task Completion Rate
```

---

# Future Research Directions

## Chapter 4

Fully Distributed Peer-to-Peer Agent Networks

Topics:

- Agent discovery
- Dynamic topology formation
- Decentralized registries

---

## Chapter 5

Self-Evolving Agent Societies

Topics:

- Agent creation
- Agent retirement
- Capability evolution
- Multi-agent self-optimization

---

# Expected Outcomes

By the completion of this project, TravelNet will provide a comprehensive experimental platform for studying:

- Memory architectures in multi-agent systems
- Adaptive orchestration strategies
- Distributed synchronization techniques
- Emergent behaviors in autonomous agent networks

The resulting framework can serve as both a research testbed and a portfolio project demonstrating advanced expertise in LangChain, LangGraph, MLflow, distributed systems, and AI agent engineering.
