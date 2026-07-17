# Multi Agent Co-Pilot Backend Design

## Architecture

USER QUERY
     ↓
Planner Agent
     ↓
Designer Agent
     ↓
Coding Agent <--------------|
     ↓                      |
Test Runner Tool <----------|
     ↓                      |
Debugger Agent >------------|
     ↓
Critic Agent
     ↓
Final Executable Codebase

## Core Modules

1. Planner Agent

converts request into requirements:
- modules
- interactions between modules
- components

2. Designer Agent

- For the given plan, design the modules
- Create technical documents for the modules
- Idetify additionally required resources

3. Coding Agent

- Breaks down the module requirements into file, functions, calsses and other objects
- Creates and writes all the files
- Breaks the modules into files if required
- Creates directories if needed

4. Testing Agent

- 1. See if the created file compiles / has no errors
- 2. See if the file is logically correct
- 3. Writes tests to verify the functionality of the code based on design
- 4. Runs the tests
- 5. Produces a per file based testing report

5. Debugger Agent

- Given the error report, debugs all the files with errors to match the module design
- Call the coding agent to write / update code
- Verifies that all the files compile properly
- Call the testing agent to test the updated code

6. Critic Agnet

- Validates that all the written code matches the requirements given by the user
- Calls the flow from designer agent with the updates to the design
- Produces a detailed design document (Design Document.md)

## Shared Components

1. Tools layer

- - Memory Fetch (gets the latest information stored in one specific layer)
- - Memory Update (updates the latest information stored in one specific layer)
- - Web Search (for documnetation)
- - File search
- - File Read
- - File Write (Logs as a new file creation)
- - File update  (Logs the updates done to a specific file)
- - File Delete 
- - Directory Creation (Logs as a new directory creation)
- - Directory Deletion (Logs deletion of the directory with all the files and subdirectories that was deleted)
- - Directory Updation (Logs the renaming of the directory)
- - Code execution (For complete end to end execution)
- - Code Compilation (Compile all the files in the directory, return the list of all files that faile dto compile or threw error)

2. Multi-Layer Memory

- - Project Memory - All project related information, accessible to all the agent [Save locally and do not keep in memory, fetch once neeeded]
- - Module Memory - Design of the module, expected function and interaction, accessible to all the agent
- - Agent Memory - The memory specific to and agent and not shared

## General Details

- All agnets can talk to each other
- All agents are part of the same graph
- All agents produce some document at the end of execution for the given requirement
- Updates should be provided via the API on every update in the flow
- No need for docker files

## Expexted Outcomes

- The complete ready to execute codebase
- A readme file with the description, instruction for set up and execution
- A directory with all the final documentaitons from each agent
